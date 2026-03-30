#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
    FINAX OS - SISTEMA DE GESTÃO ESCOLAR
    ============================================================================
    Versão: 2.0 Professional
    Autor: Nivaldo Simon
    Descrição: Sistema completo de gestão escolar com interface de terminal
               moderna, cores e funcionalidades avançadas.
    Módulos: Cadastro, Presenças, Notas, Ranking, Financeiro, Biblioteca, etc.
================================================================================
"""

import os
import sys
import time
import uuid
import getpass
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any

# ============================================================================
# CONFIGURAÇÃO DE CORES (ANSI)
# ============================================================================

class Colors:
    """Cores ANSI para terminal moderno"""
    # Cores básicas
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Cores brilhantes
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Estilos
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    
    # Fundos
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # Reset
    RESET = '\033[0m'
    
    @classmethod
    def colorize(cls, text: str, color: str = WHITE, style: str = "") -> str:
        """Aplica cor e estilo ao texto"""
        return f"{style}{color}{text}{cls.RESET}"


# ============================================================================
# UTILITÁRIOS DE INTERFACE
# ============================================================================

def clear_screen():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title: str, subtitle: str = ""):
    """Imprime cabeçalho estilizado"""
    width = 70
    print(f"\n{Colors.colorize('╔' + '═' * (width - 2) + '╗', Colors.BRIGHT_CYAN, Colors.BOLD)}")
    print(f"{Colors.colorize('║', Colors.BRIGHT_CYAN)}{Colors.colorize(title.center(width - 2), Colors.BRIGHT_WHITE, Colors.BOLD)}{Colors.colorize('║', Colors.BRIGHT_CYAN)}")
    if subtitle:
        print(f"{Colors.colorize('║', Colors.BRIGHT_CYAN)}{Colors.colorize(subtitle.center(width - 2), Colors.BRIGHT_BLACK)}{Colors.colorize('║', Colors.BRIGHT_CYAN)}")
    print(f"{Colors.colorize('╚' + '═' * (width - 2) + '╝', Colors.BRIGHT_CYAN)}")


def print_success(message: str):
    """Imprime mensagem de sucesso"""
    print(f"{Colors.colorize('✓', Colors.GREEN, Colors.BOLD)} {message}")


def print_error(message: str):
    """Imprime mensagem de erro"""
    print(f"{Colors.colorize('✗', Colors.RED, Colors.BOLD)} {message}")


def print_warning(message: str):
    """Imprime mensagem de aviso"""
    print(f"{Colors.colorize('⚠', Colors.YELLOW, Colors.BOLD)} {message}")


def print_info(message: str):
    """Imprime mensagem informativa"""
    print(f"{Colors.colorize('ℹ', Colors.CYAN, Colors.BOLD)} {message}")


def print_separator(char: str = "─", length: int = 70):
    """Imprime linha separadora"""
    print(Colors.colorize(char * length, Colors.BRIGHT_BLACK))


def input_with_validation(prompt: str, required: bool = True, input_type: str = "text", 
                          min_value: float = None, max_value: float = None) -> Optional[str]:
    """
    Input com validação
    
    Args:
        prompt: Texto do prompt
        required: Se o campo é obrigatório
        input_type: 'text', 'number', 'email', 'phone'
        min_value: Valor mínimo (para numbers)
        max_value: Valor máximo (para numbers)
    """
    while True:
        value = input(f"{Colors.colorize(prompt, Colors.BRIGHT_CYAN)}").strip()
        
        if not value and not required:
            return None
        
        if not value and required:
            print_error("Este campo é obrigatório!")
            continue
        
        if input_type == "number":
            try:
                num = float(value)
                if min_value is not None and num < min_value:
                    print_error(f"Valor mínimo: {min_value}")
                    continue
                if max_value is not None and num > max_value:
                    print_error(f"Valor máximo: {max_value}")
                    continue
                return str(num)
            except ValueError:
                print_error("Digite um número válido!")
                continue
        
        if input_type == "email":
            if '@' not in value or '.' not in value:
                print_error("Email inválido!")
                continue
        
        if input_type == "phone":
            if not value.isdigit() or len(value) < 9:
                print_error("Telefone inválido! Use apenas números (9 dígitos)")
                continue
        
        return value


def confirm_action(message: str) -> bool:
    """Confirma uma ação"""
    response = input(f"{Colors.colorize(message, Colors.YELLOW)} (s/n): ").lower()
    return response == 's'


def wait_for_enter():
    """Aguarda o usuário pressionar ENTER"""
    input(f"\n{Colors.colorize('Pressione ENTER para continuar...', Colors.BRIGHT_BLACK)}")


# ============================================================================
# SISTEMA DE LOGIN
# ============================================================================

class AuthSystem:
    """Sistema de autenticação"""
    
    def __init__(self):
        self.supabase = None
        self._init_supabase()
    
    def _init_supabase(self):
        """Inicializa conexão com Supabase"""
        try:
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from modules.database_config import db_config
            self.supabase = db_config.get_client()
        except Exception as e:
            print_error(f"Erro ao conectar ao Supabase: {e}")
            sys.exit(1)
    
    def login(self) -> Optional[Dict]:
        """Realiza login do usuário"""
        clear_screen()
        print_header("🔐 FINAX OS", "Sistema de Gestão Escolar")
        
        print(f"\n{Colors.colorize('Bem-vindo! Por favor, insira suas credenciais.', Colors.BRIGHT_WHITE)}")
        print()
        
        attempts = 0
        max_attempts = 3
        
        while attempts < max_attempts:
            username = input_with_validation("Username: ", required=True)
            password = getpass.getpass(f"{Colors.colorize('Password: ', Colors.BRIGHT_CYAN)}")
            
            try:
                result = self.supabase.table('usuarios')\
                    .select('*')\
                    .eq('username', username.lower())\
                    .eq('password', password)\
                    .execute()
                
                if result.data:
                    user = result.data[0]
                    
                    if user.get('status_conta') == "Bloqueada":
                        print_error("Conta bloqueada! Contacte o administrador.")
                        attempts += 1
                        continue
                    
                    print_success(f"Bem-vindo, {user['nome']}!")
                    time.sleep(1)
                    
                    return {
                        "id": user.get('id'),
                        "nome": user.get('nome'),
                        "username": user.get('username'),
                        "nivel": user.get('nivel'),
                        "escola": user.get('escola_id'),
                        "classe": user.get('classe', 'N/A'),
                        "turma": user.get('turma', 'N/A'),
                        "curso": user.get('curso', 'N/A'),
                        "tem_divida": user.get('tem_divida', False),
                        "email": user.get('email', ''),
                        "telefone": user.get('telefone', '')
                    }
                else:
                    attempts += 1
                    remaining = max_attempts - attempts
                    print_error(f"Credenciais inválidas. Tentativas restantes: {remaining}")
                    time.sleep(1)
                    
            except Exception as e:
                print_error(f"Erro: {e}")
                attempts += 1
        
        print_error("Número máximo de tentativas excedido.")
        return None
    
    def signup(self) -> Optional[Dict]:
        """Cria nova conta"""
        clear_screen()
        print_header("📝 Criar Nova Conta", "Junte-se ao FinaX OS")
        
        print(f"\n{Colors.colorize('1 - Sou Administrador (Criar Escola)', Colors.BRIGHT_WHITE)}")
        print(f"{Colors.colorize('2 - Sou Estudante (Juntar-me a uma Escola)', Colors.BRIGHT_WHITE)}")
        print(f"{Colors.colorize('0 - Voltar', Colors.BRIGHT_BLACK)}")
        
        option = input_with_validation("\nEscolha: ", required=True, input_type="number")
        
        if option == "0":
            return None
        elif option == "1":
            return self._signup_admin()
        elif option == "2":
            return self._signup_student()
        else:
            print_error("Opção inválida!")
            return None
    
    def _signup_admin(self) -> Optional[Dict]:
        """Cadastro de administrador e escola"""
        clear_screen()
        print_header("🏫 Cadastro de Administrador / Escola")
        
        print(f"\n{Colors.colorize('DADOS DA ESCOLA', Colors.BRIGHT_CYAN, Colors.BOLD)}")
        print_separator()
        
        escola_nome = input_with_validation("Nome da Escola: ", required=True)
        escola_endereco = input_with_validation("Endereço: ", required=True)
        escola_telefone = input_with_validation("Telefone: ", required=True, input_type="phone")
        escola_email = input_with_validation("Email da Escola: ", required=True, input_type="email")
        
        print(f"\n{Colors.colorize('DADOS DO ADMINISTRADOR', Colors.BRIGHT_CYAN, Colors.BOLD)}")
        print_separator()
        
        nome = input_with_validation("Nome completo: ", required=True)
        username = input_with_validation("Username: ", required=True)
        password = getpass.getpass(f"{Colors.colorize('Password: ', Colors.BRIGHT_CYAN)}")
        email = input_with_validation("Email: ", required=True, input_type="email")
        telefone = input_with_validation("Telefone: ", required=True, input_type="phone")
        
        # Confirmar
        print(f"\n{Colors.colorize('CONFIRMAÇÃO', Colors.BRIGHT_YELLOW, Colors.BOLD)}")
        print_separator()
        print(f"Escola: {escola_nome}")
        print(f"Administrador: {nome}")
        print(f"Username: {username}")
        
        if not confirm_action("\nConfirmar criação da conta?"):
            print_info("Cadastro cancelado.")
            return None
        
        try:
            escola_id = f"ESC_{uuid.uuid4().hex[:8].upper()}"
            admin_id = str(uuid.uuid4())
            
            dados_admin = {
                "id": admin_id,
                "username": username.lower(),
                "password": password,
                "nivel": "Administrador",
                "nome": nome,
                "escola_id": escola_id,
                "classe": "DIREÇÃO",
                "turma": "GERAL",
                "curso": "ADMINISTRAÇÃO",
                "tem_divida": False,
                "status_conta": "Ativa",
                "email": email,
                "telefone": telefone
            }
            
            self.supabase.table('usuarios').insert(dados_admin).execute()
            
            print_success("Conta criada com sucesso!")
            print_info(f"ID da Escola: {Colors.colorize(escola_id, Colors.BRIGHT_GREEN)}")
            print_info(f"Username: {Colors.colorize(username, Colors.BRIGHT_GREEN)}")
            print_warning("Guarde estas informações!")
            
            wait_for_enter()
            
            return {
                "id": admin_id,
                "nome": nome,
                "username": username.lower(),
                "nivel": "Administrador",
                "escola": escola_id,
                "classe": "DIREÇÃO",
                "turma": "GERAL",
                "curso": "ADMINISTRAÇÃO",
                "tem_divida": False,
                "email": email,
                "telefone": telefone
            }
            
        except Exception as e:
            print_error(f"Erro ao criar conta: {e}")
            return None
    
    def _signup_student(self) -> Optional[Dict]:
        """Cadastro de estudante"""
        clear_screen()
        print_header("🎓 Cadastro de Estudante")
        
        print(f"\n{Colors.colorize('Para se juntar a uma escola, precisa do ID fornecido pelo administrador.', Colors.BRIGHT_WHITE)}")
        print()
        
        escola_id = input_with_validation("ID da Escola: ", required=True)
        
        # Verificar se escola existe
        try:
            escola_existe = self.supabase.table('usuarios')\
                .select('escola_id')\
                .eq('escola_id', escola_id)\
                .limit(1)\
                .execute()
            
            if not escola_existe.data:
                print_error("Escola não encontrada!")
                return None
            
            print(f"\n{Colors.colorize('DADOS PESSOAIS', Colors.BRIGHT_CYAN, Colors.BOLD)}")
            print_separator()
            
            nome = input_with_validation("Nome completo: ", required=True)
            username = input_with_validation("Username: ", required=True)
            password = getpass.getpass(f"{Colors.colorize('Password: ', Colors.BRIGHT_CYAN)}")
            email = input_with_validation("Email: ", required=True, input_type="email")
            telefone = input_with_validation("Telefone: ", required=True, input_type="phone")
            
            print(f"\n{Colors.colorize('DADOS ACADÉMICOS', Colors.BRIGHT_CYAN, Colors.BOLD)}")
            print_separator()
            
            classe = input_with_validation("Classe (ex: 10ª, 11ª, 12ª): ", required=True)
            turma = input_with_validation("Turma (ex: A, B, C): ", required=True)
            curso = input_with_validation("Curso (ex: Ciências, Humanidades): ", required=True)
            
            # Confirmar
            print(f"\n{Colors.colorize('CONFIRMAÇÃO', Colors.BRIGHT_YELLOW, Colors.BOLD)}")
            print_separator()
            print(f"Escola ID: {escola_id}")
            print(f"Nome: {nome}")
            print(f"Username: {username}")
            print(f"Classe/Turma: {classe}/{turma}")
            
            if not confirm_action("\nConfirmar cadastro?"):
                print_info("Cadastro cancelado.")
                return None
            
            # Verificar se username já existe
            existe = self.supabase.table('usuarios').select('id').eq('username', username.lower()).execute()
            if existe.data:
                print_error("Username já existe!")
                return None
            
            estudante_id = str(uuid.uuid4())
            dados_estudante = {
                "id": estudante_id,
                "username": username.lower(),
                "password": password,
                "nivel": "Estudante",
                "nome": nome,
                "escola_id": escola_id,
                "classe": classe,
                "turma": turma,
                "curso": curso,
                "tem_divida": True,
                "status_conta": "Ativa",
                "email": email,
                "telefone": telefone
            }
            
            self.supabase.table('usuarios').insert(dados_estudante).execute()
            
            print_success(f"Estudante {nome} cadastrado com sucesso!")
            print_info(f"Username: {username}")
            
            wait_for_enter()
            
            return {
                "id": estudante_id,
                "nome": nome,
                "username": username.lower(),
                "nivel": "Estudante",
                "escola": escola_id,
                "classe": classe,
                "turma": turma,
                "curso": curso,
                "tem_divida": True,
                "email": email,
                "telefone": telefone
            }
            
        except Exception as e:
            print_error(f"Erro ao cadastrar: {e}")
            return None


# ============================================================================
# MÓDULOS DO SISTEMA (INTEGRAÇÃO)
# ============================================================================

class FinaXOS:
    """Classe principal do sistema FinaX OS"""
    
    def __init__(self):
        self.session = None
        self.supabase = None
        self._init_modules()
    
    def _init_modules(self):
        """Inicializa módulos"""
        try:
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from modules.database_config import db_config
            self.supabase = db_config.get_client()
        except Exception as e:
            print_error(f"Erro ao carregar módulos: {e}")
            sys.exit(1)
    
    def run(self):
        """Executa o sistema"""
        auth = AuthSystem()
        
        while True:
            clear_screen()
            print_header("🏫 FINAX OS", "Sistema Inteligente de Gestão Escolar")
            
            print(f"\n{Colors.colorize('1 - Login', Colors.BRIGHT_WHITE)}")
            print(f"{Colors.colorize('2 - Criar Conta', Colors.BRIGHT_WHITE)}")
            print(f"{Colors.colorize('0 - Sair', Colors.BRIGHT_BLACK)}")
            
            option = input_with_validation("\nEscolha: ", required=True, input_type="number")
            
            if option == "0":
                self._exit()
                break
            elif option == "1":
                self.session = auth.login()
                if self.session:
                    self._main_menu()
            elif option == "2":
                self.session = auth.signup()
                if self.session:
                    self._main_menu()
            else:
                print_error("Opção inválida!")
                wait_for_enter()
    
    def _main_menu(self):
        """Menu principal"""
        while True:
            clear_screen()
            
            nivel = self.session['nivel']
            nome = self.session['nome']
            escola_id = self.session['escola']
            
            print_header(f"📊 MENU PRINCIPAL", f"Bem-vindo, {nome}")
            
            print(f"\n{Colors.colorize(f'🎯 Nível: {nivel}', Colors.BRIGHT_CYAN)}")
            print(f"{Colors.colorize(f'🏛️ Escola ID: {escola_id}', Colors.BRIGHT_BLACK)}")
            print_separator()
            
            if nivel == "Administrador":
                self._menu_admin()
            else:
                self._menu_student()
            
            print_separator()
            print(f"{Colors.colorize('0 - Sair do Sistema', Colors.BRIGHT_BLACK)}")
            
            option = input_with_validation("\n👉 Escolha uma opção: ", required=True, input_type="number")
            
            if option == "0":
                break
            
            self._execute_option(option, nivel, escola_id)
        
        self.session = None
    
    def _menu_admin(self):
        """Menu do administrador"""
        print(f"\n{Colors.colorize('📋 MÓDULOS DISPONÍVEIS', Colors.BRIGHT_GREEN, Colors.BOLD)}")
        print()
        print(" 1 - 📝 Cadastro de Utilizadores")
        print(" 2 - 📍 Controlo de Presenças")
        print(" 3 - 📊 Gestão de Notas")
        print(" 4 - 🏆 Ranking de Alunos")
        print(" 5 - 📈 Dashboard Administrativo")
        print(" 6 - ⚠️ Análise de Risco")
        print(" 7 - 💰 Gestão Financeira (ERP)")
        print(" 8 - 💵 FinaX Pay (Pagamentos)")
        print(" 9 - 📚 Biblioteca Digital")
        print("10 - 🕊️ Canal de Ética")
        print("11 - 🔔 Gestão de Alertas")
        print("12 - 🔐 Segurança (Alterar Senha)")
        print("13 - ⚙️ Configurações")
    
    def _menu_student(self):
        """Menu do estudante"""
        print(f"\n{Colors.colorize('📋 MÓDULOS DISPONÍVEIS', Colors.BRIGHT_GREEN, Colors.BOLD)}")
        print()
        print(" 1 - 📍 Registrar Presença")
        print(" 2 - 📊 Ver Minhas Notas")
        print(" 3 - 🏆 Ver Ranking da Escola")
        print(" 4 - 📚 Biblioteca Digital")
        print(" 5 - 🕊️ Canal de Ética")
        print(" 6 - 🔐 Alterar Minha Senha")
    
    def _execute_option(self, option: str, nivel: str, escola_id: str):
        """Executa a opção escolhida"""
        try:
            if nivel == "Administrador":
                self._execute_admin_option(option, escola_id)
            else:
                self._execute_student_option(option)
        except Exception as e:
            print_error(f"Erro: {e}")
            wait_for_enter()
    
    def _execute_admin_option(self, option: str, escola_id: str):
        """Executa opções do administrador"""
        if option == "1":
            self._module_cadastro(escola_id)
        elif option == "2":
            self._module_presencas(escola_id)
        elif option == "3":
            self._module_notas(escola_id)
        elif option == "4":
            self._module_ranking(escola_id)
        elif option == "5":
            self._module_dashboard(escola_id)
        elif option == "6":
            self._module_risco(escola_id)
        elif option == "7":
            self._module_financeiro(escola_id)
        elif option == "8":
            self._module_financeiro_pay(escola_id)
        elif option == "9":
            self._module_material(escola_id)
        elif option == "10":
            self._module_denuncias()
        elif option == "11":
            self._module_alertas()
        elif option == "12":
            self._module_auth()
        elif option == "13":
            self._module_config(escola_id)
        else:
            print_error("Opção inválida!")
            wait_for_enter()
    
    def _execute_student_option(self, option: str):
        """Executa opções do estudante"""
        aluno_id = self.session['id']
        escola_id = self.session['escola']
        
        if option == "1":
            self._registrar_presenca(aluno_id, escola_id)
        elif option == "2":
            self._ver_boletim(aluno_id)
        elif option == "3":
            self._ver_ranking(escola_id)
        elif option == "4":
            self._module_material(escola_id)
        elif option == "5":
            self._module_denuncias()
        elif option == "6":
            self._module_auth()
        else:
            print_error("Opção inválida!")
            wait_for_enter()
    
    # ========================================================================
    # MÓDULOS (INTEGRAÇÃO COM OS ARQUIVOS EXISTENTES)
    # ========================================================================
    
    def _module_cadastro(self, escola_id: str):
        """Módulo de cadastro"""
        clear_screen()
        print_header("📝 Cadastro de Utilizadores")
        
        try:
            from modules.cadastro import iniciar_cadastro
            iniciar_cadastro(escola_id)
        except ImportError:
            print_warning("Módulo de cadastro não disponível.")
            wait_for_enter()
    
    def _module_presencas(self, escola_id: str):
        """Módulo de presenças"""
        clear_screen()
        print_header("📍 Controlo de Presenças")
        
        try:
            from modules.presencas import iniciar_presenca
            iniciar_presenca(escola_id)
        except ImportError:
            print_warning("Módulo de presenças não disponível.")
            wait_for_enter()
    
    def _module_notas(self, escola_id: str):
        """Módulo de notas"""
        clear_screen()
        print_header("📊 Gestão de Notas")
        
        try:
            from modules.notas import iniciar_notas
            iniciar_notas(escola_id)
        except ImportError:
            print_warning("Módulo de notas não disponível.")
            wait_for_enter()
    
    def _module_ranking(self, escola_id: str):
        """Módulo de ranking"""
        clear_screen()
        print_header("🏆 Ranking de Alunos")
        
        try:
            from modules.ranking import iniciar_ranking
            iniciar_ranking(escola_id)
        except ImportError:
            print_warning("Módulo de ranking não disponível.")
            wait_for_enter()
    
    def _module_dashboard(self, escola_id: str):
        """Módulo dashboard"""
        clear_screen()
        print_header("📈 Dashboard Administrativo")
        
        try:
            from modules.dashboard import iniciar_dashboard
            iniciar_dashboard(escola_id)
        except ImportError:
            print_warning("Módulo dashboard não disponível.")
            wait_for_enter()
    
    def _module_risco(self, escola_id: str):
        """Módulo de análise de risco"""
        clear_screen()
        print_header("⚠️ Análise de Risco")
        
        try:
            from modules.risco import iniciar_analise_risco
            iniciar_analise_risco(escola_id)
        except ImportError:
            print_warning("Módulo de risco não disponível.")
            wait_for_enter()
    
    def _module_financeiro(self, escola_id: str):
        """Módulo financeiro ERP"""
        clear_screen()
        print_header("💰 Gestão Financeira (ERP)")
        
        try:
            from modules.financeiro import iniciar_financeiro
            iniciar_financeiro(escola_id)
        except ImportError:
            print_warning("Módulo financeiro não disponível.")
            wait_for_enter()
    
    def _module_financeiro_pay(self, escola_id: str):
        """Módulo FinaX Pay"""
        clear_screen()
        print_header("💵 FinaX Pay - Pagamentos")
        
        try:
            from modules.financeiro_pay import iniciar_financeiro_pay
            iniciar_financeiro_pay(escola_id)
        except ImportError:
            print_warning("Módulo FinaX Pay não disponível.")
            wait_for_enter()
    
    def _module_material(self, escola_id: str):
        """Módulo biblioteca digital"""
        clear_screen()
        print_header("📚 Biblioteca Digital")
        
        try:
            from modules.material import iniciar_material
            iniciar_material(self.session)
        except ImportError:
            print_warning("Módulo biblioteca não disponível.")
            wait_for_enter()
    
    def _module_denuncias(self):
        """Módulo canal de ética"""
        clear_screen()
        print_header("🕊️ Canal de Ética")
        
        try:
            from modules.denuncias import iniciar_denuncias
            iniciar_denuncias(self.session)
        except ImportError:
            print_warning("Módulo de denúncias não disponível.")
            wait_for_enter()
    
    def _module_alertas(self):
        """Módulo de alertas"""
        clear_screen()
        print_header("🔔 Gestão de Alertas")
        
        try:
            from modules.alertas import iniciar_alertas
            iniciar_alertas(self.session)
        except ImportError:
            print_warning("Módulo de alertas não disponível.")
            wait_for_enter()
    
    def _module_auth(self):
        """Módulo de segurança"""
        clear_screen()
        print_header("🔐 Segurança")
        
        try:
            from modules.auth import iniciar_auth
            iniciar_auth(self.session)
        except ImportError:
            print_warning("Módulo de segurança não disponível.")
            wait_for_enter()
    
    def _module_config(self, escola_id: str):
        """Módulo de configurações"""
        clear_screen()
        print_header("⚙️ Configurações")
        
        print(f"\n{Colors.colorize('1 - Estatísticas do Sistema', Colors.BRIGHT_WHITE)}")
        print(f"{Colors.colorize('2 - Gerenciar Contas', Colors.BRIGHT_WHITE)}")
        print(f"{Colors.colorize('0 - Voltar', Colors.BRIGHT_BLACK)}")
        
        option = input_with_validation("\nEscolha: ", required=True, input_type="number")
        
        if option == "1":
            self._estatisticas_sistema(escola_id)
        elif option == "2":
            self._gerenciar_contas(escola_id)
        
        wait_for_enter()
    
    def _estatisticas_sistema(self, escola_id: str):
        """Exibe estatísticas do sistema"""
        clear_screen()
        print_header("📊 Estatísticas do Sistema")
        
        try:
            alunos = self.supabase.table('usuarios').select('*', count='exact').eq('escola_id', escola_id).eq('nivel', 'Estudante').execute()
            total_alunos = alunos.count
            
            professores = self.supabase.table('usuarios').select('*', count='exact').eq('escola_id', escola_id).eq('nivel', 'Administrador').execute()
            total_professores = professores.count
            
            print(f"\n👥 Total de Alunos: {Colors.colorize(str(total_alunos), Colors.BRIGHT_GREEN)}")
            print(f"👨‍🏫 Total de Administradores: {Colors.colorize(str(total_professores), Colors.BRIGHT_CYAN)}")
            
        except Exception as e:
            print_error(f"Erro: {e}")
    
    def _gerenciar_contas(self, escola_id: str):
        """Gerencia contas de utilizadores"""
        clear_screen()
        print_header("🔑 Gerenciar Contas")
        
        try:
            usuarios = self.supabase.table('usuarios')\
                .select('username, nome, nivel, status_conta')\
                .eq('escola_id', escola_id)\
                .execute()
            
            if usuarios.data:
                from tabulate import tabulate
                print(f"\n{tabulate(usuarios.data, headers='keys', tablefmt='grid')}")
            else:
                print_info("Nenhum utilizador encontrado.")
                
        except Exception as e:
            print_error(f"Erro: {e}")
    
    def _registrar_presenca(self, aluno_id: str, escola_id: str):
        """Registra presença do aluno"""
        clear_screen()
        print_header("📍 Registrar Presença")
        
        print(f"\n{Colors.colorize('Digite o código QR (ou username) do aluno', Colors.BRIGHT_WHITE)}")
        qr_code = input_with_validation("Código: ", required=True)
        
        try:
            aluno = self.supabase.table('usuarios')\
                .select('*')\
                .eq('username', qr_code)\
                .eq('escola_id', escola_id)\
                .eq('nivel', 'Estudante')\
                .execute()
            
            if aluno.data:
                aluno_data = aluno.data[0]
                agora = datetime.now()
                hora = agora.strftime("%H:%M:%S")
                data = agora.strftime("%Y-%m-%d")
                status = "ATRASADO" if agora.hour > 7 or (agora.hour == 7 and agora.minute > 30) else "PRESENTE"
                
                presenca_id = str(uuid.uuid4())
                self.supabase.table('presencas').insert({
                    "id": presenca_id,
                    "aluno_id": aluno_data['id'],
                    "aluno_username": qr_code,
                    "nome_aluno": aluno_data['nome'],
                    "escola_id": escola_id,
                    "data": data,
                    "hora_entrada": hora,
                    "status": status
                }).execute()
                
                print_success(f"{aluno_data['nome']} - {status} às {hora}")
            else:
                print_error("Aluno não encontrado!")
                
        except Exception as e:
            print_error(f"Erro: {e}")
        
        wait_for_enter()
    
    def _ver_boletim(self, aluno_id: str):
        """Ver boletim do aluno"""
        clear_screen()
        print_header("📋 Boletim Escolar")
        
        try:
            from modules.notas import GestaoNotas
            notas = GestaoNotas()
            notas.ver_boletim(aluno_id)
        except ImportError:
            print_warning("Módulo de notas não disponível.")
        
        wait_for_enter()
    
    def _ver_ranking(self, escola_id: str):
        """Ver ranking da escola"""
        clear_screen()
        print_header("🏆 Ranking da Escola")
        
        try:
            from modules.ranking import RankingSistema
            ranking = RankingSistema()
            ranking.exibir_top_10(escola_id)
        except ImportError:
            print_warning("Módulo de ranking não disponível.")
        
        wait_for_enter()
    
    def _exit(self):
        """Encerra o sistema"""
        clear_screen()
        print_header("👋 FINAX OS", "Obrigado por utilizar o sistema!")
        print(f"\n{Colors.colorize('Volte sempre!', Colors.BRIGHT_GREEN)}")
        time.sleep(2)


# ============================================================================
# PONTO DE ENTRADA PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    try:
        app = FinaXOS()
        app.run()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.colorize('Sistema interrompido pelo utilizador.', Colors.YELLOW)}")
    except Exception as e:
        print(f"\n\n{Colors.colorize(f'Erro inesperado: {e}', Colors.RED)}")
        sys.exit(1)