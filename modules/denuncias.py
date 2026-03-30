"""
MÓDULO DENÚNCIAS - FINAX OS
Canal de Ética anónimo para a escola

Funcionalidade:
- Denúncias 100% anónimas (não guarda identificação do aluno)
- Painel de ouvidoria para administradores
- Gestão de status das denúncias
- Proteção do denunciante
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

# Tipos de denúncia
TIPOS_DENUNCIA = ["Bullying", "Infraestrutura", "Assédio", "Outros"]

# Status possíveis
STATUS_PENDENTE = "Pendente"
STATUS_ANALISE = "Em Análise"
STATUS_RESOLVIDO = "Resolvido"

# Cores por status
COR_STATUS = {
    STATUS_PENDENTE: "\033[93m",  # Amarelo
    STATUS_ANALISE: "\033[94m",   # Azul
    STATUS_RESOLVIDO: "\033[92m"  # Verde
}


# ============================================
# CLASSE PRINCIPAL DE GESTÃO DE DENÚNCIAS
# ============================================

class GestaoDenuncias:
    """
    Classe responsável pela gestão do canal de ética anónimo.
    
    Funcionalidades:
    - Denúncias 100% anónimas (sem identificação do aluno)
    - Painel de ouvidoria para administradores
    - Gestão de status das denúncias
    """
    
    def __init__(self):
        """Inicializa o módulo com conexão ao banco de dados"""
        self.supabase = db_config.get_client()
        self.interface = Interface()
    
    # ============================================
    # 1. FAZER DENÚNCIA ANÓNIMA (ALUNO)
    # ============================================
    
    def fazer_denuncia_anonima(self, escola_id):
        """
        Regista uma denúncia anónima (sem identificar o aluno).
        
        Args:
            escola_id (str): ID da escola
        
        Returns:
            dict or None: Dados da denúncia registada
        """
        self.interface.limpar_tela()
        self.interface.mostrar_titulo("🕊️ CANAL DE ÉTICA - DENÚNCIA ANÓNIMA")
        
        # ============================================
        # AVISO IMPORTANTE (Responsabilidade)
        # ============================================
        print(f"\n{self.interface.cores.AMARELO}{self.interface.cores.NEGRITO}")
        print("╔════════════════════════════════════════════════════════════╗")
        print("║  ⚠️  AVISO IMPORTANTE                                      ║")
        print("║                                                            ║")
        print("║  A sua identidade será PRESERVADA.                         ║")
        print("║  Este canal é para denúncias legítimas e responsáveis.     ║")
        print("║  Denúncias falsas ou maliciosas podem ser rastreadas.      ║")
        print("║                                                            ║")
        print("║  ✅ Use este canal com responsabilidade.                   ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print(f"{self.interface.cores.RESET}")
        
        try:
            # Confirmar que o aluno quer continuar
            if not self.interface.confirmar("\nDeseja continuar com a denúncia anónima?"):
                self.interface.mostrar_info("Denúncia cancelada.")
                return None
            
            # ============================================
            # COLETAR DADOS DA DENÚNCIA (ANÓNIMO)
            # ============================================
            print(f"\n{self.interface.cores.AZUL}📝 PREENCHA OS DADOS DA DENÚNCIA{self.interface.cores.RESET}")
            
            # Título
            titulo = self.interface.input_com_validação(
                "Título/resumo da denúncia: ",
                obrigatorio=True
            )
            
            # Tipo de denúncia
            print(f"\n{self.interface.cores.AZUL}📌 TIPO DE DENÚNCIA{self.interface.cores.RESET}")
            for i, tipo in enumerate(TIPOS_DENUNCIA, 1):
                print(f"   {i} - {tipo}")
            
            tipo_opcao = self.interface.input_com_validação(
                "\nEscolha (1-{}): ".format(len(TIPOS_DENUNCIA)),
                obrigatorio=True,
                tipo="numero"
            )
            
            try:
                tipo_idx = int(tipo_opcao) - 1
                if tipo_idx < 0 or tipo_idx >= len(TIPOS_DENUNCIA):
                    raise ValueError
                tipo = TIPOS_DENUNCIA[tipo_idx]
            except ValueError:
                self.interface.exibir_mensagem("Tipo inválido!", tipo="erro")
                return None
            
            # Descrição detalhada
            print(f"\n{self.interface.cores.AZUL}📝 DESCRIÇÃO DETALHADA{self.interface.cores.RESET}")
            print("   Descreva a situação com o máximo de detalhes (local, data, envolvidos, etc.)")
            print("   ⚠️ NÃO inclua informações que possam identificá-lo.")
            
            descricao = self.interface.input_com_validação(
                "Descrição: ",
                obrigatorio=True
            )
            
            # Confirmar envio
            self.interface.mostrar_info("\n📋 CONFIRMAÇÃO")
            print(f"   Título: {titulo}")
            print(f"   Tipo: {tipo}")
            print(f"   Descrição: {descricao[:100]}{'...' if len(descricao) > 100 else ''}")
            
            if not self.interface.confirmar("\nDeseja enviar esta denúncia de forma anónima?"):
                self.interface.mostrar_info("Denúncia cancelada.")
                return None
            
            # ============================================
            # REGISTAR DENÚNCIA (SEM IDENTIFICAÇÃO)
            # ============================================
            denuncia_id = str(uuid.uuid4())
            data_atual = datetime.now().isoformat()
            
            dados_denuncia = {
                "id": denuncia_id,
                "titulo": titulo,
                "descricao": descricao,
                "tipo": tipo,
                "data": data_atual,
                "status": STATUS_PENDENTE,
                "escola_id": escola_id
                # NOTA: NÃO há campo aluno_id - é 100% anónimo!
            }
            
            resultado = self.supabase.table('denuncias').insert(dados_denuncia).execute()
            
            if resultado.data:
                print(f"\n{self.interface.cores.VERDE}{self.interface.cores.NEGRITO}")
                print("╔════════════════════════════════════════════════════════════╗")
                print("║  ✅ DENÚNCIA REGISTADA COM SUCESSO!                        ║")
                print("║                                                            ║")
                print("║  📌 Número de protocolo: {}  ║".format(denuncia_id[:8]))
                print("║                                                            ║")
                print("║  A sua identidade foi preservada.                          ║")
                print("║  O caso será analisado pela direção.                       ║")
                print("╚════════════════════════════════════════════════════════════╝")
                print(f"{self.interface.cores.RESET}")
                return resultado.data[0]
            else:
                self.interface.exibir_mensagem("Erro ao registar denúncia.", tipo="erro")
                return None
                
        except Exception as e:
            self.interface.exibir_mensagem(f"Erro ao registar denúncia: {e}", tipo="erro")
            return None
    
    # ============================================
    # 2. PAINEL DE OUVIDORIA (ADMIN)
    # ============================================
    
    def painel_ouvidoria(self, escola_id):
        """
        Painel exclusivo para administradores.
        Lista todas as denúncias e permite gestão de status.
        
        Args:
            escola_id (str): ID da escola
        """
        self.interface.limpar_tela()
        self.interface.mostrar_titulo("👁️ PAINEL DE OUVIDORIA - CANAL DE ÉTICA")
        
        try:
            # Buscar todas as denúncias da escola
            denuncias = self.supabase.table('denuncias')\
                .select('*')\
                .eq('escola_id', escola_id)\
                .order('data', desc=True)\
                .execute().data
            
            if not denuncias:
                self.interface.mostrar_info("Nenhuma denúncia registada.")
                return
            
            # Preparar dados para a tabela
            dados_tabela = []
            for d in denuncias:
                # Formatar data
                try:
                    data_obj = datetime.fromisoformat(d['data'])
                    data_formatada = data_obj.strftime("%d/%m/%Y %H:%M")
                except:
                    data_formatada = d['data'][:16] if d['data'] else "N/A"
                
                # Cor por status
                status_cor = COR_STATUS.get(d['status'], self.interface.cores.RESET)
                status_display = f"{status_cor}{d['status']}{self.interface.cores.RESET}"
                
                dados_tabela.append([
                    d['id'][:8],
                    data_formatada,
                    d['tipo'],
                    d['titulo'][:40] + ("..." if len(d['titulo']) > 40 else ""),
                    d['descricao'][:50] + ("..." if len(d['descricao']) > 50 else ""),
                    status_display
                ])
            
            # Exibir tabela
            print("\n")
            tabela = tabulate(
                dados_tabela,
                headers=["PROTOCOLO", "DATA", "TIPO", "TÍTULO", "DESCRIÇÃO", "STATUS"],
                tablefmt="grid"
            )
            print(tabela)
            
            # ============================================
            # OPÇÕES DE GESTÃO
            # ============================================
            print(f"\n{self.interface.cores.AZUL}{'═'*60}{self.interface.cores.RESET}")
            print("1 - 📝 Alterar status de uma denúncia")
            print("2 - 🔍 Ver detalhes completos")
            print("3 - 🔄 Atualizar lista")
            print("4 - ⬅️ Voltar")
            
            opcao = self.interface.input_com_validação(
                "\nEscolha uma opção",
                obrigatorio=True,
                tipo="numero"
            )
            
            if opcao == "1":
                self._alterar_status(denuncias, escola_id)
            elif opcao == "2":
                self._ver_detalhes(denuncias)
            elif opcao == "3":
                self.painel_ouvidoria(escola_id)
            elif opcao == "4":
                return
            else:
                self.interface.exibir_mensagem("Opção inválida!", tipo="erro")
            
        except Exception as e:
            self.interface.exibir_mensagem(f"Erro ao carregar painel: {e}", tipo="erro")
    
    # ============================================
    # 3. ALTERAR STATUS DE DENÚNCIA
    # ============================================
    
    def _alterar_status(self, denuncias, escola_id):
        """
        Altera o status de uma denúncia (admin apenas).
        
        Args:
            denuncias (list): Lista de denúncias
            escola_id (str): ID da escola
        """
        try:
            # Mostrar denúncias com opções
            print(f"\n{self.interface.cores.CIANO}DENÚNCIAS DISPONÍVEIS:{self.interface.cores.RESET}")
            for i, d in enumerate(denuncias, 1):
                status_cor = COR_STATUS.get(d['status'], self.interface.cores.RESET)
                print(f"   {i}. [{status_cor}{d['status']}{self.interface.cores.RESET}] {d['titulo'][:50]}")
            
            escolha = self.interface.input_com_validação(
                "\nNúmero da denúncia: ",
                obrigatorio=True,
                tipo="numero"
            )
            
            idx = int(escolha) - 1
            if idx < 0 or idx >= len(denuncias):
                self.interface.exibir_mensagem("Número inválido!", tipo="erro")
                return
            
            denuncia = denuncias[idx]
            
            # Mostrar opções de status
            status_opcoes = [STATUS_PENDENTE, STATUS_ANALISE, STATUS_RESOLVIDO]
            print(f"\n{self.interface.cores.AZUL}ALTERAR STATUS:{self.interface.cores.RESET}")
            for i, status in enumerate(status_opcoes, 1):
                status_cor = COR_STATUS.get(status, self.interface.cores.RESET)
                print(f"   {i}. {status_cor}{status}{self.interface.cores.RESET}")
            
            status_escolha = self.interface.input_com_validação(
                "Novo status (1-3): ",
                obrigatorio=True,
                tipo="numero"
            )
            
            status_idx = int(status_escolha) - 1
            if status_idx < 0 or status_idx >= len(status_opcoes):
                self.interface.exibir_mensagem("Status inválido!", tipo="erro")
                return
            
            novo_status = status_opcoes[status_idx]
            
            # Confirmar
            if self.interface.confirmar(f"\nAlterar status para '{novo_status}'?"):
                resultado = self.supabase.table('denuncias')\
                    .update({"status": novo_status})\
                    .eq('id', denuncia['id'])\
                    .execute()
                
                if resultado.data:
                    self.interface.mostrar_sucesso(f"Status alterado para '{novo_status}'!")
                else:
                    self.interface.exibir_mensagem("Erro ao alterar status.", tipo="erro")
                    
        except Exception as e:
            self.interface.exibir_mensagem(f"Erro ao alterar status: {e}", tipo="erro")
    
    # ============================================
    # 4. VER DETALHES DE DENÚNCIA
    # ============================================
    
    def _ver_detalhes(self, denuncias):
        """
        Exibe detalhes completos de uma denúncia.
        
        Args:
            denuncias (list): Lista de denúncias
        """
        try:
            print(f"\n{self.interface.cores.CIANO}DENÚNCIAS DISPONÍVEIS:{self.interface.cores.RESET}")
            for i, d in enumerate(denuncias, 1):
                print(f"   {i}. {d['titulo'][:50]}")
            
            escolha = self.interface.input_com_validação(
                "\nNúmero da denúncia: ",
                obrigatorio=True,
                tipo="numero"
            )
            
            idx = int(escolha) - 1
            if idx < 0 or idx >= len(denuncias):
                self.interface.exibir_mensagem("Número inválido!", tipo="erro")
                return
            
            denuncia = denuncias[idx]
            
            # Formatar data
            try:
                data_obj = datetime.fromisoformat(denuncia['data'])
                data_formatada = data_obj.strftime("%d/%m/%Y às %H:%M:%S")
            except:
                data_formatada = denuncia['data']
            
            # Exibir detalhes
            self.interface.limpar_tela()
            self.interface.mostrar_titulo("📄 DETALHES DA DENÚNCIA")
            
            print(f"\n{self.interface.cores.AZUL}📌 DADOS GERAIS{self.interface.cores.RESET}")
            print(f"   Protocolo: {denuncia['id']}")
            print(f"   Data: {data_formatada}")
            print(f"   Tipo: {denuncia['tipo']}")
            print(f"   Status: {COR_STATUS.get(denuncia['status'], '')}{denuncia['status']}{self.interface.cores.RESET}")
            
            print(f"\n{self.interface.cores.AZUL}📝 TÍTULO{self.interface.cores.RESET}")
            print(f"   {denuncia['titulo']}")
            
            print(f"\n{self.interface.cores.AZUL}📄 DESCRIÇÃO COMPLETA{self.interface.cores.RESET}")
            print(f"   {denuncia['descricao']}")
            
            print(f"\n{self.interface.cores.AMARELO}🔒 Esta denúncia foi registada de forma anónima.{self.interface.cores.RESET}")
            
            input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)
            
        except Exception as e:
            self.interface.exibir_mensagem(f"Erro ao ver detalhes: {e}", tipo="erro")
    
    # ============================================
    # 5. MENU PRINCIPAL (POR PERFIL)
    # ============================================
    
    def menu_por_perfil(self, sessao):
        """
        Menu principal do módulo de denúncias conforme perfil.
        
        Args:
            sessao (dict): Dados da sessão do utilizador logado
        """
        nivel = sessao.get('nivel')
        escola_id = sessao.get('escola')
        
        if nivel == 'Administrador':
            self._menu_admin(escola_id)
        else:
            self._menu_aluno(escola_id)
    
    def _menu_aluno(self, escola_id):
        """
        Menu para alunos (apenas fazer denúncia).
        
        Args:
            escola_id (str): ID da escola
        """
        while True:
            self.interface.limpar_tela()
            self.interface.mostrar_titulo("🕊️ CANAL DE ÉTICA - FINAX OS")
            
            print(f"\n{self.interface.cores.CIANO}")
            print("   Este é um espaço seguro para reportar situações")
            print("   que violam o código de conduta da escola.")
            print(f"{self.interface.cores.RESET}")
            
            print("\n1 - 📝 Fazer Denúncia Anónima")
            print("2 - ⬅️ Voltar ao Menu Principal")
            
            opcao = self.interface.input_com_validação(
                "\nEscolha uma opção",
                obrigatorio=True,
                tipo="numero"
            )
            
            if opcao == "1":
                self.fazer_denuncia_anonima(escola_id)
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)
            elif opcao == "2":
                break
            else:
                self.interface.exibir_mensagem("Opção inválida!", tipo="erro")
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)
    
    def _menu_admin(self, escola_id):
        """
        Menu para administradores (painel de ouvidoria).
        
        Args:
            escola_id (str): ID da escola
        """
        while True:
            self.interface.limpar_tela()
            self.interface.mostrar_titulo("🕊️ CANAL DE ÉTICA - FINAX OS")
            
            print("\n1 - 👁️ Painel de Ouvidoria")
            print("2 - ⬅️ Voltar ao Menu Principal")
            
            opcao = self.interface.input_com_validação(
                "\nEscolha uma opção",
                obrigatorio=True,
                tipo="numero"
            )
            
            if opcao == "1":
                self.painel_ouvidoria(escola_id)
            elif opcao == "2":
                break
            else:
                self.interface.exibir_mensagem("Opção inválida!", tipo="erro")
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)


# ============================================
# FUNÇÃO DE INTEGRAÇÃO PARA O MAIN
# ============================================

def iniciar_denuncias(sessao):
    """
    Função de integração para ser chamada pelo main.py
    
    Args:
        sessao (dict): Dados da sessão do utilizador logado
    """
    denuncias = GestaoDenuncias()
    denuncias.menu_por_perfil(sessao)


# ============================================
# TESTE DO MÓDULO
# ============================================

if __name__ == "__main__":
    print("🧪 Teste do módulo Canal de Ética")
    print("⚠️ Para testar, execute o main.py com um utilizador logado.")
    print("   Ou utilize: denuncias = GestaoDenuncias()")