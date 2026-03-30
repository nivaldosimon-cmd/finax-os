"""
MÓDULO SUPER PERFIL - FINAX OS
Sistema de gestão escolar com Supabase Cloud

Funcionalidade:
- Autenticação de utilizadores (login)
- Carregamento de sessão com dados completos
- Gestão de perfis (Estudante / Administrador)
"""

import sys
import os
import time

# Adiciona a pasta raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================
# IMPORTAÇÕES
# ============================================
from modules.database_config import db_config

# ============================================
# CORES SIMPLIFICADAS
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
    print(f"\n{cor_azul('='*50)}")
    print(f"{cor_azul(titulo)}")
    print(f"{cor_azul('='*50)}")


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
# CLASSE SUPER PERFIL
# ============================================

class SuperPerfil:
    """
    Classe responsável pela autenticação e carregamento de sessão.
    """
    
    def __init__(self):
        """Inicializa o módulo com conexão ao banco de dados"""
        self.supabase = db_config.get_client()
        self.usuario_logado = None
    
    def fazer_login(self, username, password):
        """
        Realiza a autenticação do utilizador.
        
        Args:
            username (str): Nome de utilizador
            password (str): Senha
        
        Returns:
            dict or None: Dicionário com dados do utilizador
        """
        username_limpo = username.lower().strip()
        
        if not username_limpo or not password:
            mostrar_erro("Username e password são obrigatórios!")
            return None
        
        try:
            # Buscar utilizador
            resultado = self.supabase.table('usuarios')\
                .select('*')\
                .eq('username', username_limpo)\
                .eq('password', password)\
                .execute()
            
            if not resultado.data or len(resultado.data) == 0:
                mostrar_erro("Username ou password incorretos!")
                return None
            
            usuario = resultado.data[0]
            
            # Verificar status da conta
            if usuario.get('status_conta') == "Bloqueada":
                mostrar_erro("Conta bloqueada! Contacte o administrador.")
                return None
            
            # Dados da sessão
            dados_sessao = {
                "id": usuario.get("id"),
                "nome": usuario.get("nome"),
                "username": usuario.get("username"),
                "nivel": usuario.get("nivel"),
                "escola": usuario.get("escola_id"),
                "classe": usuario.get("classe", "N/A"),
                "turma": usuario.get("turma", "N/A"),
                "curso": usuario.get("curso", "N/A"),
                "tem_divida": usuario.get("tem_divida", False),
                "status_conta": usuario.get("status_conta", "Ativa"),
                "email": usuario.get("email", ""),
                "telefone": usuario.get("telefone", "")
            }
            
            self.usuario_logado = dados_sessao
            self._exibir_boas_vindas(dados_sessao)
            
            return dados_sessao
            
        except Exception as e:
            mostrar_erro(f"Erro ao realizar login: {e}")
            return None
    
    def _exibir_boas_vindas(self, dados_sessao):
        """Exibe mensagem de boas-vindas"""
        nome = dados_sessao.get("nome", "Utilizador")
        nivel = dados_sessao.get("nivel", "")
        
        limpar_tela()
        mostrar_titulo("FINAX OS - SISTEMA DE GESTÃO ESCOLAR")
        
        print(f"\n{cor_verde('╔════════════════════════════════════════════════════════════╗')}")
        print(f"{cor_verde(f'║  🎉 BEM-VINDO(A), {nome.upper()}!  🎉')}")
        print(f"{cor_verde('╚════════════════════════════════════════════════════════════╝')}")
        
        print(f"\n{cor_azul('📋 PERFIL')}")
        print(f"   • Nível: {cor_ciano(nivel)}")
        print(f"   • Username: {dados_sessao.get('username')}")
        print(f"   • Escola ID: {dados_sessao.get('escola')}")
        
        if nivel == "Estudante":
            print(f"\n{cor_azul('📚 DADOS ACADÉMICOS')}")
            print(f"   • Classe: {dados_sessao.get('classe', 'N/A')}")
            print(f"   • Turma: {dados_sessao.get('turma', 'N/A')}")
            print(f"   • Curso: {dados_sessao.get('curso', 'N/A')}")
            
            if dados_sessao.get('tem_divida'):
                print(f"   • Status Financeiro: {cor_vermelho('DÉBITO PENDENTE')}")
            else:
                print(f"   • Status Financeiro: {cor_verde('EM DIA')}")
        
        print(f"\n{cor_azul('═'*60)}")
        from datetime import datetime
        print(f"{cor_amarelo(f'⏰ {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')}")
    
    def get_usuario_logado(self):
        """Retorna o utilizador logado"""
        return self.usuario_logado
    
    def is_autenticado(self):
        """Verifica se há utilizador autenticado"""
        return self.usuario_logado is not None
    
    def logout(self):
        """Realiza logout"""
        if self.usuario_logado:
            nome = self.usuario_logado.get("nome", "Utilizador")
            mostrar_info(f"Até logo, {nome}!")
            self.usuario_logado = None


# ============================================
# FUNÇÃO DE LOGIN PARA O TERMINAL
# ============================================

def iniciar_login():
    """
    Função de integração para ser chamada pelo main.py (terminal).
    
    Returns:
        dict or None: Dados da sessão se login bem-sucedido
    """
    limpar_tela()
    mostrar_titulo("🔐 FINAX OS - LOGIN")
    
    print(f"\n{cor_ciano('Por favor, insira as suas credenciais de acesso.')}")
    print()
    
    tentativas = 0
    max_tentativas = 3
    perfil = SuperPerfil()
    
    while tentativas < max_tentativas:
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        
        sessao = perfil.fazer_login(username, password)
        
        if sessao:
            return sessao
        else:
            tentativas += 1
            restantes = max_tentativas - tentativas
            if restantes > 0:
                mostrar_info(f"Tentativas restantes: {restantes}")
                time.sleep(1)
    
    mostrar_erro("Número máximo de tentativas excedido.")
    return None


# ============================================
# FUNÇÃO DE LOGIN SIMPLES PARA O FRONTEND (STREAMLIT)
# ============================================

def iniciar_login_simples(username, password):
    """
    Função de login simplificada para ser usada pelo frontend Streamlit.
    
    Args:
        username (str): Nome de utilizador
        password (str): Senha
    
    Returns:
        dict or None: Dados do utilizador se sucesso, None se falha
    """
    try:
        supabase = db_config.get_client()
        
        resultado = supabase.table('usuarios')\
            .select('*')\
            .eq('username', username.lower())\
            .eq('password', password)\
            .execute()
        
        if not resultado.data:
            return None
        
        usuario = resultado.data[0]
        
        return {
            "id": usuario.get('id'),
            "username": usuario.get('username'),
            "nome": usuario.get('nome'),
            "nivel": usuario.get('nivel'),
            "escola": usuario.get('escola_id'),
            "status_conta": usuario.get('status_conta'),
            "classe": usuario.get('classe', 'N/A'),
            "turma": usuario.get('turma', 'N/A'),
            "curso": usuario.get('curso', 'N/A'),
            "tem_divida": usuario.get('tem_divida', False),
            "email": usuario.get('email', ''),
            "telefone": usuario.get('telefone', '')
        }
    except Exception as e:
        print(f"Erro ao fazer login: {e}")
        return None


# ============================================
# TESTE DO MÓDULO
# ============================================

if __name__ == "__main__":
    print("🧪 Teste do módulo Super Perfil")
    print("⚠️ Para testar, execute o main.py")
    print("   Ou utilize: perfil = SuperPerfil()")
    print("   sessao = perfil.fazer_login('username', 'password')")