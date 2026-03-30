"""
MÓDULO AUTH - FINAX OS
Segurança de acesso ao sistema

Funcionalidade:
- Validação de credenciais com verificação de status da conta
- Alteração de senha por utilizador logado
- Recuperação de acesso por administrador (reset de senha)
- Proteção contra força bruta (delay após falhas)
"""

import sys
import os
import time
import hashlib
import secrets
from datetime import datetime

# Adiciona a pasta raiz ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================
# IMPORTAÇÕES DOS MÓDULOS INTERNOS
# ============================================
from modules.database_config import db_config
from utils.interface import Interface

# ============================================
# CONSTANTES
# ============================================

# Status da conta
STATUS_ATIVA = "Ativa"
STATUS_BLOQUEADA = "Bloqueada"

# Mensagens
MSG_ACESSO_AUTORIZADO = "✅ Acesso Autorizado"
MSG_CREDENCIAIS_INVALIDAS = "❌ Credenciais Inválidas"
MSG_CONTA_BLOQUEADA = "⚠️ Conta Bloqueada. Contacte o administrador."
MSG_SENHA_ATUALIZADA = "🔐 Senha atualizada com sucesso!"
MSG_SENHA_CURTA = "A senha deve ter pelo menos 4 caracteres."
MSG_USUARIO_NAO_ENCONTRADO = "Usuário não encontrado."

# Delay após falha de login (segundos) - proteção contra força bruta
DELAY_APOS_FALHA = 1

# Tamanho mínimo da senha
MIN_SENHA_LENGTH = 4


# ============================================
# CLASSE PRINCIPAL DE AUTENTICAÇÃO
# ============================================

class Autenticador:
    """
    Classe responsável pela segurança de acesso ao sistema.
    
    Funcionalidades:
    - Validação de credenciais com verificação de status da conta
    - Alteração de senha por utilizador logado
    - Recuperação de acesso por administrador (reset de senha)
    - Delay após falhas para proteção contra força bruta
    """
    
    def __init__(self):
        """Inicializa o módulo com conexão ao banco de dados"""
        self.supabase = db_config.get_client()
        self.interface = Interface()
    
    # ============================================
    # 1. FUNÇÕES AUXILIARES
    # ============================================
    
    def _hash_senha(self, senha):
        """
        Gera hash simples da senha (para projeto escolar).
        Em produção, usar bcrypt ou argon2.
        
        Args:
            senha (str): Senha em texto plano
        
        Returns:
            str: Hash da senha
        """
        # Usando SHA-256 para simplicidade (projeto escolar)
        return hashlib.sha256(senha.encode()).hexdigest()
    
    def _verificar_senha(self, senha, hash_armazenado):
        """
        Verifica se a senha corresponde ao hash armazenado.
        
        Args:
            senha (str): Senha em texto plano
            hash_armazenado (str): Hash armazenado no banco
        
        Returns:
            bool: True se corresponder
        """
        return self._hash_senha(senha) == hash_armazenado
    
    def _delay_apos_falha(self):
        """
        Adiciona delay após tentativa de login falha.
        Protege contra ataques de força bruta.
        """
        time.sleep(DELAY_APOS_FALHA)
    
    def _gerar_senha_temporaria(self):
        """
        Gera uma senha temporária aleatória.
        
        Returns:
            str: Senha temporária de 8 caracteres
        """
        alfabeto = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        return ''.join(secrets.choice(alfabeto) for _ in range(8))
    
    # ============================================
    # 2. VALIDAR ACESSO (LOGIN)
    # ============================================
    
    def validar_acesso(self, username, password):
        """
        Valida as credenciais de acesso ao sistema.
        
        Args:
            username (str): Nome de utilizador
            password (str): Senha
        
        Returns:
            dict or None: Dados do utilizador se sucesso, None se falha
        """
        # Normalizar username (lowercase e sem espaços)
        username_limpo = username.lower().strip()
        
        if not username_limpo or not password:
            self.interface.exibir_mensagem(MSG_CREDENCIAIS_INVALIDAS, tipo="erro")
            self._delay_apos_falha()
            return None
        
        try:
            # Buscar utilizador no banco
            resultado = self.supabase.table('usuarios')\
                .select('id, username, nome, nivel, status_conta, escola_id, classe, turma, curso, tem_divida')\
                .eq('username', username_limpo)\
                .execute()
            
            # Verificar se utilizador existe
            if not resultado.data or len(resultado.data) == 0:
                self.interface.exibir_mensagem(MSG_CREDENCIAIS_INVALIDAS, tipo="erro")
                self._delay_apos_falha()
                return None
            
            usuario = resultado.data[0]
            
            # Verificar senha
            if not self._verificar_senha(password, usuario.get('password', '')):
                self.interface.exibir_mensagem(MSG_CREDENCIAIS_INVALIDAS, tipo="erro")
                self._delay_apos_falha()
                return None
            
            # Verificar status da conta
            if usuario.get('status_conta') == STATUS_BLOQUEADA:
                self.interface.exibir_mensagem(MSG_CONTA_BLOQUEADA, tipo="erro")
                self._delay_apos_falha()
                return None
            
            # Login bem-sucedido
            self._exibir_sucesso_login(usuario)
            
            # Retornar dados da sessão
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
                "tem_divida": usuario.get('tem_divida', False)
            }
            
        except Exception as e:
            self.interface.exibir_mensagem(f"Erro ao validar acesso: {e}", tipo="erro")
            self._delay_apos_falha()
            return None
    
    def _exibir_sucesso_login(self, usuario):
        """
        Exibe mensagem de sucesso no login.
        
        Args:
            usuario (dict): Dados do utilizador
        """
        nome = usuario.get('nome', 'Utilizador')
        nivel = usuario.get('nivel', '')
        
        print(f"\n{self.interface.cores.VERDE}{self.interface.cores.NEGRITO}")
        print("╔════════════════════════════════════════════════════════════╗")
        print(f"║  ✅ ACESSO AUTORIZADO - {nome.upper()}  ✅")
        print("╚════════════════════════════════════════════════════════════╝")
        print(f"{self.interface.cores.RESET}")
        
        print(f"\n{self.interface.cores.CIANO}📋 DADOS DA SESSÃO{self.interface.cores.RESET}")
        print(f"   Nível: {nivel}")
        print(f"   Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # ============================================
    # 3. ALTERAR SENHA (UTILIZADOR LOGADO)
    # ============================================
    
    def alterar_senha(self, user_id, nova_senha):
        """
        Permite que o utilizador altere a sua própria senha.
        
        Args:
            user_id (str): ID do utilizador
            nova_senha (str): Nova senha
        
        Returns:
            bool: True se sucesso, False caso contrário
        """
        # Validar nova senha
        if len(nova_senha) < MIN_SENHA_LENGTH:
            self.interface.exibir_mensagem(MSG_SENHA_CURTA, tipo="erro")
            return False
        
        try:
            # Gerar hash da nova senha
            hash_nova = self._hash_senha(nova_senha)
            
            # Atualizar no banco
            resultado = self.supabase.table('usuarios')\
                .update({"password": hash_nova})\
                .eq('id', user_id)\
                .execute()
            
            if resultado.data:
                self.interface.mostrar_sucesso(MSG_SENHA_ATUALIZADA)
                return True
            else:
                self.interface.exibir_mensagem("Erro ao atualizar senha.", tipo="erro")
                return False
                
        except Exception as e:
            self.interface.exibir_mensagem(f"Erro ao alterar senha: {e}", tipo="erro")
            return False
    
    # ============================================
    # 4. RECUPERAR ACESSO (ADMIN)
    # ============================================
    
    def recuperar_acesso_admin(self, username_alvo, nova_senha_mestra):
        """
        Função exclusiva para Administradores resetarem a senha de alunos.
        
        Args:
            username_alvo (str): Username do aluno
            nova_senha_mestra (str): Nova senha a ser definida
        
        Returns:
            dict or None: Dados do utilizador resetado
        """
        # Validar nova senha
        if len(nova_senha_mestra) < MIN_SENHA_LENGTH:
            self.interface.exibir_mensagem(MSG_SENHA_CURTA, tipo="erro")
            return None
        
        username_limpo = username_alvo.lower().strip()
        
        try:
            # Buscar utilizador
            resultado = self.supabase.table('usuarios')\
                .select('id, username, nome, nivel')\
                .eq('username', username_limpo)\
                .execute()
            
            if not resultado.data:
                self.interface.exibir_mensagem(MSG_USUARIO_NAO_ENCONTRADO, tipo="erro")
                return None
            
            usuario = resultado.data[0]
            
            # Gerar hash da nova senha
            hash_nova = self._hash_senha(nova_senha_mestra)
            
            # Atualizar senha e desbloquear conta
            resultado_update = self.supabase.table('usuarios')\
                .update({
                    "password": hash_nova,
                    "status_conta": STATUS_ATIVA
                })\
                .eq('id', usuario['id'])\
                .execute()
            
            if resultado_update.data:
                self.interface.mostrar_sucesso(f"Senha de {usuario['nome']} redefinida com sucesso!")
                self.interface.mostrar_info(f"Nova senha: {nova_senha_mestra}")
                return usuario
            else:
                self.interface.exibir_mensagem("Erro ao redefinir senha.", tipo="erro")
                return None
                
        except Exception as e:
            self.interface.exibir_mensagem(f"Erro ao recuperar acesso: {e}", tipo="erro")
            return None
    
    def gerar_senha_temporaria_admin(self, username_alvo):
        """
        Gera uma senha temporária aleatória para o aluno (admin apenas).
        
        Args:
            username_alvo (str): Username do aluno
        
        Returns:
            str or None: Senha temporária gerada
        """
        senha_temp = self._gerar_senha_temporaria()
        if self.recuperar_acesso_admin(username_alvo, senha_temp):
            return senha_temp
        return None
    
    # ============================================
    # 5. BLOQUEAR/DESBLOQUEAR CONTA (ADMIN)
    # ============================================
    
    def alterar_status_conta(self, username_alvo, novo_status):
        """
        Altera o status da conta (Bloquear/Desbloquear).
        
        Args:
            username_alvo (str): Username do utilizador
            novo_status (str): 'Ativa' ou 'Bloqueada'
        
        Returns:
            bool: True se sucesso
        """
        if novo_status not in [STATUS_ATIVA, STATUS_BLOQUEADA]:
            self.interface.exibir_mensagem("Status inválido!", tipo="erro")
            return False
        
        username_limpo = username_alvo.lower().strip()
        
        try:
            resultado = self.supabase.table('usuarios')\
                .update({"status_conta": novo_status})\
                .eq('username', username_limpo)\
                .execute()
            
            if resultado.data:
                self.interface.mostrar_sucesso(f"Conta {username_limpo} agora está {novo_status}.")
                return True
            else:
                self.interface.exibir_mensagem(MSG_USUARIO_NAO_ENCONTRADO, tipo="erro")
                return False
                
        except Exception as e:
            self.interface.exibir_mensagem(f"Erro ao alterar status: {e}", tipo="erro")
            return False
    
    # ============================================
    # 6. MENU INTERATIVO
    # ============================================
    
    def menu_alterar_senha(self, sessao):
        """
        Menu para alteração de senha pelo utilizador logado.
        
        Args:
            sessao (dict): Dados da sessão do utilizador
        """
        self.interface.limpar_tela()
        self.interface.mostrar_titulo("🔐 ALTERAR SENHA")
        
        print(f"\n{self.interface.cores.CIANO}Utilizador: {sessao.get('nome')}{self.interface.cores.RESET}")
        
        nova_senha = self.interface.input_com_validação(
            "Nova senha (mínimo 4 caracteres): ",
            obrigatorio=True,
            mascara=True
        )
        
        confirmar = self.interface.input_com_validação(
            "Confirmar nova senha: ",
            obrigatorio=True,
            mascara=True
        )
        
        if nova_senha != confirmar:
            self.interface.exibir_mensagem("As senhas não coincidem!", tipo="erro")
            return
        
        self.alterar_senha(sessao['id'], nova_senha)
    
    def menu_admin_recuperar(self, escola_id):
        """
        Menu para administrador recuperar senha de alunos.
        
        Args:
            escola_id (str): ID da escola
        """
        self.interface.limpar_tela()
        self.interface.mostrar_titulo("🔑 RECUPERAR ACESSO - ADMIN")
        
        # Listar alunos da escola
        try:
            alunos = self.supabase.table('usuarios')\
                .select('username, nome')\
                .eq('escola_id', escola_id)\
                .eq('nivel', 'Estudante')\
                .execute().data
            
            if not alunos:
                self.interface.mostrar_info("Nenhum aluno encontrado.")
                return
            
            print(f"\n{self.interface.cores.CIANO}ALUNOS CADASTRADOS:{self.interface.cores.RESET}")
            for a in alunos:
                print(f"   • {a['username']} - {a['nome']}")
            
            username = self.interface.input_com_validação(
                "\nUsername do aluno: ",
                obrigatorio=True
            )
            
            print("\n1 - Definir senha personalizada")
            print("2 - Gerar senha temporária")
            
            opcao = self.interface.input_com_validação(
                "Escolha uma opção",
                obrigatorio=True,
                tipo="numero"
            )
            
            if opcao == "1":
                nova_senha = self.interface.input_com_validação(
                    "Nova senha: ",
                    obrigatorio=True,
                    mascara=True
                )
                self.recuperar_acesso_admin(username, nova_senha)
            elif opcao == "2":
                senha_temp = self.gerar_senha_temporaria_admin(username)
                if senha_temp:
                    print(f"\n{self.interface.cores.VERDE}Senha temporária: {senha_temp}{self.interface.cores.RESET}")
            else:
                self.interface.exibir_mensagem("Opção inválida!", tipo="erro")
                
        except Exception as e:
            self.interface.exibir_mensagem(f"Erro: {e}", tipo="erro")


# ============================================
# FUNÇÃO DE INTEGRAÇÃO PARA O MAIN
# ============================================

def iniciar_auth(sessao):
    """
    Função de integração para o menu de autenticação.
    
    Args:
        sessao (dict): Dados da sessão do utilizador logado
    """
    auth = Autenticador()
    
    while True:
        auth.interface.limpar_tela()
        auth.interface.mostrar_titulo("🔐 SEGURANÇA - FINAX OS")
        
        print("\n1 - 🔑 Alterar minha senha")
        if sessao.get('nivel') == 'Administrador':
            print("2 - 🔓 Recuperar senha de aluno")
        print("3 - ⬅️ Voltar")
        
        opcao = auth.interface.input_com_validação(
            "\nEscolha uma opção",
            obrigatorio=True,
            tipo="numero"
        )
        
        if opcao == "1":
            auth.menu_alterar_senha(sessao)
            input("\n" + auth.interface.cores.AMARELO + "Pressione ENTER para continuar..." + auth.interface.cores.RESET)
        elif opcao == "2" and sessao.get('nivel') == 'Administrador':
            auth.menu_admin_recuperar(sessao.get('escola'))
            input("\n" + auth.interface.cores.AMARELO + "Pressione ENTER para continuar..." + auth.interface.cores.RESET)
        elif opcao == "3":
            break
        else:
            auth.interface.exibir_mensagem("Opção inválida!", tipo="erro")


# ============================================
# TESTE DO MÓDULO
# ============================================

if __name__ == "__main__":
    print("🧪 Teste do módulo Autenticador")
    print("⚠️ Para testar, execute o main.py com um utilizador logado.")
    print("   Ou utilize: auth = Autenticador()")
    print("   sessao = auth.validar_acesso('username', 'password')")