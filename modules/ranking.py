"""
MÓDULO RANKING - FINAX OS
Sistema de gestão escolar com Supabase Cloud

Funcionalidade:
- Ranking dos melhores alunos por média de notas
- Filtro por escola e opcionalmente por turma
- Medalhas simbólicas para os 3 primeiros colocados
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
# CONSTANTES
# ============================================

# Medalhas para os 3 primeiros colocados
MEDALHAS = {
    1: "🥇",
    2: "🥈",
    3: "🥉"
}

# Número máximo de alunos no ranking principal
TOP_LIMIT = 10


# ============================================
# CLASSE PRINCIPAL DO RANKING
# ============================================

class RankingSistema:
    """
    Classe responsável pela geração do ranking de alunos.
    
    Funcionalidades:
    - Cálculo da média aritmética das 3 notas
    - Ordenação descendente por média
    - Filtro por escola (obrigatório) e turma (opcional)
    - Exibição do Top 10 com medalhas
    """
    
    def __init__(self):
        """Inicializa o módulo com conexão ao banco de dados"""
        self.supabase = db_config.get_client()
        self.interface = Interface()
    
    # ============================================
    # 1. CÁLCULO DA MÉDIA
    # ============================================
    
    def _calcular_media(self, nota_1, nota_2, nota_3):
        """
        Calcula a média aritmética das 3 notas.
        
        Args:
            nota_1 (float): Primeira nota
            nota_2 (float): Segunda nota
            nota_3 (float): Terceira nota
        
        Returns:
            float: Média aritmética (0-20)
        """
        notas = [n for n in [nota_1, nota_2, nota_3] if n is not None and n > 0]
        if not notas:
            return 0.0
        return sum(notas) / len(notas)
    
    # ============================================
    # 2. BUSCAR DADOS DOS ALUNOS
    # ============================================
    
    def _buscar_dados_alunos(self, escola_id, turma=None):
        """
        Busca todos os alunos da escola com suas notas.
        
        Args:
            escola_id (str): ID da escola
            turma (str, optional): Filtro por turma
        
        Returns:
            list: Lista de dicionários com dados dos alunos e suas médias
        """
        try:
            # Construir query base para alunos
            query_alunos = self.supabase.table('usuarios')\
                .select('id, nome, turma, classe')\
                .eq('escola_id', escola_id)\
                .eq('nivel', 'Estudante')
            
            # Aplicar filtro de turma se fornecido
            if turma:
                query_alunos = query_alunos.eq('turma', turma)
            
            alunos = query_alunos.execute().data
            
            if not alunos:
                return []
            
            # Para cada aluno, buscar suas notas
            dados_completos = []
            
            for aluno in alunos:
                # Buscar notas do aluno
                notas_resp = self.supabase.table('notas')\
                    .select('nota_1, nota_2, nota_3')\
                    .eq('aluno_id', aluno['id'])\
                    .execute()
                
                if notas_resp.data:
                    notas = notas_resp.data[0]
                    nota_1 = notas.get('nota_1', 0)
                    nota_2 = notas.get('nota_2', 0)
                    nota_3 = notas.get('nota_3', 0)
                else:
                    nota_1 = nota_2 = nota_3 = 0
                
                # Calcular média
                media = self._calcular_media(nota_1, nota_2, nota_3)
                
                # Nome da turma formatado
                nome_turma = f"{aluno.get('classe', '')} {aluno.get('turma', '')}".strip()
                if not nome_turma:
                    nome_turma = aluno.get('turma', 'N/A')
                
                dados_completos.append({
                    'id': aluno['id'],
                    'nome': aluno['nome'],
                    'turma': nome_turma,
                    'media': media,
                    'nota_1': nota_1,
                    'nota_2': nota_2,
                    'nota_3': nota_3
                })
            
            # Ordenar por média (decrescente)
            dados_completos.sort(key=lambda x: x['media'], reverse=True)
            
            return dados_completos
            
        except Exception as e:
            self.interface.exibir_mensagem(f"Erro ao buscar dados: {e}", tipo="erro")
            return []
    
    # ============================================
    # 3. EXIBIR TOP 10
    # ============================================
    
    def exibir_top_10(self, escola_id, turma=None):
        """
        Exibe os 10 melhores alunos da escola ou turma.
        
        Args:
            escola_id (str): ID da escola
            turma (str, optional): Filtro por turma
        """
        self.interface.limpar_tela()
        
        # Título conforme filtro
        if turma:
            self.interface.mostrar_titulo(f"🏆 RANKING FINAX - TOP {TOP_LIMIT} - TURMA {turma.upper()}")
        else:
            self.interface.mostrar_titulo(f"🏆 RANKING FINAX - TOP {TOP_LIMIT} DA ESCOLA")
        
        try:
            # Buscar dados dos alunos
            self.interface.mostrar_processando("Calculando médias e gerando ranking...")
            alunos = self._buscar_dados_alunos(escola_id, turma)
            
            if not alunos:
                self.interface.exibir_mensagem(
                    "Nenhum aluno encontrado para gerar o ranking.",
                    tipo="info"
                )
                return
            
            # Selecionar apenas os TOP_LIMIT melhores
            top_alunos = alunos[:TOP_LIMIT]
            
            # Preparar dados para a tabela
            dados_tabela = []
            
            for posicao, aluno in enumerate(top_alunos, 1):
                # Definir medalha ou emoji para a posição
                if posicao in MEDALHAS:
                    posicao_display = f"{MEDALHAS[posicao]} {posicao}º"
                else:
                    posicao_display = f"{posicao}º"
                
                # Cor para a média (verde se >= 14, amarelo se >= 10, vermelho se < 10)
                if aluno['media'] >= 14:
                    media_cor = self.interface.cores.VERDE
                elif aluno['media'] >= 10:
                    media_cor = self.interface.cores.AMARELO
                else:
                    media_cor = self.interface.cores.VERMELHO
                
                # Formatar média com 1 casa decimal
                media_formatada = f"{media_cor}{aluno['media']:.1f}{self.interface.cores.RESET}"
                
                # Nome com destaque para o primeiro lugar
                if posicao == 1:
                    nome_display = f"{self.interface.cores.CIANO}{self.interface.cores.NEGRITO}{aluno['nome']}{self.interface.cores.RESET}"
                else:
                    nome_display = aluno['nome']
                
                dados_tabela.append([
                    posicao_display,
                    nome_display,
                    aluno['turma'],
                    media_formatada
                ])
            
            # Exibir tabela
            print("\n")
            tabela = tabulate(
                dados_tabela,
                headers=["POSIÇÃO", "NOME", "TURMA", "MÉDIA FINAL"],
                tablefmt="grid"
            )
            print(tabela)
            
            # ============================================
            # 3.1 ESTATÍSTICAS ADICIONAIS
            # ============================================
            print(f"\n{self.interface.cores.AZUL}{'═'*60}{self.interface.cores.RESET}")
            print(f"{self.interface.cores.AZUL}📊 ESTATÍSTICAS DO RANKING{self.interface.cores.RESET}")
            print(f"   • Total de alunos analisados: {len(alunos)}")
            print(f"   • Melhor média: {self.interface.cores.VERDE}{top_alunos[0]['media']:.1f}{self.interface.cores.RESET} ({top_alunos[0]['nome']})")
            print(f"   • Média do Top 10: {self._calcular_media_top(top_alunos):.1f}")
            print(f"   • Média geral da turma: {self._calcular_media_geral(alunos):.1f}")
            
            # Mostrar alunos que ficaram perto do Top 10
            if len(alunos) > TOP_LIMIT:
                proximo = alunos[TOP_LIMIT] if len(alunos) > TOP_LIMIT else None
                if proximo:
                    diferenca = top_alunos[-1]['media'] - proximo['media']
                    print(f"\n{self.interface.cores.AMARELO}📌 Na porta do pódio: {proximo['nome']} ({proximo['media']:.1f}) - diferença de {diferenca:.1f} pontos{self.interface.cores.RESET}")
            
        except Exception as e:
            self.interface.exibir_mensagem(f"Erro ao gerar ranking: {e}", tipo="erro")
    
    # ============================================
    # 4. FUNÇÕES AUXILIARES DE ESTATÍSTICAS
    # ============================================
    
    def _calcular_media_top(self, top_alunos):
        """
        Calcula a média dos alunos do Top 10.
        
        Args:
            top_alunos (list): Lista dos top alunos
        
        Returns:
            float: Média das médias
        """
        if not top_alunos:
            return 0.0
        medias = [a['media'] for a in top_alunos]
        return sum(medias) / len(medias)
    
    def _calcular_media_geral(self, alunos):
        """
        Calcula a média geral de todos os alunos.
        
        Args:
            alunos (list): Lista de todos os alunos
        
        Returns:
            float: Média geral
        """
        if not alunos:
            return 0.0
        medias = [a['media'] for a in alunos]
        return sum(medias) / len(medias)
    
    # ============================================
    # 5. RELATÓRIO COMPLETO DO RANKING
    # ============================================
    
    def exibir_ranking_completo(self, escola_id, turma=None):
        """
        Exibe o ranking completo de todos os alunos (não apenas Top 10).
        
        Args:
            escola_id (str): ID da escola
            turma (str, optional): Filtro por turma
        """
        self.interface.limpar_tela()
        
        if turma:
            self.interface.mostrar_titulo(f"🏆 RANKING COMPLETO - TURMA {turma.upper()}")
        else:
            self.interface.mostrar_titulo("🏆 RANKING COMPLETO - TODA A ESCOLA")
        
        try:
            alunos = self._buscar_dados_alunos(escola_id, turma)
            
            if not alunos:
                self.interface.exibir_mensagem(
                    "Nenhum aluno encontrado para gerar o ranking.",
                    tipo="info"
                )
                return
            
            # Preparar dados para a tabela
            dados_tabela = []
            
            for posicao, aluno in enumerate(alunos, 1):
                # Definir medalha para os 3 primeiros
                if posicao in MEDALHAS:
                    posicao_display = f"{MEDALHAS[posicao]} {posicao}º"
                else:
                    posicao_display = f"{posicao}º"
                
                # Cor para a média
                if aluno['media'] >= 14:
                    media_cor = self.interface.cores.VERDE
                elif aluno['media'] >= 10:
                    media_cor = self.interface.cores.AMARELO
                else:
                    media_cor = self.interface.cores.VERMELHO
                
                media_formatada = f"{media_cor}{aluno['media']:.1f}{self.interface.cores.RESET}"
                
                dados_tabela.append([
                    posicao_display,
                    aluno['nome'],
                    aluno['turma'],
                    media_formatada
                ])
            
            # Exibir tabela
            print("\n")
            tabela = tabulate(
                dados_tabela,
                headers=["POSIÇÃO", "NOME", "TURMA", "MÉDIA FINAL"],
                tablefmt="grid"
            )
            print(tabela)
            
            # Resumo
            print(f"\n{self.interface.cores.AZUL}{'═'*60}{self.interface.cores.RESET}")
            print(f"📊 Total de alunos no ranking: {len(alunos)}")
            print(f"🏅 Alunos com média >= 14: {len([a for a in alunos if a['media'] >= 14])}")
            print(f"📈 Alunos com média >= 10: {len([a for a in alunos if a['media'] >= 10])}")
            print(f"⚠️ Alunos em risco (média < 10): {len([a for a in alunos if a['media'] < 10])}")
            
        except Exception as e:
            self.interface.exibir_mensagem(f"Erro ao gerar ranking: {e}", tipo="erro")
    
    # ============================================
    # 6. MENU PRINCIPAL
    # ============================================
    
    def menu(self, escola_id):
        """
        Menu interativo do módulo de ranking.
        
        Args:
            escola_id (str): ID da escola do administrador logado
        """
        while True:
            self.interface.limpar_tela()
            self.interface.mostrar_titulo("🏆 FINAX RANKING - CLASSIFICAÇÃO DE ALUNOS")
            
            print("1 - 📊 Top 10 da Escola")
            print("2 - 🏫 Top 10 por Turma")
            print("3 - 📋 Ranking Completo da Escola")
            print("4 - 🏘️ Ranking Completo por Turma")
            print("5 - ⬅️ Voltar ao Menu Principal")
            
            opcao = self.interface.input_com_validação(
                "\nEscolha uma opção",
                obrigatorio=True,
                tipo="numero"
            )
            
            if opcao == "1":
                self.exibir_top_10(escola_id)
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)
                
            elif opcao == "2":
                turma = self.interface.input_com_validação(
                    "Digite o nome da turma (ex: A, B, C): ",
                    obrigatorio=True
                )
                self.exibir_top_10(escola_id, turma)
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)
                
            elif opcao == "3":
                self.exibir_ranking_completo(escola_id)
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)
                
            elif opcao == "4":
                turma = self.interface.input_com_validação(
                    "Digite o nome da turma (ex: A, B, C): ",
                    obrigatorio=True
                )
                self.exibir_ranking_completo(escola_id, turma)
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)
                
            elif opcao == "5":
                break
                
            else:
                self.interface.exibir_mensagem("Opção inválida!", tipo="erro")
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)


# ============================================
# FUNÇÃO DE INTEGRAÇÃO PARA O MAIN
# ============================================

def iniciar_ranking(escola_id):
    """
    Função de integração para ser chamada pelo main.py
    
    Args:
        escola_id (str): ID da escola do administrador logado
    """
    ranking = RankingSistema()
    ranking.menu(escola_id)


# ============================================
# TESTE DO MÓDULO
# ============================================

if __name__ == "__main__":
    print("🧪 Teste do módulo Ranking")
    print("⚠️ Para testar, execute o main.py com um administrador logado.")
    print("   Ou utilize: ranking = RankingSistema()")
    print("   ranking.exibir_top_10('ESC_001')")