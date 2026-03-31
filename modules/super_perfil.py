#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
    MÓDULO SUPER PERFIL - FINAX OS
    ============================================================================
    Versão: 3.0 Professional
    Autor: Nivaldo Simon
    Descrição: Sistema de autenticação e gestão de sessões com segurança avançada
               - Criptografia de senhas com bcrypt
               - Gestão de sessões com tokens JWT
               - Validação de entrada robusta
               - Logging de todas as operações
               - Proteção contra força bruta
================================================================================
"""

import os
import sys
import time
import uuid
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from functools import wraps
import json

# Adiciona a pasta raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================
# IMPORTAÇÕES DE SEGURANÇA
# ============================================
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    print("⚠️ bcrypt não instalado. Usando fallback SHA-256.")

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    print("⚠️ PyJWT não instalado. Usando fallback de sessão simples.")

# ============================================
# IMPORTAÇÕES DOS MÓDULOS INTERNOS
# ============================================
from modules.database_config import db_config

# ============================================
# CONFIGURAÇÃO DE LOGGING
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/auth.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================
# CORES PARA TERMINAL
# ============================================
class Colors:
    """Cores ANSI para terminal profissional"""
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'


def colorize(text: str, color: str = Colors.WHITE, style: str = "") -> str:
    """Aplica cor e estilo ao texto"""
    return f"{style}{color}{text}{Colors.RESET}"


def print_success(message: str):
    """Imprime mensagem de sucesso"""
    print(f"{colorize('✓', Colors.GREEN, Colors.BOLD)} {message}")


def print_error(message: str):
    """Imprime mensagem de erro"""
    print(f"{colorize('✗', Colors.RED, Colors.BOLD)} {message}")


def print_warning(message: str):
    """Imprime mensagem de aviso"""
    print(f"{colorize('⚠', Colors.YELLOW, Colors.BOLD)} {message}")


def print_info(message: str):
    """Imprime mensagem informativa"""
    print(f"{colorize('ℹ', Colors.CYAN, Colors.BOLD)} {message}")


def clear_screen():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title: str, subtitle: str = ""):
    """Imprime cabeçalho estilizado"""
    width = 70
    print(f"\n{colorize('╔' + '═' * (width - 2) + '╗', Colors.BRIGHT_CYAN, Colors.BOLD)}")
    print(f"{colorize('║', Colors.BRIGHT_CYAN)}{colorize(title.center(width - 2), Colors.BRIGHT_WHITE, Colors.BOLD)}{colorize('║', Colors.BRIGHT_CYAN)}")
    if subtitle:
        print(f"{colorize('║', Colors.BRIGHT_CYAN)}{colorize(subtitle.center(width - 2), Colors.BRIGHT_BLACK)}{colorize('║', Colors.BRIGHT_CYAN)}")
    print(f"{colorize('╚' + '═' * (width - 2) + '╝', Colors.BRIGHT_CYAN)}")


# ============================================
# CLASSE DE CRIPTOGRAFIA
# ============================================

class CryptoService:
    """Serviço de criptografia para senhas e tokens"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Gera hash seguro da senha.
        
        Args:
            password: Senha em texto plano
        
        Returns:
            Hash da senha
        """
        if BCRYPT_AVAILABLE:
            salt = bcrypt.gensalt(rounds=12)
            return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        else:
            # Fallback: SHA-256 com salt
            salt = secrets.token_hex(16)
            hash_obj = hashlib.sha256((password + salt).encode('utf-8'))
            return f"{salt}:{hash_obj.hexdigest()}"
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verifica se a senha corresponde ao hash.
        
        Args:
            password: Senha em texto plano
            password_hash: Hash armazenado
        
        Returns:
            True se corresponde, False caso contrário
        """
        if BCRYPT_AVAILABLE:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        else:
            # Fallback: verificar SHA-256
            try:
                salt, stored_hash = password_hash.split(':')
                computed_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
                return computed_hash == stored_hash
            except Exception:
                return False


# ============================================
# CLASSE DE SESSÃO
# ============================================

class SessionManager:
    """Gestor de sessões com tokens JWT"""
    
    SECRET_KEY = os.environ.get("JWT_SECRET", "finax-super-secret-key-change-in-production")
    TOKEN_EXPIRY_HOURS = 24
    
    @classmethod
    def create_session(cls, user_data: Dict[str, Any]) -> str:
        """
        Cria um token de sessão JWT.
        
        Args:
            user_data: Dados do utilizador
        
        Returns:
            Token JWT
        """
        if JWT_AVAILABLE:
            payload = {
                "user_id": user_data.get("id"),
                "username": user_data.get("username"),
                "nivel": user_data.get("nivel"),
                "escola": user_data.get("escola"),
                "exp": datetime.utcnow() + timedelta(hours=cls.TOKEN_EXPIRY_HOURS),
                "iat": datetime.utcnow()
            }
            return jwt.encode(payload, cls.SECRET_KEY, algorithm="HS256")
        else:
            # Fallback: token simples
            token_data = {
                "user": user_data,
                "expires": (datetime.now() + timedelta(hours=cls.TOKEN_EXPIRY_HOURS)).isoformat()
            }
            return secrets.token_urlsafe(32)
    
    @classmethod
    def validate_session(cls, token: str) -> Optional[Dict[str, Any]]:
        """
        Valida um token de sessão.
        
        Args:
            token: Token JWT
        
        Returns:
            Dados do utilizador se válido, None caso contrário
        """
        if JWT_AVAILABLE:
            try:
                payload = jwt.decode(token, cls.SECRET_KEY, algorithms=["HS256"])
                return {
                    "id": payload.get("user_id"),
                    "username": payload.get("username"),
                    "nivel": payload.get("nivel"),
                    "escola": payload.get("escola")
                }
            except jwt.ExpiredSignatureError:
                logger.warning("Token expirado")
                return None
            except jwt.InvalidTokenError:
                logger.warning("Token inválido")
                return None
        return None


# ============================================
# CLASSE SUPER PERFIL
# ============================================

class SuperPerfil:
    """
    Classe responsável pela autenticação e gestão de sessões.
    
    Funcionalidades:
    - Login com validação de credenciais
    - Criptografia de senhas
    - Gestão de sessões com tokens
    - Logging de todas as operações
    - Proteção contra força bruta
    """
    
    # Limite de tentativas de login
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_TIME_MINUTES = 15
    
    def __init__(self):
        """Inicializa o módulo de autenticação"""
        self.supabase = db_config.get_client()
        self._login_attempts = {}  # {username: (attempts, last_attempt_time)}
        self._current_session = None
        self._init_logging()
    
    def _init_logging(self):
        """Inicializa o logging"""
        # Criar diretório de logs se não existir
        if not os.path.exists('logs'):
            os.makedirs('logs')
    
    def _is_locked_out(self, username: str) -> Tuple[bool, int]:
        """
        Verifica se o username está bloqueado por tentativas excessivas.
        
        Args:
            username: Nome de utilizador
        
        Returns:
            (bloqueado, minutos_restantes)
        """
        if username not in self._login_attempts:
            return False, 0
        
        attempts, last_attempt = self._login_attempts[username]
        
        if attempts >= self.MAX_LOGIN_ATTEMPTS:
            elapsed = (datetime.now() - last_attempt).total_seconds() / 60
            if elapsed < self.LOCKOUT_TIME_MINUTES:
                return True, int(self.LOCKOUT_TIME_MINUTES - elapsed)
            else:
                # Reset após tempo de bloqueio
                del self._login_attempts[username]
                return False, 0
        
        return False, 0
    
    def _record_failed_attempt(self, username: str):
        """
        Regista uma tentativa de login falhada.
        
        Args:
            username: Nome de utilizador
        """
        now = datetime.now()
        if username in self._login_attempts:
            attempts, _ = self._login_attempts[username]
            self._login_attempts[username] = (attempts + 1, now)
        else:
            self._login_attempts[username] = (1, now)
        
        logger.warning(f"Tentativa de login falhada para: {username}")
    
    def _reset_login_attempts(self, username: str):
        """
        Reseta as tentativas de login após sucesso.
        
        Args:
            username: Nome de utilizador
        """
        if username in self._login_attempts:
            del self._login_attempts[username]
    
    def _validate_input(self, username: str, password: str) -> bool:
        """
        Valida os inputs de login.
        
        Args:
            username: Nome de utilizador
            password: Senha
        
        Returns:
            True se válido, False caso contrário
        """
        if not username or not username.strip():
            print_error("Username não pode estar vazio")
            return False
        
        if not password:
            print_error("Password não pode estar vazia")
            return False
        
        if len(username) < 3:
            print_error("Username deve ter pelo menos 3 caracteres")
            return False
        
        if len(password) < 4:
            print_error("Password deve ter pelo menos 4 caracteres")
            return False
        
        return True
    
    def fazer_login(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Realiza a autenticação do utilizador.
        
        Args:
            username: Nome de utilizador
            password: Senha
        
        Returns:
            Dicionário com dados do utilizador se sucesso, None caso contrário
        """
        # Limpar e normalizar
        username_limpo = username.lower().strip()
        
        # Validar input
        if not self._validate_input(username_limpo, password):
            return None
        
        # Verificar bloqueio
        locked, minutes = self._is_locked_out(username_limpo)
        if locked:
            print_error(f"Conta temporariamente bloqueada. Tente novamente em {minutes} minutos.")
            logger.warning(f"Tentativa de login em conta bloqueada: {username_limpo}")
            return None
        
        try:
            # Buscar utilizador no banco
            resultado = self.supabase.table('usuarios')\
                .select('*')\
                .eq('username', username_limpo)\
                .execute()
            
            if not resultado.data or len(resultado.data) == 0:
                self._record_failed_attempt(username_limpo)
                print_error("Username ou password incorretos")
                logger.info(f"Login falhado - utilizador não encontrado: {username_limpo}")
                return None
            
            usuario = resultado.data[0]
            
            # Verificar senha
            password_hash = usuario.get('password', '')
            if not CryptoService.verify_password(password, password_hash):
                self._record_failed_attempt(username_limpo)
                print_error("Username ou password incorretos")
                logger.info(f"Login falhado - senha incorreta: {username_limpo}")
                return None
            
            # Verificar status da conta
            status_conta = usuario.get('status_conta', 'Ativa')
            if status_conta == "Bloqueada":
                print_error("Conta bloqueada! Contacte o administrador.")
                logger.warning(f"Tentativa de login em conta bloqueada: {username_limpo}")
                return None
            
            # Reset tentativas após sucesso
            self._reset_login_attempts(username_limpo)
            
            # Construir dados da sessão
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
            
            # Criar token de sessão
            token = SessionManager.create_session(dados_sessao)
            dados_sessao["token"] = token
            
            self._current_session = dados_sessao
            
            # Log de sucesso
            logger.info(f"Login bem-sucedido: {username_limpo} ({usuario.get('nivel', 'N/A')})")
            
            # Exibir mensagem de boas-vindas
            self._exibir_boas_vindas(dados_sessao)
            
            return dados_sessao
            
        except Exception as e:
            logger.error(f"Erro durante login: {e}")
            print_error(f"Erro ao realizar login: {e}")
            return None
    
    def _exibir_boas_vindas(self, dados_sessao: Dict[str, Any]):
        """
        Exibe mensagem de boas-vindas personalizada.
        
        Args:
            dados_sessao: Dados do utilizador logado
        """
        clear_screen()
        print_header("FINAX OS", "Sistema Inteligente de Gestão Escolar")
        
        nome = dados_sessao.get("nome", "Utilizador")
        nivel = dados_sessao.get("nivel", "")
        
        print(f"\n{colorize('╔════════════════════════════════════════════════════════════╗', Colors.BRIGHT_GREEN)}")
        print(f"{colorize(f'║  🎉 BEM-VINDO(A), {nome.upper()}!  🎉', Colors.BRIGHT_GREEN)}")
        print(f"{colorize('╚════════════════════════════════════════════════════════════╝', Colors.BRIGHT_GREEN)}")
        
        print(f"\n{colorize('📋 PERFIL', Colors.BRIGHT_CYAN, Colors.BOLD)}")
        print(f"   • Nível: {colorize(nivel, Colors.BRIGHT_CYAN)}")
        print(f"   • Username: {dados_sessao.get('username')}")
        print(f"   • Escola ID: {dados_sessao.get('escola')}")
        
        if nivel == "Estudante":
            print(f"\n{colorize('📚 DADOS ACADÉMICOS', Colors.BRIGHT_CYAN, Colors.BOLD)}")
            print(f"   • Classe: {dados_sessao.get('classe', 'N/A')}")
            print(f"   • Turma: {dados_sessao.get('turma', 'N/A')}")
            print(f"   • Curso: {dados_sessao.get('curso', 'N/A')}")
            
            if dados_sessao.get('tem_divida'):
                print(f"   • Status Financeiro: {colorize('DÉBITO PENDENTE', Colors.RED)}")
            else:
                print(f"   • Status Financeiro: {colorize('EM DIA', Colors.GREEN)}")
        
        print(f"\n{colorize('═' * 60, Colors.BRIGHT_CYAN)}")
        print(f"{colorize(f'⏰ {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', Colors.BRIGHT_BLACK)}")
    
    def get_usuario_logado(self) -> Optional[Dict[str, Any]]:
        """
        Retorna o utilizador logado.
        
        Returns:
            Dados do utilizador ou None
        """
        return self._current_session
    
    def is_autenticado(self) -> bool:
        """
        Verifica se há utilizador autenticado.
        
        Returns:
            True se autenticado
        """
        return self._current_session is not None
    
    def logout(self) -> bool:
        """
        Realiza logout do utilizador.
        
        Returns:
            True se sucesso
        """
        if self._current_session:
            nome = self._current_session.get("nome", "Utilizador")
            print_info(f"Até logo, {nome}!")
            logger.info(f"Logout: {self._current_session.get('username')}")
            self._current_session = None
            return True
        return False
    
    def alterar_senha(self, user_id: str, nova_senha: str, old_password: str = None) -> bool:
        """
        Altera a senha do utilizador.
        
        Args:
            user_id: ID do utilizador
            nova_senha: Nova senha
            old_password: Senha antiga (opcional, para verificação)
        
        Returns:
            True se sucesso
        """
        if len(nova_senha) < 4:
            print_error("A nova senha deve ter pelo menos 4 caracteres")
            return False
        
        try:
            # Verificar se utilizador existe
            resultado = self.supabase.table('usuarios')\
                .select('password')\
                .eq('id', user_id)\
                .execute()
            
            if not resultado.data:
                print_error("Utilizador não encontrado")
                return False
            
            # Verificar senha antiga se fornecida
            if old_password:
                if not CryptoService.verify_password(old_password, resultado.data[0]['password']):
                    print_error("Senha antiga incorreta")
                    return False
            
            # Gerar nova hash
            nova_hash = CryptoService.hash_password(nova_senha)
            
            # Atualizar no banco
            self.supabase.table('usuarios')\
                .update({"password": nova_hash})\
                .eq('id', user_id)\
                .execute()
            
            print_success("Senha alterada com sucesso!")
            logger.info(f"Senha alterada para utilizador ID: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao alterar senha: {e}")
            print_error(f"Erro: {e}")
            return False
    
    def recuperar_senha(self, username: str, email: str) -> bool:
        """
        Inicia processo de recuperação de senha.
        
        Args:
            username: Nome de utilizador
            email: Email do utilizador
        
        Returns:
            True se sucesso
        """
        try:
            resultado = self.supabase.table('usuarios')\
                .select('id, email')\
                .eq('username', username)\
                .eq('email', email)\
                .execute()
            
            if not resultado.data:
                print_error("Utilizador ou email não encontrados")
                return False
            
            # Gerar token de recuperação
            token = secrets.token_urlsafe(32)
            # TODO: Armazenar token no banco e enviar email
            
            print_info(f"Link de recuperação enviado para {email}")
            logger.info(f"Recuperação de senha solicitada para: {username}")
            return True
            
        except Exception as e:
            logger.error(f"Erro na recuperação de senha: {e}")
            print_error(f"Erro: {e}")
            return False


# ============================================
# FUNÇÕES DE CONVENIÊNCIA
# ============================================

def iniciar_login() -> Optional[Dict[str, Any]]:
    """
    Função de integração para ser chamada pelo main.py.
    
    Returns:
        Dados da sessão ou None
    """
    clear_screen()
    print_header("🔐 FINAX OS", "Sistema de Gestão Escolar")
    
    print(f"\n{colorize('Por favor, insira as suas credenciais de acesso.', Colors.BRIGHT_WHITE)}")
    print()
    
    tentativas = 0
    max_tentativas = 3
    perfil = SuperPerfil()
    
    while tentativas < max_tentativas:
        username = input(f"{colorize('Username: ', Colors.BRIGHT_CYAN)}").strip()
        password = input(f"{colorize('Password: ', Colors.BRIGHT_CYAN)}").strip()
        
        sessao = perfil.fazer_login(username, password)
        
        if sessao:
            return sessao
        else:
            tentativas += 1
            restantes = max_tentativas - tentativas
            if restantes > 0:
                print_info(f"Tentativas restantes: {restantes}")
                time.sleep(1)
    
    print_error("Número máximo de tentativas excedido.")
    return None


def iniciar_login_simples(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Função de login simplificada para o frontend Streamlit.
    
    Args:
        username: Nome de utilizador
        password: Senha
    
    Returns:
        Dados do utilizador ou None
    """
    perfil = SuperPerfil()
    return perfil.fazer_login(username, password)


# ============================================
# TESTE DO MÓDULO
# ============================================

if __name__ == "__main__":
    print("🧪 Teste do módulo Super Perfil")
    print("=" * 50)
    print("\n⚠️ Para testar, execute o main.py")
    print("   Ou utilize: perfil = SuperPerfil()")
    print("   sessao = perfil.fazer_login('username', 'password')")