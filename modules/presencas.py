"""
MÓDULO PRESENÇAS - FINAX OS
Sistema de gestão escolar com Supabase Cloud

Funcionalidade:
- Registo de entrada de alunos via QR Code
- Validação de aluno e escola
- Geração de relatório diário de presenças
"""

import sys
import os
import uuid
from datetime import datetime

# Adiciona a pasta raiz ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================
# IMPORTAÇÕES DOS MÓDULOS INTERNOS
# ============================================
from modules.database_config import db_config
from utils.interface import Interface

# ============================================
# IMPORTAÇÕES DE TERCEIROS
# ============================================
from tabulate import tabulate

# ============================================
# CONSTANTES
# ============================================

# Status de presença
STATUS_PRESENTE = "Presente"
STATUS_ACESSO_NEGADO = "Acesso Negado"
STATUS_ERRO = "Erro"


# ============================================
# CLASSE PRINCIPAL DE CONTROLO DE PRESENÇA
# ============================================

class ControloPresenca:
    """
    Classe responsável pelo controlo de presença dos alunos via QR Code.
    
    Funcionalidades:
    - Registo de entrada com validação de aluno e escola
    - Geração de relatório diário de presenças
    - Simulação de som de BIP
    """
    
    def __init__(self):
        """Inicializa o módulo com conexão ao banco de dados"""
        self.supabase = db_config.get_client()
        self.interface = Interface()
    
    # ============================================
    # 1. FUNÇÃO DE REGISTO DE ENTRADA
    # ============================================
    
    def registar_entrada(self, qr_data, escola_id):
        """
        Regista a entrada de um aluno via QR Code.
        
        Args:
            qr_data (str): Username lido do QR Code
            escola_id (str): ID da escola do administrador
        
        Returns:
            dict or None: Dados da presença registada ou None se erro
        """
        try:
            # ============================================
            # 1.1 VALIDAR QR DATA
            # ============================================
            if not qr_data or not qr_data.strip():
                self.interface.exibir_mensagem(
                    "QR Code inválido!",
                    tipo="erro"
                )
                return None
            
            qr_limpo = qr_data.strip()
            
            # ============================================
            # 1.2 BUSCAR ALUNO NA TABELA USUARIOS
            # ============================================
            self.interface.mostrar_processando("Validando QR Code...")
            
            resultado = self.supabase.table('usuarios')\
                .select('id, nome, escola_id, nivel')\
                .eq('username', qr_limpo)\
                .execute()
            
            # Verificar se aluno existe
            if not resultado.data or len(resultado.data) == 0:
                self._simular_som(False)
                self.interface.exibir_mensagem(
                    f"❌ ACESSO NEGADO: Utilizador '{qr_limpo}' não encontrado.",
                    tipo="erro"
                )
                return None
            
            aluno = resultado.data[0]
            
            # ============================================
            # 1.3 VERIFICAR SE É ESTUDANTE
            # ============================================
            if aluno.get('nivel') != 'Estudante':
                self._simular_som(False)
                self.interface.exibir_mensagem(
                    f"❌ ACESSO NEGADO: Apenas estudantes podem registar presença.",
                    tipo="erro"
                )
                return None
            
            # ============================================
            # 1.4 VERIFICAR SE PERTENCE À ESCOLA
            # ============================================
            if aluno.get('escola_id') != escola_id:
                self._simular_som(False)
                self.interface.exibir_mensagem(
                    f"❌ ACESSO NEGADO: O aluno {aluno['nome']} não pertence a esta escola.",
                    tipo="erro"
                )
                return None
            
            # ============================================
            # 1.5 VERIFICAR SE JÁ REGISTOU HOJE
            # ============================================
            data_hoje = datetime.now().strftime("%Y-%m-%d")
            
            verificar = self.supabase.table('presencas')\
                .select('id')\
                .eq('aluno_id', aluno['id'])\
                .eq('data', data_hoje)\
                .execute()
            
            if verificar.data:
                self.interface.exibir_mensagem(
                    f"⚠️ Aluno {aluno['nome']} já registou entrada hoje!",
                    tipo="info"
                )
                return None
            
            # ============================================
            # 1.6 REGISTAR PRESENÇA
            # ============================================
            agora = datetime.now()
            presenca_id = str(uuid.uuid4())
            
            dados_presenca = {
                "id": presenca_id,
                "aluno_id": aluno['id'],
                "nome_aluno": aluno['nome'],
                "escola_id": escola_id,
                "data": agora.strftime("%Y-%m-%d"),
                "hora_entrada": agora.strftime("%H:%M:%S"),
                "status": STATUS_PRESENTE
            }
            
            # Inserir na tabela presencas
            self.supabase.table('presencas').insert(dados_presenca).execute()
            
            # ============================================
            # 1.7 EXIBIR CONFIRMAÇÃO
            # ============================================
            self._simular_som(True)
            
            print("\n" + self.interface.cores.VERDE + self.interface.cores.NEGRITO)
            print("╔════════════════════════════════════════════════════════════╗")
            print("║  🔔 * BIP! ENTRADA REGISTADA! *  🔔")
            print("╚════════════════════════════════════════════════════════════╝")
            print(self.interface.cores.RESET)
            
            self.interface.mostrar_sucesso(f"✅ Aluno: {aluno['nome']}")
            print(f"   🕐 Hora: {agora.strftime('%H:%M:%S')}")
            print(f"   📅 Data: {agora.strftime('%d/%m/%Y')}")
            print(f"   📍 Status: {self.interface.cores.VERDE}PRESENTE{self.interface.cores.RESET}")
            
            return dados_presenca
            
        except Exception as e:
            self.interface.exibir_mensagem(
                f"Erro ao registar presença: {str(e)}",
                tipo="erro"
            )
            return None
    
    # ============================================
    # 2. FUNÇÃO DE SIMULAÇÃO DE SOM
    # ============================================
    
    def _simular_som(self, sucesso=True):
        """
        Simula um som de BIP (apenas visual no terminal).
        
        Args:
            sucesso (bool): True para som de sucesso, False para negação
        """
        if sucesso:
            print(f"\n{self.interface.cores.VERDE}🔊 * BIP! *{self.interface.cores.RESET}")
        else:
            print(f"\n{self.interface.cores.VERMELHO}🔊 * BIP! ACESSO NEGADO *{self.interface.cores.RESET}")
    
    # ============================================
    # 3. GERAR RELATÓRIO DIÁRIO
    # ============================================
    
    def gerar_relatorio_diario(self, escola_id):
        """
        Gera relatório de todos os alunos que entraram hoje.
        
        Args:
            escola_id (str): ID da escola
        
        Returns:
            list: Lista de presenças do dia
        """
        self.interface.limpar_tela()
        self.interface.mostrar_titulo("📋 RELATÓRIO DIÁRIO DE PRESENÇAS")
        
        try:
            data_hoje = datetime.now().strftime("%Y-%m-%d")
            data_exibicao = datetime.now().strftime("%d/%m/%Y")
            
            print(f"{self.interface.cores.CIANO}Data: {data_exibicao}{self.interface.cores.RESET}")
            print()
            
            # Buscar presenças do dia
            presencas = self.supabase.table('presencas')\
                .select('nome_aluno, hora_entrada, status')\
                .eq('escola_id', escola_id)\
                .eq('data', data_hoje)\
                .order('hora_entrada', asc=True)\
                .execute()
            
            if not presencas.data:
                self.interface.exibir_mensagem(
                    "Nenhuma presença registada hoje.",
                    tipo="info"
                )
                return []
            
            # Preparar dados para a tabela
            dados_tabela = []
            for p in presencas.data:
                # Cor para o status
                if p['status'] == STATUS_PRESENTE:
                    status_cor = self.interface.cores.VERDE
                else:
                    status_cor = self.interface.cores.VERMELHO
                
                dados_tabela.append([
                    p['nome_aluno'],
                    p['hora_entrada'],
                    f"{status_cor}{p['status']}{self.interface.cores.RESET}"
                ])
            
            # Exibir tabela
            tabela = tabulate(
                dados_tabela,
                headers=["ALUNO", "HORA DE ENTRADA", "STATUS"],
                tablefmt="grid"
            )
            print(tabela)
            
            # Estatísticas
            total = len(presencas.data)
            print(f"\n{self.interface.cores.AZUL}{'═'*60}{self.interface.cores.RESET}")
            print(f"📊 Total de presenças hoje: {self.interface.cores.VERDE}{total}{self.interface.cores.RESET}")
            
            return presencas.data
            
        except Exception as e:
            self.interface.exibir_mensagem(
                f"Erro ao gerar relatório: {e}",
                tipo="erro"
            )
            return []
    
    # ============================================
    # 4. RELATÓRIO POR PERÍODO
    # ============================================
    
    def gerar_relatorio_periodo(self, escola_id, data_inicio, data_fim):
        """
        Gera relatório de presenças num período específico.
        
        Args:
            escola_id (str): ID da escola
            data_inicio (str): Data inicial (YYYY-MM-DD)
            data_fim (str): Data final (YYYY-MM-DD)
        """
        self.interface.limpar_tela()
        self.interface.mostrar_titulo(f"📋 RELATÓRIO DE PRESENÇAS")
        print(f"{self.interface.cores.CIANO}Período: {data_inicio} a {data_fim}{self.interface.cores.RESET}")
        print()
        
        try:
            # Buscar presenças no período
            presencas = self.supabase.table('presencas')\
                .select('nome_aluno, data, hora_entrada, status')\
                .eq('escola_id', escola_id)\
                .gte('data', data_inicio)\
                .lte('data', data_fim)\
                .order('data', asc=True)\
                .order('hora_entrada', asc=True)\
                .execute()
            
            if not presencas.data:
                self.interface.exibir_mensagem(
                    "Nenhuma presença registada no período.",
                    tipo="info"
                )
                return
            
            # Preparar dados para a tabela
            dados_tabela = []
            for p in presencas.data:
                # Formatar data para exibição
                data_obj = datetime.strptime(p['data'], "%Y-%m-%d")
                data_formatada = data_obj.strftime("%d/%m/%Y")
                
                # Cor para o status
                if p['status'] == STATUS_PRESENTE:
                    status_cor = self.interface.cores.VERDE
                else:
                    status_cor = self.interface.cores.VERMELHO
                
                dados_tabela.append([
                    p['nome_aluno'],
                    data_formatada,
                    p['hora_entrada'],
                    f"{status_cor}{p['status']}{self.interface.cores.RESET}"
                ])
            
            # Exibir tabela
            tabela = tabulate(
                dados_tabela,
                headers=["ALUNO", "DATA", "HORA", "STATUS"],
                tablefmt="grid"
            )
            print(tabela)
            
            # Estatísticas
            total = len(presencas.data)
            print(f"\n{self.interface.cores.AZUL}{'═'*60}{self.interface.cores.RESET}")
            print(f"📊 Total de presenças no período: {self.interface.cores.VERDE}{total}{self.interface.cores.RESET}")
            
        except Exception as e:
            self.interface.exibir_mensagem(
                f"Erro ao gerar relatório: {e}",
                tipo="erro"
            )
    
    # ============================================
    # 5. FUNÇÃO DE LEITURA DE QR CODE (SIMULAÇÃO)
    # ============================================
    
    def ler_qr_code_simulado(self):
        """
        Simula a leitura de um QR Code (para testes).
        
        Returns:
            str: Username digitado pelo utilizador
        """
        print(f"\n{self.interface.cores.CIANO}📷 SIMULAÇÃO DE LEITOR QR CODE{self.interface.cores.RESET}")
        print("   (Para teste, digite o username do aluno)")
        print("   Digite 'cancelar' para voltar")
        
        qr_data = self.interface.input_com_validação(
            "\nCódigo QR: ",
            obrigatorio=False
        )
        
        if qr_data and qr_data.lower() == 'cancelar':
            return None
        
        return qr_data
    
    # ============================================
    # 6. MENU PRINCIPAL
    # ============================================
    
    def menu(self, escola_id):
        """
        Menu interativo do módulo de presenças.
        
        Args:
            escola_id (str): ID da escola do administrador logado
        """
        while True:
            self.interface.limpar_tela()
            self.interface.mostrar_titulo("📍 FINAX PRESENÇA - CONTROLO DE ENTRADA")
            
            print("1 - 📷 Registrar Entrada (QR Code)")
            print("2 - 📋 Relatório Diário de Presenças")
            print("3 - 📅 Relatório por Período")
            print("4 - ⬅️ Voltar ao Menu Principal")
            
            opcao = self.interface.input_com_validação(
                "\nEscolha uma opção",
                obrigatorio=True,
                tipo="numero"
            )
            
            if opcao == "1":
                # Ler QR Code (simulado)
                qr_data = self.ler_qr_code_simulado()
                if qr_data:
                    self.registar_entrada(qr_data, escola_id)
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)
                
            elif opcao == "2":
                self.gerar_relatorio_diario(escola_id)
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)
                
            elif opcao == "3":
                print(f"\n{self.interface.cores.CIANO}Formato de data: YYYY-MM-DD (ex: 2026-03-30){self.interface.cores.RESET}")
                data_inicio = self.interface.input_com_validação(
                    "Data início: ",
                    obrigatorio=True
                )
                data_fim = self.interface.input_com_validação(
                    "Data fim: ",
                    obrigatorio=True
                )
                self.gerar_relatorio_periodo(escola_id, data_inicio, data_fim)
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)
                
            elif opcao == "4":
                break
                
            else:
                self.interface.exibir_mensagem("Opção inválida!", tipo="erro")
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)


# ============================================
# FUNÇÃO DE INTEGRAÇÃO PARA O MAIN
# ============================================

def iniciar_presenca(escola_id):
    """
    Função de integração para ser chamada pelo main.py
    
    Args:
        escola_id (str): ID da escola do administrador logado
    """
    presenca = ControloPresenca()
    presenca.menu(escola_id)


# ============================================
# TESTE DO MÓDULO
# ============================================

if __name__ == "__main__":
    print("🧪 Teste do módulo Controlo de Presença")
    print("⚠️ Para testar, execute o main.py com um administrador logado.")
    print("   Ou utilize: presenca = ControloPresenca()")
    print("   presenca.registar_entrada('joao.silva', 'ESC_001')")