"""
MÓDULO DASHBOARD ADMIN - FINAX OS
Sistema de gestão escolar com Supabase Cloud

Funcionalidade:
- Visualização completa de todos os alunos da escola
- Exclusivo para Administradores
- Dados apresentados em formato de grelha (grid) com tabulate
"""

import sys
import os

# Adiciona a pasta raiz ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================
# IMPORTAÇÕES DOS MÓDULOS INTERNOS
# ============================================
from modules.database_config import db_config

# ============================================
# IMPORTAÇÕES DE TERCEIROS
# ============================================
from tabulate import tabulate

# ============================================
# CORES SIMPLIFICADAS (SEM DEPENDÊNCIA EXTERNA)
# ============================================
class Cores:
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    VERMELHO = '\033[91m'
    AZUL = '\033[94m'
    CIANO = '\033[96m'
    NEGRITO = '\033[1m'
    RESET = '\033[0m'


def cor_verde(texto):
    return f"{Cores.VERDE}{texto}{Cores.RESET}"

def cor_vermelho(texto):
    return f"{Cores.VERMELHO}{texto}{Cores.RESET}"

def cor_amarelo(texto):
    return f"{Cores.AMARELO}{texto}{Cores.RESET}"

def cor_azul(texto):
    return f"{Cores.AZUL}{texto}{Cores.RESET}"

def cor_ciano(texto):
    return f"{Cores.CIANO}{texto}{Cores.RESET}"


def limpar_tela():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')


def mostrar_titulo(titulo):
    """Mostra título formatado"""
    print(f"\n{cor_azul('='*60)}")
    print(f"{cor_azul(titulo.center(60))}")
    print(f"{cor_azul('='*60)}")


def mostrar_sucesso(mensagem):
    """Mostra mensagem de sucesso"""
    print(f"{cor_verde('✅')} {mensagem}")


def mostrar_erro(mensagem):
    """Mostra mensagem de erro"""
    print(f"{cor_vermelho('❌')} {mensagem}")


def mostrar_info(mensagem):
    """Mostra mensagem informativa"""
    print(f"{cor_ciano('ℹ️')} {mensagem}")


# ============================================
# CONSTANTES
# ============================================

# Colunas a serem exibidas no dashboard
COLUNAS_DASHBOARD = ["NOME", "USER/ID", "CLASSE", "TURMA", "CURSO", "STATUS FINANCEIRO"]


# ============================================
# FUNÇÃO PRINCIPAL DO DASHBOARD
# ============================================

def exibir_dashboard_admin(u_escola):
    """
    Exibe o dashboard administrativo com todos os alunos da escola.
    
    Args:
        u_escola (str): ID da escola do administrador logado
    
    Returns:
        bool: True se executado com sucesso, False em caso de erro
    """
    limpar_tela()
    mostrar_titulo("📊 DASHBOARD ADMIN - FINAX OS")
    mostrar_info(f"Escola ID: {u_escola}")
    mostrar_info("Visualização de todos os alunos da instituição")
    
    try:
        # ============================================
        # 1. CONSULTA AO BANCO DE DADOS
        # ============================================
        print(f"\n{cor_amarelo('⏳ Carregando dados dos alunos...')}")
        
        # Obter cliente do Supabase
        supabase = db_config.get_client()
        
        # Realizar consulta
        resposta = supabase.table('usuarios')\
            .select('username, nome, classe, turma, curso, tem_divida')\
            .eq('escola_id', u_escola)\
            .eq('nivel', 'Estudante')\
            .order('classe', asc=True)\
            .execute()
        
        alunos = resposta.data
        
        # ============================================
        # 2. VERIFICAR SE HÁ DADOS
        # ============================================
        if not alunos:
            mostrar_info("📭 Nenhum aluno encontrado nesta escola.")
            mostrar_info("Utilize o módulo de cadastro para adicionar estudantes.")
            return True
        
        # ============================================
        # 3. PROCESSAR DADOS PARA EXIBIÇÃO
        # ============================================
        mostrar_sucesso(f"{len(alunos)} aluno(s) encontrado(s)")
        
        # Preparar dados para a tabela
        dados_tabela = []
        
        for aluno in alunos:
            # Processar status financeiro com cores
            if aluno['tem_divida']:
                status = f"{Cores.VERMELHO}DÉBITO{Cores.RESET}"
            else:
                status = f"{Cores.VERDE}PAGO{Cores.RESET}"
            
            # Construir linha da tabela
            linha = [
                aluno['nome'],
                aluno['username'],
                aluno.get('classe', 'N/A'),
                aluno.get('turma', 'N/A'),
                aluno.get('curso', 'N/A'),
                status
            ]
            dados_tabela.append(linha)
        
        # ============================================
        # 4. EXIBIR TABELA COM TABULATE
        # ============================================
        print("\n")
        
        # Usar tabulate para gerar a tabela em formato grid
        tabela = tabulate(
            dados_tabela,
            headers=COLUNAS_DASHBOARD,
            tablefmt="grid",
            numalign="left",
            stralign="left"
        )
        
        print(tabela)
        
        # ============================================
        # 5. RODAPÉ COM ESTATÍSTICAS
        # ============================================
        print("\n")
        print(f"{cor_azul('═'*60)}")
        
        # Estatísticas rápidas
        total_alunos = len(alunos)
        alunos_devedores = sum(1 for a in alunos if a['tem_divida'])
        alunos_em_dia = total_alunos - alunos_devedores
        
        mostrar_info("📊 ESTATÍSTICAS:")
        print(f"   • Total de alunos: {cor_ciano(str(total_alunos))}")
        print(f"   • Pagamentos em dia: {cor_verde(str(alunos_em_dia))}")
        print(f"   • Débitos pendentes: {cor_vermelho(str(alunos_devedores))}")
        
        print(f"{cor_azul('═'*60)}")
        mostrar_info("Dashboard atualizado em tempo real.")
        
        return True
        
    except Exception as e:
        # ============================================
        # 6. TRATAMENTO DE ERROS
        # ============================================
        mostrar_erro(f"Erro ao carregar dashboard: {str(e)}")
        mostrar_info("Verifique sua conexão com a internet e tente novamente.")
        return False


# ============================================
# FUNÇÃO DE INTEGRAÇÃO COM MENU PRINCIPAL
# ============================================

def menu_dashboard_admin(u_escola):
    """
    Menu interativo do dashboard administrativo.
    Permite ao administrador visualizar os dados e acessar funcionalidades adicionais.
    
    Args:
        u_escola (str): ID da escola do administrador logado
    """
    while True:
        # Exibir dashboard principal
        exibir_dashboard_admin(u_escola)
        
        # Menu de opções
        print("\n")
        mostrar_titulo("OPÇÕES DO DASHBOARD")
        print("1 - 🔄 Atualizar Dashboard")
        print("2 - 📊 Ver Alunos em Débito")
        print("3 - 📈 Ver Alunos em Dia")
        print("4 - 🏫 Ver Alunos por Turma")
        print("5 - ⬅️ Voltar ao Menu Principal")
        
        opcao = input(f"\n{cor_ciano('👉 Escolha uma opção: ')}").strip()
        
        if opcao == "1":
            continue
            
        elif opcao == "2":
            _exibir_alunos_filtrados(u_escola, tem_divida=True)
            input(f"\n{cor_amarelo('Pressione ENTER para continuar...')}")
            
        elif opcao == "3":
            _exibir_alunos_filtrados(u_escola, tem_divida=False)
            input(f"\n{cor_amarelo('Pressione ENTER para continuar...')}")
            
        elif opcao == "4":
            _exibir_alunos_por_turma(u_escola)
            input(f"\n{cor_amarelo('Pressione ENTER para continuar...')}")
            
        elif opcao == "5":
            break
            
        else:
            mostrar_erro("Opção inválida!")
            input(f"\n{cor_amarelo('Pressione ENTER para continuar...')}")


# ============================================
# FUNÇÕES AUXILIARES (FILTROS)
# ============================================

def _exibir_alunos_filtrados(u_escola, tem_divida):
    """
    Exibe alunos filtrados por status financeiro
    
    Args:
        u_escola (str): ID da escola
        tem_divida (bool): True para débito, False para em dia
    """
    limpar_tela()
    titulo = "ALUNOS COM DÉBITO" if tem_divida else "ALUNOS EM DIA"
    mostrar_titulo(titulo)
    
    supabase = db_config.get_client()
    
    try:
        resposta = supabase.table('usuarios')\
            .select('username, nome, classe, turma, curso, tem_divida')\
            .eq('escola_id', u_escola)\
            .eq('nivel', 'Estudante')\
            .eq('tem_divida', tem_divida)\
            .order('classe', asc=True)\
            .execute()
        
        alunos = resposta.data
        
        if not alunos:
            status = "débito" if tem_divida else "em dia"
            mostrar_info(f"Nenhum aluno com status {status}.")
            return
        
        # Preparar dados
        dados_tabela = []
        for aluno in alunos:
            status_texto = "DÉBITO" if aluno['tem_divida'] else "PAGO"
            status_cor = Cores.VERMELHO if aluno['tem_divida'] else Cores.VERDE
            
            dados_tabela.append([
                aluno['nome'],
                aluno['username'],
                aluno.get('classe', 'N/A'),
                aluno.get('turma', 'N/A'),
                aluno.get('curso', 'N/A'),
                f"{status_cor}{status_texto}{Cores.RESET}"
            ])
        
        tabela = tabulate(
            dados_tabela,
            headers=["NOME", "USER/ID", "CLASSE", "TURMA", "CURSO", "STATUS"],
            tablefmt="grid"
        )
        print(f"\n{tabela}")
        
        print(f"\n{cor_azul('═'*60)}")
        print(f"📊 Total: {len(alunos)} aluno(s)")
        
    except Exception as e:
        mostrar_erro(f"Erro: {str(e)}")


def _exibir_alunos_por_turma(u_escola):
    """
    Exibe alunos agrupados por turma
    
    Args:
        u_escola (str): ID da escola
    """
    limpar_tela()
    mostrar_titulo("ALUNOS POR TURMA")
    
    supabase = db_config.get_client()
    
    try:
        resposta = supabase.table('usuarios')\
            .select('username, nome, classe, turma, curso, tem_divida')\
            .eq('escola_id', u_escola)\
            .eq('nivel', 'Estudante')\
            .order('classe', asc=True)\
            .order('turma', asc=True)\
            .execute()
        
        alunos = resposta.data
        
        if not alunos:
            mostrar_info("Nenhum aluno encontrado.")
            return
        
        # Agrupar por classe + turma
        turmas = {}
        for aluno in alunos:
            chave = f"{aluno.get('classe', 'N/A')} - {aluno.get('turma', 'N/A')}"
            if chave not in turmas:
                turmas[chave] = []
            turmas[chave].append(aluno)
        
        for turma, alunos_turma in turmas.items():
            print(f"\n{cor_azul('='*60)}")
            print(f"{cor_ciano(f'📚 {turma}')}")
            print(f"{cor_azul('='*60)}")
            
            dados = []
            for a in alunos_turma:
                status = "❌ DÉBITO" if a['tem_divida'] else "✅ PAGO"
                status_cor = Cores.VERMELHO if a['tem_divida'] else Cores.VERDE
                dados.append([
                    a['nome'],
                    a['username'],
                    a.get('curso', 'N/A'),
                    f"{status_cor}{status}{Cores.RESET}"
                ])
            
            tabela = tabulate(
                dados,
                headers=["NOME", "USER/ID", "CURSO", "STATUS"],
                tablefmt="simple"
            )
            print(tabela)
            print(f"\nTotal: {len(alunos_turma)} aluno(s)")
        
    except Exception as e:
        mostrar_erro(f"Erro: {str(e)}")


# ============================================
# FUNÇÃO DE INTEGRAÇÃO PARA O MAIN
# ============================================

def iniciar_dashboard(escola_id):
    """
    Função de integração para ser chamada pelo main.py
    
    Args:
        escola_id (str): ID da escola do administrador logado
    """
    menu_dashboard_admin(escola_id)


# ============================================
# TESTE DO MÓDULO
# ============================================

if __name__ == "__main__":
    print("🧪 Teste do módulo Dashboard Admin")
    print("⚠️ Para testar, execute o main.py com um administrador logado.")
    print("   Ou utilize: iniciar_dashboard('ID_DA_ESCOLA_AQUI')")