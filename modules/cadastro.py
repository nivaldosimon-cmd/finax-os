"""
MÓDULO CADASTRO - FINAX OS
Sistema de gestão escolar com Supabase Cloud

Arquitetura:
- Cadastro inteligente: Estudante vs Administrador
- Double Insert: usuarios + alunos (para estudantes)
- Geração automática de QR Code para estudantes
"""

from datetime import datetime
import sys
import os
import uuid

# Adiciona a pasta raiz ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================
# IMPORTAÇÕES DOS MÓDULOS INTERNOS
# ============================================
from modules.database_config import db_config
from utils.interface import Interface
from utils import qr_utils

# ============================================
# CONSTANTES
# ============================================

# Níveis de utilizador
NIVEL_ESTUDANTE = "Estudante"
NIVEL_ADMIN = "Administrador"

# Valores padrão para Administrador
ADMIN_CLASSE = "DIREÇÃO"
ADMIN_TURMA = "GERAL"
ADMIN_CURSO = "ADMINISTRAÇÃO"
ADMIN_DIVIDA = False

# Valores padrão para Estudante
ESTUDANTE_DIVIDA = True


# ============================================
# CLASSE PRINCIPAL DE CADASTRO
# ============================================

class Cadastro:
    """
    Classe responsável pelo cadastro de utilizadores no sistema FinaX OS
    
    Funcionalidades:
    - Cadastro de Estudantes (com Classe, Turma, Curso e QR Code)
    - Cadastro de Administradores (dados simplificados)
    - Double Insert: usuarios + alunos (apenas para estudantes)
    - Tratamento de duplicidade de username
    """
    
    def __init__(self):
        """Inicializa o módulo de cadastro com conexão ao banco de dados"""
        self.supabase = db_config.get_client()
        self.interface = Interface()
    
    # ============================================
    # 1. VALIDAÇÕES E UTILITÁRIOS
    # ============================================
    
    def _validar_username_unico(self, username):
        """
        Verifica se o username já existe no banco de dados
        
        Args:
            username (str): Username a ser verificado
            
        Returns:
            bool: True se único, False se já existe
        """
        try:
            resposta = self.supabase.table('usuarios')\
                .select('username')\
                .eq('username', username)\
                .execute()
            
            return len(resposta.data) == 0
            
        except Exception as e:
            self.interface.mostrar_erro(f"Erro ao validar username: {e}")
            return False
    
    def _gerar_uuid(self):
        """Gera um UUID único para o registro"""
        return str(uuid.uuid4())
    
    def _tratar_erro_duplicado(self, error):
        """
        Trata erro de chave duplicada (PostgreSQL code 23505)
        
        Args:
            error: Objeto de erro do Supabase
            
        Returns:
            bool: True se foi erro de duplicidade, False caso contrário
        """
        if hasattr(error, 'code') and error.code == '23505':
            self.interface.mostrar_erro("Este username já está em uso. Por favor, escolha outro.")
            return True
        return False
    
    # ============================================
    # 2. CADASTRO DE ESTUDANTE
    # ============================================
    
    def _cadastrar_estudante(self, dados_basicos, escola_id):
        """
        Cadastra um novo estudante no sistema (Double Insert)
        
        Args:
            dados_basicos (dict): Dados comuns (username, password, nome)
            escola_id (str): ID da escola do administrador
            
        Returns:
            dict: Dados do estudante cadastrado ou None se erro
        """
        self.interface.mostrar_titulo("CADASTRO DE ESTUDANTE")
        
        # Coletar dados específicos do estudante
        print(self.interface.cores.azul("\n📚 DADOS ACADÉMICOS"))
        
        classe = self.interface.input_com_validação(
            "Classe (ex: 10ª, 11ª, 12ª): ",
            obrigatorio=True
        )
        
        turma = self.interface.input_com_validação(
            "Turma (ex: A, B, C): ",
            obrigatorio=True
        )
        
        curso = self.interface.input_com_validação(
            "Curso (ex: Ciências, Humanidades): ",
            obrigatorio=True
        )
        
        # Confirmar dados
        self.interface.mostrar_info("\n📋 CONFIRMAÇÃO DOS DADOS")
        print(f"   Nome: {dados_basicos['nome']}")
        print(f"   Username: {dados_basicos['username']}")
        print(f"   Classe: {classe}")
        print(f"   Turma: {turma}")
        print(f"   Curso: {curso}")
        
        if not self.interface.confirmar("Deseja cadastrar este estudante?"):
            self.interface.mostrar_info("Cadastro cancelado.")
            return None
        
        # Gerar UUIDs
        usuario_id = self._gerar_uuid()
        aluno_id = self._gerar_uuid()
        
        # Dados para tabela usuarios
        dados_usuario = {
            "id": usuario_id,
            "username": dados_basicos['username'],
            "password": dados_basicos['password'],
            "nivel": NIVEL_ESTUDANTE,
            "nome": dados_basicos['nome'],
            "escola_id": escola_id,
            "classe": classe,
            "turma": turma,
            "curso": curso,
            "tem_divida": ESTUDANTE_DIVIDA
        }
        
        # Dados para tabela alunos
        dados_aluno = {
            "id": aluno_id,
            "username_ligacao": dados_basicos['username'],
            "nome": dados_basicos['nome'],
            "turma": f"{classe}{turma}",
            "escola_id": escola_id
        }
        
        try:
            # 1. Inserir na tabela usuarios
            self.interface.mostrar_processando("Registando dados do estudante...")
            resultado_usuario = self.supabase.table('usuarios').insert(dados_usuario).execute()
            
            # 2. Inserir na tabela alunos (apenas para estudantes)
            self.interface.mostrar_processando("Registando dados académicos...")
            resultado_aluno = self.supabase.table('alunos').insert(dados_aluno).execute()
            
            # 3. Gerar QR Code
            self.interface.mostrar_processando("Gerando QR Code...")
            qr_code_path = qr_utils.gerar_qr_code(
                dados_basicos['username'],
                dados_basicos['nome'],
                f"{classe}{turma}"
            )
            
            # 4. Sucesso!
            self.interface.mostrar_sucesso("Estudante cadastrado com sucesso!")
            self.interface.mostrar_info(f"📱 QR Code salvo em: {qr_code_path}")
            
            return {
                "usuario": resultado_usuario.data[0] if resultado_usuario.data else None,
                "aluno": resultado_aluno.data[0] if resultado_aluno.data else None,
                "qr_code": qr_code_path
            }
            
        except Exception as e:
            if self._tratar_erro_duplicado(e):
                return None
            self.interface.mostrar_erro(f"Erro ao cadastrar estudante: {e}")
            return None
    
    # ============================================
    # 3. CADASTRO DE ADMINISTRADOR
    # ============================================
    
    def _cadastrar_administrador(self, dados_basicos, escola_id):
        """
        Cadastra um novo administrador no sistema
        
        Args:
            dados_basicos (dict): Dados comuns (username, password, nome)
            escola_id (str): ID da escola
            
        Returns:
            dict: Dados do administrador cadastrado ou None se erro
        """
        self.interface.mostrar_titulo("CADASTRO DE ADMINISTRADOR")
        
        # Confirmar dados
        self.interface.mostrar_info("\n📋 CONFIRMAÇÃO DOS DADOS")
        print(f"   Nome: {dados_basicos['nome']}")
        print(f"   Username: {dados_basicos['username']}")
        print(f"   Nível: Administrador")
        
        if not self.interface.confirmar("Deseja cadastrar este administrador?"):
            self.interface.mostrar_info("Cadastro cancelado.")
            return None
        
        # Gerar UUID
        usuario_id = self._gerar_uuid()
        
        # Dados para tabela usuarios
        dados_usuario = {
            "id": usuario_id,
            "username": dados_basicos['username'],
            "password": dados_basicos['password'],
            "nivel": NIVEL_ADMIN,
            "nome": dados_basicos['nome'],
            "escola_id": escola_id,
            "classe": ADMIN_CLASSE,
            "turma": ADMIN_TURMA,
            "curso": ADMIN_CURSO,
            "tem_divida": ADMIN_DIVIDA
        }
        
        try:
            # Inserir na tabela usuarios
            self.interface.mostrar_processando("Registando administrador...")
            resultado = self.supabase.table('usuarios').insert(dados_usuario).execute()
            
            self.interface.mostrar_sucesso("Administrador cadastrado com sucesso!")
            
            return {
                "usuario": resultado.data[0] if resultado.data else None,
                "aluno": None
            }
            
        except Exception as e:
            if self._tratar_erro_duplicado(e):
                return None
            self.interface.mostrar_erro(f"Erro ao cadastrar administrador: {e}")
            return None
    
    # ============================================
    # 4. CADASTRO PRINCIPAL (PONTO DE ENTRADA)
    # ============================================
    
    def cadastrar(self, escola_id):
        """
        Ponto de entrada principal para cadastro de utilizadores
        
        Args:
            escola_id (str): ID da escola do administrador logado
            
        Returns:
            dict: Dados do utilizador cadastrado ou None se cancelado
        """
        self.interface.limpar_tela()
        self.interface.mostrar_titulo("FINAX OS - SISTEMA DE GESTÃO ESCOLAR")
        self.interface.mostrar_info("Bem-vindo ao módulo de cadastro de utilizadores.\n")
        
        # 1. Escolher tipo de utilizador
        tipo = self.interface.menu_opcoes(
            "TIPO DE UTILIZADOR",
            [
                "Estudante",
                "Administrador",
                "Cancelar"
            ]
        )
        
        if tipo == 3:  # Cancelar
            self.interface.mostrar_info("Cadastro cancelado.")
            return None
        
        tipo_utilizador = "Estudante" if tipo == 1 else "Administrador"
        
        # 2. Coletar dados básicos
        self.interface.mostrar_titulo(f"CADASTRO DE {tipo_utilizador.upper()}")
        
        nome = self.interface.input_com_validação(
            "Nome completo: ",
            obrigatorio=True
        )
        
        username = self.interface.input_com_validação(
            "Username (apenas letras e números, sem espaços): ",
            obrigatorio=True
        )
        username = username.lower().strip()
        
        # Validar username único
        if not self._validar_username_unico(username):
            self.interface.mostrar_erro("Este username já está em uso. Tente outro.")
            return None
        
        password = self.interface.input_com_validação(
            "Password: ",
            obrigatorio=True,
            mascara=True
        )
        
        dados_basicos = {
            "nome": nome.strip(),
            "username": username,
            "password": password
        }
        
        # 3. Cadastrar conforme tipo
        if tipo == 1:  # Estudante
            return self._cadastrar_estudante(dados_basicos, escola_id)
        else:  # Administrador
            return self._cadastrar_administrador(dados_basicos, escola_id)
    
    # ============================================
    # 5. LISTAGEM DE UTILIZADORES
    # ============================================
    
    def listar_utilizadores(self, escola_id, nivel=None):
        """
        Lista utilizadores da escola
        
        Args:
            escola_id (str): ID da escola
            nivel (str, optional): Filtrar por nível ('Estudante' ou 'Administrador')
        """
        try:
            query = self.supabase.table('usuarios')\
                .select('*')\
                .eq('escola_id', escola_id)
            
            if nivel:
                query = query.eq('nivel', nivel)
            
            resultado = query.execute()
            usuarios = resultado.data
            
            if not usuarios:
                self.interface.mostrar_info("Nenhum utilizador encontrado.")
                return
            
            self.interface.mostrar_titulo("LISTA DE UTILIZADORES")
            
            for u in usuarios:
                print(f"\n{self.interface.cores.azul('='*50)}")
                print(f"{self.interface.cores.ciano(f'📌 {u["nome"]}')}")
                print(f"   Username: {u['username']}")
                print(f"   Nível: {u['nivel']}")
                print(f"   Classe/Turma: {u.get('classe', 'N/A')} / {u.get('turma', 'N/A')}")
                print(f"   Curso: {u.get('curso', 'N/A')}")
                print(f"   Status Financeiro: {'❌ Débito' if u.get('tem_divida') else '✅ Em dia'}")
            
            print(f"\n{self.interface.cores.azul('='*50)}")
            print(f"Total: {len(usuarios)} utilizador(es)")
            
        except Exception as e:
            self.interface.mostrar_erro(f"Erro ao listar utilizadores: {e}")
    
    # ============================================
    # 6. MENU PRINCIPAL
    # ============================================
    
    def menu(self, escola_id):
        """
        Menu interativo do módulo de cadastro
        
        Args:
            escola_id (str): ID da escola do administrador logado
        """
        while True:
            self.interface.limpar_tela()
            opcao = self.interface.menu_opcoes(
                "MÓDULO DE CADASTRO",
                [
                    "Cadastrar Novo Utilizador",
                    "Listar Estudantes",
                    "Listar Administradores",
                    "Listar Todos Utilizadores",
                    "Voltar ao Menu Principal"
                ]
            )
            
            if opcao == 1:
                self.cadastrar(escola_id)
                input("\n" + self.interface.cores.amarelo("Pressione ENTER para continuar..."))
                
            elif opcao == 2:
                self.listar_utilizadores(escola_id, NIVEL_ESTUDANTE)
                input("\n" + self.interface.cores.amarelo("Pressione ENTER para continuar..."))
                
            elif opcao == 3:
                self.listar_utilizadores(escola_id, NIVEL_ADMIN)
                input("\n" + self.interface.cores.amarelo("Pressione ENTER para continuar..."))
                
            elif opcao == 4:
                self.listar_utilizadores(escola_id)
                input("\n" + self.interface.cores.amarelo("Pressione ENTER para continuar..."))
                
            elif opcao == 5:
                break


# ============================================
# FUNÇÃO DE INTEGRAÇÃO PARA O MAIN
# ============================================

def iniciar_cadastro(escola_id):
    """
    Função de integração para ser chamada pelo main.py
    
    Args:
        escola_id (str): ID da escola do administrador logado
    """
    cadastro = Cadastro()
    cadastro.menu(escola_id)


# ============================================
# TESTE DO MÓDULO
# ============================================

if __name__ == "__main__":
    print("🧪 Teste do módulo Cadastro")
    print("⚠️ Para testar, execute o main.py com um administrador logado.")