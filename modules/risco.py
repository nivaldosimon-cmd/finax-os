"""
MÓDULO RISCO - FINAX OS
Sistema de gestão escolar com Supabase Cloud

Funcionalidade:
- Análise de risco de reprovação dos alunos
- Baseado em média das notas e faltas
- Classificação em níveis: CRÍTICO, ATENÇÃO, SEGURO
- Relatório completo para administradores
"""

import sys
import os

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
# CONSTANTES (REGRAS DE ANGOLA)
# ============================================

# Média mínima para aprovação (sistema angolano: 10 valores)
MEDIA_MINIMA_APROVACAO = 10.0

# Limite de faltas para reprovação (25 faltas = reprovação direta)
LIMITE_FALTAS_REPROVACAO = 25

# Limite de faltas para alerta (20 faltas = atenção)
LIMITE_FALTAS_ATENCAO = 20

# Limite de faltas seguro (menos de 15 faltas = seguro)
LIMITE_FALTAS_SEGURO = 15

# ============================================
# CLASSIFICAÇÃO DE RISCO
# ============================================

class NivelRisco:
    """Enum para os níveis de risco"""
    CRITICO = "CRÍTICO"
    ATENCAO = "ATENÇÃO"
    SEGURO = "SEGURO"
    SEM_DADOS = "SEM DADOS"


# ============================================
# CLASSE PRINCIPAL DO MÓDULO RISCO
# ============================================

class AnalisadorRisco:
    """
    Classe responsável pela análise de risco de reprovação dos alunos.
    
    Regras de Angola:
    - Média mínima: 10 valores
    - Limite de faltas: 25 faltas = reprovação direta
    
    Níveis:
    - CRÍTICO (Vermelho): Média < 10 E Faltas > 25
    - ATENÇÃO (Amarelo): Média < 10 OU Faltas > 20
    - SEGURO (Verde): Média >= 10 e Faltas < 15
    """
    
    def __init__(self):
        """Inicializa o módulo com conexão ao banco de dados"""
        self.supabase = db_config.get_client()
        self.interface = Interface()
    
    # ============================================
    # 1. CÁLCULO DE MÉDIA
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
        notas = [n for n in [nota_1, nota_2, nota_3] if n is not None]
        if not notas:
            return 0.0
        return sum(notas) / len(notas)
    
    # ============================================
    # 2. CLASSIFICAÇÃO DO RISCO
    # ============================================
    
    def _classificar_risco(self, media, faltas):
        """
        Classifica o risco do aluno com base nas regras de Angola.
        
        Regras:
        - CRÍTICO: Média < 10 E Faltas > 25
        - ATENÇÃO: Média < 10 OU Faltas > 20
        - SEGURO: Média >= 10 e Faltas < 15
        
        Args:
            media (float): Média das notas
            faltas (int): Número de faltas
        
        Returns:
            tuple: (nivel, mensagem)
        """
        if media == 0 and faltas == 0:
            return NivelRisco.SEM_DADOS, "Sem notas ou faltas registadas"
        
        if media < MEDIA_MINIMA_APROVACAO and faltas > LIMITE_FALTAS_REPROVACAO:
            return NivelRisco.CRITICO, f"Média {media:.1f} < 10 e {faltas} faltas > {LIMITE_FALTAS_REPROVACAO}"
        
        if media < MEDIA_MINIMA_APROVACAO:
            return NivelRisco.ATENCAO, f"Média {media:.1f} abaixo de {MEDIA_MINIMA_APROVACAO:.0f}"
        
        if faltas > LIMITE_FALTAS_ATENCAO:
            return NivelRisco.ATENCAO, f"{faltas} faltas excedem o limite de alerta ({LIMITE_FALTAS_ATENCAO})"
        
        if faltas > LIMITE_FALTAS_SEGURO:
            return NivelRisco.ATENCAO, f"{faltas} faltas requerem atenção"
        
        return NivelRisco.SEGURO, "Aprovado (média e faltas dentro dos limites)"
    
    # ============================================
    # 2. BUSCAR DADOS DOS ALUNOS
    # ============================================
    
    def _buscar_dados_alunos(self, escola_id):
        """
        Busca todos os alunos da escola com suas notas e faltas.
        
        Args:
            escola_id (str): ID da escola
        
        Returns:
            list: Lista de dicionários com dados dos alunos
        """
        try:
            # Buscar todos os estudantes da escola
            resposta = self.supabase.table('usuarios')\
                .select('id, nome, turma, classe')\
                .eq('escola_id', escola_id)\
                .eq('nivel', 'Estudante')\
                .execute()
            
            alunos = resposta.data
            
            if not alunos:
                return []
            
            # Para cada aluno, buscar suas notas e faltas
            dados_completos = []
            
            for aluno in alunos:
                # Buscar notas do aluno
                notas_resp = self.supabase.table('notas')\
                    .select('nota_1, nota_2, nota_3, faltas')\
                    .eq('aluno_id', aluno['id'])\
                    .execute()
                
                if notas_resp.data:
                    notas = notas_resp.data[0]
                    nota_1 = notas.get('nota_1', 0)
                    nota_2 = notas.get('nota_2', 0)
                    nota_3 = notas.get('nota_3', 0)
                    faltas = notas.get('faltas', 0)
                else:
                    nota_1 = nota_2 = nota_3 = 0
                    faltas = 0
                
                # Calcular média
                media = self._calcular_media(nota_1, nota_2, nota_3)
                
                # Classificar risco
                nivel, motivo = self._classificar_risco(media, faltas)
                
                dados_completos.append({
                    'id': aluno['id'],
                    'nome': aluno['nome'],
                    'turma': aluno.get('turma', 'N/A'),
                    'classe': aluno.get('classe', 'N/A'),
                    'media': media,
                    'nota_1': nota_1,
                    'nota_2': nota_2,
                    'nota_3': nota_3,
                    'faltas': faltas,
                    'nivel_risco': nivel,
                    'motivo': motivo
                })
            
            # Ordenar por nível de risco (CRÍTICO primeiro, depois ATENÇÃO, depois SEGURO)
            ordem_risco = {NivelRisco.CRITICO: 1, NivelRisco.ATENCAO: 2, NivelRisco.SEGURO: 3, NivelRisco.SEM_DADOS: 4}
            dados_completos.sort(key=lambda x: ordem_risco.get(x['nivel_risco'], 5))
            
            return dados_completos
            
        except Exception as e:
            self.interface.exibir_mensagem(f"Erro ao buscar dados: {e}", tipo="erro")
            return []
    
    # ============================================
    # 3. EXIBIR RELATÓRIO DE RISCO
    # ============================================
    
    def exibir_relatorio_risco(self, escola_id):
        """
        Exibe relatório de todos os alunos da escola que apresentam risco.
        
        Args:
            escola_id (str): ID da escola do administrador
        """
        self.interface.limpar_tela()
        self.interface.mostrar_titulo("⚠️ ANÁLISE DE RISCO DE REPROVAÇÃO")
        self.interface.mostrar_info(f"Regras de Avaliação (Angola):")
        print(f"   • Média mínima para aprovação: {self.interface.cores.AMARELO}{MEDIA_MINIMA_APROVACAO:.0f} valores{self.interface.cores.RESET}")
        print(f"   • Limite de faltas para reprovação: {self.interface.cores.VERMELHO}{LIMITE_FALTAS_REPROVACAO} faltas{self.interface.cores.RESET}")
        print(f"   • Alerta de atenção: {self.interface.cores.AMARELO}{LIMITE_FALTAS_ATENCAO} faltas{self.interface.cores.RESET}")
        
        try:
            # Buscar dados dos alunos
            self.interface.mostrar_processando("Analisando dados dos alunos...")
            alunos = self._buscar_dados_alunos(escola_id)
            
            if not alunos:
                self.interface.exibir_mensagem(
                    "Nenhum aluno encontrado nesta escola.",
                    tipo="info"
                )
                return
            
            # ============================================
            # 3.1 FILTRAR ALUNOS COM RISCO (CRÍTICO OU ATENÇÃO)
            # ============================================
            alunos_risco = [a for a in alunos if a['nivel_risco'] in [NivelRisco.CRITICO, NivelRisco.ATENCAO]]
            alunos_seguros = [a for a in alunos if a['nivel_risco'] == NivelRisco.SEGURO]
            alunos_sem_dados = [a for a in alunos if a['nivel_risco'] == NivelRisco.SEM_DADOS]
            
            # ============================================
            # 3.2 EXIBIR ALUNOS EM RISCO (TABELA PRINCIPAL)
            # ============================================
            if alunos_risco:
                self.interface.mostrar_titulo("🚨 ALUNOS EM SITUAÇÃO DE RISCO", nivel=2)
                
                dados_tabela = []
                for aluno in alunos_risco:
                    # Definir cor conforme nível
                    if aluno['nivel_risco'] == NivelRisco.CRITICO:
                        situacao = f"{self.interface.cores.VERMELHO}{self.interface.cores.NEGRITO}CRÍTICO{self.interface.cores.RESET}"
                    else:
                        situacao = f"{self.interface.cores.AMARELO}ATENÇÃO{self.interface.cores.RESET}"
                    
                    # Cor para média
                    if aluno['media'] < MEDIA_MINIMA_APROVACAO:
                        media_cor = self.interface.cores.VERMELHO
                    else:
                        media_cor = self.interface.cores.VERDE
                    
                    # Cor para faltas
                    if aluno['faltas'] > LIMITE_FALTAS_REPROVACAO:
                        faltas_cor = self.interface.cores.VERMELHO
                    elif aluno['faltas'] > LIMITE_FALTAS_ATENCAO:
                        faltas_cor = self.interface.cores.AMARELO
                    else:
                        faltas_cor = self.interface.cores.VERDE
                    
                    dados_tabela.append([
                        aluno['nome'],
                        f"{aluno.get('classe', 'N/A')} {aluno.get('turma', '')}",
                        f"{media_cor}{aluno['media']:.1f}{self.interface.cores.RESET}",
                        f"{faltas_cor}{aluno['faltas']}{self.interface.cores.RESET}",
                        situacao
                    ])
                
                tabela = tabulate(
                    dados_tabela,
                    headers=["NOME", "TURMA", "MÉDIA", "FALTAS", "SITUAÇÃO"],
                    tablefmt="grid"
                )
                print(f"\n{tabela}")
                
                print(f"\n{self.interface.cores.VERMELHO}⚠️ Total de alunos em risco: {len(alunos_risco)}{self.interface.cores.RESET}")
            
            # ============================================
            # 3.3 EXIBIR ALUNOS SEGUROS (OPCIONAL)
            # ============================================
            if alunos_seguros:
                print(f"\n{self.interface.cores.VERDE}✅ ALUNOS SEGUROS (sem risco){self.interface.cores.RESET}")
                print(f"   Total: {len(alunos_seguros)} aluno(s) com média >= {MEDIA_MINIMA_APROVACAO:.0f} e faltas < {LIMITE_FALTAS_SEGURO}")
            
            # ============================================
            # 3.4 EXIBIR ALUNOS SEM DADOS (OPCIONAL)
            # ============================================
            if alunos_sem_dados:
                print(f"\n{self.interface.cores.AMARELO}⚠️ ALUNOS SEM NOTAS REGISTADAS{self.interface.cores.RESET}")
                print(f"   Total: {len(alunos_sem_dados)} aluno(s)")
                for aluno in alunos_sem_dados:
                    print(f"   • {aluno['nome']} - {aluno.get('classe', 'N/A')} {aluno.get('turma', '')}")
            
            # ============================================
            # 3.5 RESUMO ESTATÍSTICO
            # ============================================
            self.interface.mostrar_linha()
            print(f"\n{self.interface.cores.AZUL}📊 RESUMO GERAL{self.interface.cores.RESET}")
            print(f"   Total de alunos analisados: {len(alunos)}")
            print(f"   {self.interface.cores.VERMELHO}CRÍTICO: {len([a for a in alunos_risco if a['nivel_risco'] == NivelRisco.CRITICO])}{self.interface.cores.RESET}")
            print(f"   {self.interface.cores.AMARELO}ATENÇÃO: {len([a for a in alunos_risco if a['nivel_risco'] == NivelRisco.ATENCAO])}{self.interface.cores.RESET}")
            print(f"   {self.interface.cores.VERDE}SEGURO: {len(alunos_seguros)}{self.interface.cores.RESET}")
            
        except Exception as e:
            self.interface.exibir_mensagem(f"Erro ao gerar relatório: {e}", tipo="erro")
    
    # ============================================
    # 4. RELATÓRIO DETALHADO POR ALUNO
    # ============================================
    
    def exibir_detalhes_aluno(self, escola_id, aluno_id=None):
        """
        Exibe detalhes completos de um aluno específico.
        
        Args:
            escola_id (str): ID da escola
            aluno_id (str, optional): ID do aluno. Se None, pede input.
        """
        if not aluno_id:
            aluno_id = self.interface.input_com_validação(
                "ID do aluno: ",
                obrigatorio=True
            )
        
        try:
            # Buscar dados do aluno
            alunos = self._buscar_dados_alunos(escola_id)
            aluno = next((a for a in alunos if a['id'] == aluno_id), None)
            
            if not aluno:
                self.interface.exibir_mensagem("Aluno não encontrado.", tipo="erro")
                return
            
            self.interface.limpar_tela()
            self.interface.mostrar_titulo(f"📋 FICHA DE ANÁLISE - {aluno['nome']}")
            
            print(f"\n{self.interface.cores.AZUL}📌 DADOS PESSOAIS{self.interface.cores.RESET}")
            print(f"   Nome: {aluno['nome']}")
            print(f"   Turma: {aluno.get('classe', 'N/A')} {aluno.get('turma', '')}")
            
            print(f"\n{self.interface.cores.AZUL}📊 DESEMPENHO ACADÉMICO{self.interface.cores.RESET}")
            print(f"   Nota 1: {aluno['nota_1']:.1f}")
            print(f"   Nota 2: {aluno['nota_2']:.1f}")
            print(f"   Nota 3: {aluno['nota_3']:.1f}")
            print(f"   Média: {self.interface.cores.AMARELO if aluno['media'] < MEDIA_MINIMA_APROVACAO else self.interface.cores.VERDE}{aluno['media']:.1f}{self.interface.cores.RESET}")
            
            print(f"\n{self.interface.cores.AZUL}📅 ASSIDUIDADE{self.interface.cores.RESET}")
            if aluno['faltas'] > LIMITE_FALTAS_REPROVACAO:
                faltas_cor = self.interface.cores.VERMELHO
            elif aluno['faltas'] > LIMITE_FALTAS_ATENCAO:
                faltas_cor = self.interface.cores.AMARELO
            else:
                faltas_cor = self.interface.cores.VERDE
            print(f"   Total de faltas: {faltas_cor}{aluno['faltas']}{self.interface.cores.RESET}")
            
            print(f"\n{self.interface.cores.AZUL}⚠️ ANÁLISE DE RISCO{self.interface.cores.RESET}")
            if aluno['nivel_risco'] == NivelRisco.CRITICO:
                print(f"   Situação: {self.interface.cores.VERMELHO}{self.interface.cores.NEGRITO}CRÍTICO{self.interface.cores.RESET}")
            elif aluno['nivel_risco'] == NivelRisco.ATENCAO:
                print(f"   Situação: {self.interface.cores.AMARELO}ATENÇÃO{self.interface.cores.RESET}")
            else:
                print(f"   Situação: {self.interface.cores.VERDE}SEGURO{self.interface.cores.RESET}")
            
            print(f"   Motivo: {aluno['motivo']}")
            
            # Sugestões
            print(f"\n{self.interface.cores.AZUL}💡 SUGESTÕES{self.interface.cores.RESET}")
            if aluno['nivel_risco'] == NivelRisco.CRITICO:
                print("   • Reforço escolar imediato")
                print("   • Reunião com pais/responsáveis")
                print("   • Plano de recuperação de notas")
            elif aluno['nivel_risco'] == NivelRisco.ATENCAO:
                if aluno['media'] < MEDIA_MINIMA_APROVACAO:
                    print("   • Acompanhamento pedagógico")
                    print("   • Atividades de recuperação")
                if aluno['faltas'] > LIMITE_FALTAS_ATENCAO:
                    print("   • Conversa sobre assiduidade")
                    print("   • Alerta sobre limite de faltas")
            else:
                print("   • Manter acompanhamento normal")
                print("   • Incentivar continuidade do bom desempenho")
            
        except Exception as e:
            self.interface.exibir_mensagem(f"Erro ao exibir detalhes: {e}", tipo="erro")
    
    # ============================================
    # 5. MENU PRINCIPAL
    # ============================================
    
    def menu(self, escola_id):
        """
        Menu interativo do módulo de análise de risco.
        
        Args:
            escola_id (str): ID da escola do administrador logado
        """
        while True:
            self.interface.limpar_tela()
            self.interface.mostrar_titulo("⚠️ FINAX RISK - ANÁLISE DE RISCO")
            
            print("1 - 📊 Relatório Geral de Risco")
            print("2 - 🔍 Ver Detalhes de Aluno")
            print("3 - ⬅️ Voltar ao Menu Principal")
            
            opcao = self.interface.input_com_validação(
                "\nEscolha uma opção",
                obrigatorio=True,
                tipo="numero"
            )
            
            if opcao == "1":
                self.exibir_relatorio_risco(escola_id)
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)
                
            elif opcao == "2":
                self.exibir_detalhes_aluno(escola_id)
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)
                
            elif opcao == "3":
                break
                
            else:
                self.interface.exibir_mensagem("Opção inválida!", tipo="erro")
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)


# ============================================
# FUNÇÃO DE INTEGRAÇÃO PARA O MAIN
# ============================================

def iniciar_analise_risco(escola_id):
    """
    Função de integração para ser chamada pelo main.py
    
    Args:
        escola_id (str): ID da escola do administrador logado
    """
    analisador = AnalisadorRisco()
    analisador.menu(escola_id)


# ============================================
# TESTE DO MÓDULO
# ============================================

if __name__ == "__main__":
    print("🧪 Teste do módulo Analisador de Risco")
    print("⚠️ Para testar, execute o main.py com um administrador logado.")
    print("   Ou utilize: analisador = AnalisadorRisco()")