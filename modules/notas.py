"""
MÓDULO NOTAS - FINAX OS
Sistema de gestão escolar com Supabase Cloud

Funcionalidade:
- Gestão de avaliações e faltas dos alunos
- Lançamento de notas com cálculo automático de média
- Boletim individual e pauta de turma
- Validação conforme sistema angolano (0-20 valores)
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

# Limites do sistema de avaliação angolano
NOTA_MINIMA = 0
NOTA_MAXIMA = 20
MEDIA_APROVACAO = 10

# Mensagens de validação
MSG_NOTA_INVALIDA = f"As notas devem estar entre {NOTA_MINIMA} e {NOTA_MAXIMA} valores."


# ============================================
# CLASSE PRINCIPAL DE GESTÃO DE NOTAS
# ============================================

class GestaoNotas:
    """
    Classe responsável pela gestão de notas e faltas dos alunos.
    
    Funcionalidades:
    - Lançamento de notas com cálculo automático de média
    - Boletim individual do aluno
    - Pauta de turma (listagem de notas)
    - Validação conforme sistema angolano (0-20)
    """
    
    def __init__(self):
        """Inicializa o módulo com conexão ao banco de dados"""
        self.supabase = db_config.get_client()
        self.interface = Interface()
    
    # ============================================
    # 1. FUNÇÕES AUXILIARES
    # ============================================
    
    def _calcular_media(self, nota_1, nota_2, nota_3):
        """
        Calcula a média aritmética das 3 notas.
        
        Args:
            nota_1 (float): Primeira nota
            nota_2 (float): Segunda nota
            nota_3 (float): Terceira nota
        
        Returns:
            float: Média aritmética
        """
        return round((nota_1 + nota_2 + nota_3) / 3, 1)
    
    def _validar_nota(self, nota):
        """
        Valida se a nota está dentro do sistema angolano (0-20).
        
        Args:
            nota (float): Nota a validar
        
        Returns:
            bool: True se válida, False caso contrário
        """
        return NOTA_MINIMA <= nota <= NOTA_MAXIMA
    
    def _buscar_alunos_por_turma(self, escola_id, turma):
        """
        Busca todos os alunos de uma turma.
        
        Args:
            escola_id (str): ID da escola
            turma (str): Nome da turma
        
        Returns:
            list: Lista de alunos da turma
        """
        try:
            alunos = self.supabase.table('usuarios')\
                .select('id, nome')\
                .eq('escola_id', escola_id)\
                .eq('nivel', 'Estudante')\
                .eq('turma', turma)\
                .order('nome', asc=True)\
                .execute()
            return alunos.data if alunos.data else []
        except Exception as e:
            self.interface.exibir_mensagem(f"Erro ao buscar alunos: {e}", tipo="erro")
            return []
    
    def _buscar_notas_aluno(self, aluno_id, disciplina=None):
        """
        Busca as notas de um aluno.
        
        Args:
            aluno_id (str): ID do aluno
            disciplina (str, optional): Disciplina específica
        
        Returns:
            dict or None: Dados das notas
        """
        try:
            query = self.supabase.table('notas')\
                .select('*')\
                .eq('aluno_id', aluno_id)
            
            if disciplina:
                query = query.eq('disciplina', disciplina)
            
            resultado = query.execute()
            return resultado.data[0] if resultado.data else None
        except Exception:
            return None
    
    # ============================================
    # 2. LANÇAR NOTAS (UPSERT)
    # ============================================
    
    def lancar_notas(self, aluno_id, escola_id):
        """
        Lança ou atualiza as notas e faltas de um aluno.
        
        Args:
            aluno_id (str): ID do aluno
            escola_id (str): ID da escola
        
        Returns:
            dict or None: Dados das notas lançadas
        """
        self.interface.limpar_tela()
        self.interface.mostrar_titulo("📝 LANÇAR NOTAS - FINAX OS")
        
        try:
            # Buscar nome do aluno
            aluno = self.supabase.table('usuarios')\
                .select('nome, turma')\
                .eq('id', aluno_id)\
                .execute()
            
            if not aluno.data:
                self.interface.exibir_mensagem("Aluno não encontrado!", tipo="erro")
                return None
            
            nome_aluno = aluno.data[0]['nome']
            turma = aluno.data[0].get('turma', 'N/A')
            
            self.interface.mostrar_info(f"Aluno: {self.interface.cores.CIANO}{nome_aluno}{self.interface.cores.RESET}")
            self.interface.mostrar_info(f"Turma: {turma}")
            print()
            
            # Perguntar disciplina
            disciplina = self.interface.input_com_validação(
                "Disciplina: ",
                obrigatorio=True
            )
            
            # Verificar se já existem notas para esta disciplina
            notas_existentes = self._buscar_notas_aluno(aluno_id, disciplina)
            
            if notas_existentes:
                self.interface.mostrar_info(f"Atualizando notas para {disciplina}...")
                print(f"   Notas atuais: N1={notas_existentes.get('nota_1', 0)} | N2={notas_existentes.get('nota_2', 0)} | N3={notas_existentes.get('nota_3', 0)}")
                print(f"   Faltas atuais: {notas_existentes.get('faltas', 0)}")
                print()
            
            # Coletar notas
            print(f"{self.interface.cores.AZUL}📊 NOTAS (0 a 20){self.interface.cores.RESET}")
            
            while True:
                nota_1 = self.interface.input_com_validação(
                    "Nota 1: ",
                    obrigatorio=True,
                    tipo="numero"
                )
                nota_1 = float(nota_1)
                if self._validar_nota(nota_1):
                    break
                self.interface.exibir_mensagem(MSG_NOTA_INVALIDA, tipo="erro")
            
            while True:
                nota_2 = self.interface.input_com_validação(
                    "Nota 2: ",
                    obrigatorio=True,
                    tipo="numero"
                )
                nota_2 = float(nota_2)
                if self._validar_nota(nota_2):
                    break
                self.interface.exibir_mensagem(MSG_NOTA_INVALIDA, tipo="erro")
            
            while True:
                nota_3 = self.interface.input_com_validação(
                    "Nota 3: ",
                    obrigatorio=True,
                    tipo="numero"
                )
                nota_3 = float(nota_3)
                if self._validar_nota(nota_3):
                    break
                self.interface.exibir_mensagem(MSG_NOTA_INVALIDA, tipo="erro")
            
            # Coletar faltas
            faltas = self.interface.input_com_validação(
                "Número de faltas: ",
                obrigatorio=True,
                tipo="numero"
            )
            faltas = int(faltas)
            
            # Calcular média
            media = self._calcular_media(nota_1, nota_2, nota_3)
            
            # Preparar dados para upsert
            dados_notas = {
                "nota_1": nota_1,
                "nota_2": nota_2,
                "nota_3": nota_3,
                "faltas": faltas,
                "media": media,
                "disciplina": disciplina
            }
            
            # Confirmar
            self.interface.mostrar_info("\n📋 CONFIRMAÇÃO")
            print(f"   Disciplina: {disciplina}")
            print(f"   Notas: {nota_1} | {nota_2} | {nota_3}")
            print(f"   Média: {media:.1f}")
            print(f"   Faltas: {faltas}")
            
            if not self.interface.confirmar("\nDeseja guardar estas notas?"):
                self.interface.mostrar_info("Operação cancelada.")
                return None
            
            # Executar UPSERT
            if notas_existentes:
                # UPDATE: atualizar registo existente
                resultado = self.supabase.table('notas')\
                    .update(dados_notas)\
                    .eq('id', notas_existentes['id'])\
                    .execute()
                self.interface.mostrar_sucesso(f"Notas de {disciplina} atualizadas com sucesso!")
            else:
                # INSERT: criar novo registo
                dados_notas.update({
                    "id": str(uuid.uuid4()),
                    "aluno_id": aluno_id,
                    "escola_id": escola_id
                })
                resultado = self.supabase.table('notas').insert(dados_notas).execute()
                self.interface.mostrar_sucesso(f"Notas de {disciplina} lançadas com sucesso!")
            
            return resultado.data[0] if resultado.data else None
            
        except Exception as e:
            self.interface.exibir_mensagem(f"Erro ao lançar notas: {e}", tipo="erro")
            return None
    
    # ============================================
    # 3. VER BOLETIM DO ALUNO
    # ============================================
    
    def ver_boletim(self, aluno_id):
        """
        Exibe o boletim completo de um aluno.
        
        Args:
            aluno_id (str): ID do aluno
        """
        self.interface.limpar_tela()
        self.interface.mostrar_titulo("📋 BOLETIM ESCOLAR - FINAX OS")
        
        try:
            # Buscar dados do aluno
            aluno = self.supabase.table('usuarios')\
                .select('nome, turma, classe')\
                .eq('id', aluno_id)\
                .execute()
            
            if not aluno.data:
                self.interface.exibir_mensagem("Aluno não encontrado!", tipo="erro")
                return
            
            nome_aluno = aluno.data[0]['nome']
            turma = aluno.data[0].get('turma', 'N/A')
            classe = aluno.data[0].get('classe', 'N/A')
            turma_completa = f"{classe} {turma}".strip()
            
            # Buscar todas as notas do aluno
            notas = self.supabase.table('notas')\
                .select('*')\
                .eq('aluno_id', aluno_id)\
                .order('disciplina', asc=True)\
                .execute()
            
            print(f"\n{self.interface.cores.AZUL}Aluno: {self.interface.cores.CIANO}{nome_aluno}{self.interface.cores.RESET}")
            print(f"{self.interface.cores.AZUL}Turma: {turma_completa}{self.interface.cores.RESET}")
            print(f"{self.interface.cores.AZUL}Data: {datetime.now().strftime('%d/%m/%Y')}{self.interface.cores.RESET}")
            print()
            
            if not notas.data:
                self.interface.exibir_mensagem("Nenhuma nota registada para este aluno.", tipo="info")
                return
            
            # Preparar dados para a tabela
            dados_tabela = []
            medias = []
            total_faltas = 0
            
            for nota in notas.data:
                # Cor para a média
                media = nota.get('media', 0)
                if media >= MEDIA_APROVACAO:
                    media_cor = self.interface.cores.VERDE
                else:
                    media_cor = self.interface.cores.VERMELHO
                
                dados_tabela.append([
                    nota['disciplina'],
                    f"{nota['nota_1']:.1f}",
                    f"{nota['nota_2']:.1f}",
                    f"{nota['nota_3']:.1f}",
                    f"{media_cor}{media:.1f}{self.interface.cores.RESET}",
                    nota.get('faltas', 0)
                ])
                medias.append(media)
                total_faltas += nota.get('faltas', 0)
            
            # Exibir tabela
            tabela = tabulate(
                dados_tabela,
                headers=["DISCIPLINA", "N1", "N2", "N3", "MÉDIA", "FALTAS"],
                tablefmt="grid"
            )
            print(tabela)
            
            # Calcular média geral
            if medias:
                media_geral = sum(medias) / len(medias)
                if media_geral >= MEDIA_APROVACAO:
                    status_geral = f"{self.interface.cores.VERDE}APROVADO{self.interface.cores.RESET}"
                else:
                    status_geral = f"{self.interface.cores.VERMELHO}REPROVADO{self.interface.cores.RESET}"
                
                print(f"\n{self.interface.cores.AZUL}{'═'*60}{self.interface.cores.RESET}")
                print(f"📊 MÉDIA GERAL: {media_geral:.1f}")
                print(f"📅 TOTAL DE FALTAS: {total_faltas}")
                print(f"🏆 STATUS: {status_geral}")
            
        except Exception as e:
            self.interface.exibir_mensagem(f"Erro ao gerar boletim: {e}", tipo="erro")
    
    # ============================================
    # 4. LISTAR NOTAS DA TURMA (PAUTA)
    # ============================================
    
    def listar_notas_turma(self, escola_id, turma):
        """
        Exibe a pauta de notas de todos os alunos de uma turma.
        
        Args:
            escola_id (str): ID da escola
            turma (str): Nome da turma
        """
        self.interface.limpar_tela()
        self.interface.mostrar_titulo(f"📊 PAUTA DE NOTAS - TURMA {turma.upper()}")
        
        try:
            # Buscar alunos da turma
            alunos = self._buscar_alunos_por_turma(escola_id, turma)
            
            if not alunos:
                self.interface.exibir_mensagem(f"Nenhum aluno encontrado na turma {turma}.", tipo="info")
                return
            
            # Para cada aluno, buscar suas notas
            dados_tabela = []
            
            for aluno in alunos:
                notas = self._buscar_notas_aluno(aluno['id'])
                
                if notas:
                    media = notas.get('media', 0)
                    if media >= MEDIA_APROVACAO:
                        media_cor = self.interface.cores.VERDE
                    else:
                        media_cor = self.interface.cores.VERMELHO
                    
                    dados_tabela.append([
                        aluno['nome'],
                        notas.get('disciplina', 'N/A'),
                        f"{notas['nota_1']:.1f}",
                        f"{notas['nota_2']:.1f}",
                        f"{notas['nota_3']:.1f}",
                        f"{media_cor}{media:.1f}{self.interface.cores.RESET}",
                        notas.get('faltas', 0)
                    ])
                else:
                    dados_tabela.append([
                        aluno['nome'],
                        "Sem notas",
                        "-",
                        "-",
                        "-",
                        f"{self.interface.cores.AMARELO}N/A{self.interface.cores.RESET}",
                        "-"
                    ])
            
            # Exibir tabela
            tabela = tabulate(
                dados_tabela,
                headers=["ALUNO", "DISCIPLINA", "N1", "N2", "N3", "MÉDIA", "FALTAS"],
                tablefmt="grid"
            )
            print(tabela)
            
            # Estatísticas da turma
            medias = [float(linha[5].replace(self.interface.cores.VERDE, '').replace(self.interface.cores.VERMELHO, '').replace(self.interface.cores.RESET, '')) 
                      for linha in dados_tabela if linha[5] != f"{self.interface.cores.AMARELO}N/A{self.interface.cores.RESET}"]
            
            if medias:
                media_turma = sum(medias) / len(medias)
                aprovados = sum(1 for m in medias if m >= MEDIA_APROVACAO)
                
                print(f"\n{self.interface.cores.AZUL}{'═'*60}{self.interface.cores.RESET}")
                print(f"📊 ESTATÍSTICAS DA TURMA")
                print(f"   Total de alunos: {len(alunos)}")
                print(f"   Média da turma: {media_turma:.1f}")
                print(f"   Alunos aprovados: {aprovados}/{len(alunos)} ({aprovados/len(alunos)*100:.1f}%)")
            
        except Exception as e:
            self.interface.exibir_mensagem(f"Erro ao listar notas: {e}", tipo="erro")
    
    # ============================================
    # 5. MENU PRINCIPAL
    # ============================================
    
    def menu(self, escola_id):
        """
        Menu interativo do módulo de notas.
        
        Args:
            escola_id (str): ID da escola do administrador logado
        """
        while True:
            self.interface.limpar_tela()
            self.interface.mostrar_titulo("📝 FINAX NOTAS - GESTÃO DE AVALIAÇÕES")
            
            print("1 - 📊 Lançar/Atualizar Notas")
            print("2 - 📋 Ver Boletim de Aluno")
            print("3 - 📚 Pauta de Turma")
            print("4 - ⬅️ Voltar ao Menu Principal")
            
            opcao = self.interface.input_com_validação(
                "\nEscolha uma opção",
                obrigatorio=True,
                tipo="numero"
            )
            
            if opcao == "1":
                aluno_id = self.interface.input_com_validação(
                    "ID do aluno: ",
                    obrigatorio=True
                )
                self.lancar_notas(aluno_id, escola_id)
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)
                
            elif opcao == "2":
                aluno_id = self.interface.input_com_validação(
                    "ID do aluno: ",
                    obrigatorio=True
                )
                self.ver_boletim(aluno_id)
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)
                
            elif opcao == "3":
                turma = self.interface.input_com_validação(
                    "Turma (ex: A, B, C): ",
                    obrigatorio=True
                )
                self.listar_notas_turma(escola_id, turma)
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)
                
            elif opcao == "4":
                break
                
            else:
                self.interface.exibir_mensagem("Opção inválida!", tipo="erro")
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)


# ============================================
# FUNÇÃO DE INTEGRAÇÃO PARA O MAIN
# ============================================

def iniciar_notas(escola_id):
    """
    Função de integração para ser chamada pelo main.py
    
    Args:
        escola_id (str): ID da escola do administrador logado
    """
    notas = GestaoNotas()
    notas.menu(escola_id)


# ============================================
# TESTE DO MÓDULO
# ============================================

if __name__ == "__main__":
    print("🧪 Teste do módulo Gestão de Notas")
    print("⚠️ Para testar, execute o main.py com um administrador logado.")
    print("   Ou utilize: notas = GestaoNotas()")
    print("   notas.lancar_notas('aluno_id', 'escola_id')")