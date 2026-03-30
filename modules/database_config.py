"""
MÓDULO DATABASE_CONFIG - FINAX OS
Centraliza a conexão com o Supabase

Funcionalidade:
- Conexão única (Singleton) com o Supabase
- Carregamento de credenciais do .env ou variáveis de ambiente
- Tratamento de erros de conexão
- Cliente disponível para todos os módulos
"""

import os
import sys
from supabase import create_client, Client

# ============================================
# CORES SIMPLIFICADAS (para terminal)
# ============================================
class Cores:
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    VERMELHO = '\033[91m'
    AZUL = '\033[94m'
    CIANO = '\033[96m'
    RESET = '\033[0m'
    NEGRITO = '\033[1m'


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


# ============================================
# CLASSE DATABASE CONFIG (SINGLETON)
# ============================================

class DatabaseConfig:
    """
    Classe Singleton para configuração e conexão com o Supabase.
    Garante que apenas uma instância de conexão seja criada.
    """
    
    _instance = None
    _client = None
    _initialized = False
    
    def __new__(cls):
        """Implementação do padrão Singleton"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa a configuração do banco de dados"""
        if self._initialized:
            return
        
        self._initialized = True
        self.url = None
        self.key = None
        self._carregar_credenciais()
        
        if self.url and self.key:
            self._conectar()
        else:
            print(cor_vermelho("❌ Credenciais do Supabase não disponíveis"))
    
    def _carregar_credenciais(self):
        """
        Carrega as credenciais do Supabase.
        
        Ordem de prioridade:
        1. Variáveis de ambiente (os.environ)
        2. Arquivo .env (desenvolvimento local)
        """
        # 1. Tentar de variáveis de ambiente
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_KEY")
        
        if self.url and self.key:
            print(cor_verde("✅ Credenciais carregadas de variáveis de ambiente"))
            return
        
        # 2. Tentar carregar do arquivo .env
        try:
            from dotenv import load_dotenv
            load_dotenv()
            self.url = os.getenv("SUPABASE_URL")
            self.key = os.getenv("SUPABASE_KEY")
            
            if self.url and self.key:
                print(cor_verde("✅ Credenciais carregadas do arquivo .env"))
                return
        except ImportError:
            pass
        except Exception as e:
            print(cor_amarelo(f"⚠️ Erro ao carregar .env: {e}"))
        
        # Se chegou aqui, não encontrou credenciais
        print(cor_vermelho("❌ Credenciais do Supabase não encontradas!"))
        print("   Verifique:")
        print("   1. Se está no Streamlit Cloud, configure os secrets")
        print("   2. Se está localmente, crie um arquivo .env")
        print("   3. Ou defina variáveis de ambiente SUPABASE_URL e SUPABASE_KEY")
    
    def _conectar(self):
        """Estabelece a conexão com o Supabase"""
        try:
            self._client = create_client(self.url, self.key)
            print(cor_verde("🚀 Conectado ao Supabase com sucesso!"))
        except Exception as e:
            print(cor_vermelho(f"❌ Erro ao conectar ao Supabase: {e}"))
            self._client = None
    
    def get_client(self) -> Client:
        """
        Retorna o cliente Supabase ativo.
        
        Returns:
            Client: Cliente Supabase configurado e conectado
        """
        if self._client is None and self.url and self.key:
            self._conectar()
        return self._client
    
    def is_connected(self) -> bool:
        """
        Verifica se a conexão está ativa.
        
        Returns:
            bool: True se conectado, False caso contrário
        """
        return self._client is not None
    
    def get_url(self) -> str:
        """Retorna a URL do Supabase"""
        return self.url
    
    def get_key(self) -> str:
        """Retorna a chave do Supabase"""
        return self.key
    
    def reconectar(self) -> bool:
        """Tenta reconectar ao Supabase"""
        try:
            self._client = None
            self._carregar_credenciais()
            self._conectar()
            return self.is_connected()
        except Exception:
            return False


# ============================================
# INSTÂNCIA GLOBAL (SINGLETON)
# ============================================

# Criação da instância global que será importada pelos outros módulos
try:
    db_config = DatabaseConfig()
except Exception as e:
    print(cor_vermelho(f"❌ Falha ao inicializar DatabaseConfig: {e}"))
    db_config = None


# ============================================
# FUNÇÕES DE CONVENIÊNCIA
# ============================================

def get_supabase_client() -> Client:
    """
    Função de conveniência para obter o cliente Supabase.
    
    Returns:
        Client: Cliente Supabase configurado
    """
    if db_config is None:
        raise RuntimeError("DatabaseConfig não foi inicializado corretamente")
    return db_config.get_client()


def is_connected() -> bool:
    """
    Função de conveniência para verificar conexão.
    
    Returns:
        bool: True se conectado
    """
    if db_config is None:
        return False
    return db_config.is_connected()


# ============================================
# TESTE DO MÓDULO
# ============================================

if __name__ == "__main__":
    print("🧪 Teste do módulo Database Config")
    print("=" * 50)
    
    try:
        # Testar conexão
        config = DatabaseConfig()
        
        if config.is_connected():
            print(f"\n✅ Configuração carregada:")
            print(f"   URL: {config.get_url()}")
            print(f"   Cliente ativo: {config.is_connected()}")
            
            # Testar cliente
            client = config.get_client()
            print(f"   Cliente retornado: {type(client).__name__}")
            print("\n🎉 Configuração concluída com sucesso!")
        else:
            print("\n⚠️ Não foi possível estabelecer conexão")
            print("   Verifique suas credenciais e conexão com a internet")
        
    except Exception as e:
        print(f"\n❌ Erro no teste: {e}")