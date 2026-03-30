"""
FINAX OS - SISTEMA COMPLETO DE GESTÃO ESCOLAR
Com sistema de Signup para Estudantes e Administradores
"""

import sys
import os
import time
import uuid
from datetime import datetime

# Adiciona a pasta raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ============================================
# CORES SIMPLIFICADAS
# ============================================
class Cores:
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    VERMELHO = '\033[91m'
    AZUL = '\033[94m'
    CIANO = '\033[96m'
    ROXO = '\033[95m'
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


def mostrar_alerta(mensagem):
    """Mostra mensagem de alerta"""
    print(f"{cor_amarelo('⚠️')} {mensagem}")


def input_com_validacao(prompt, obrigatorio=True, tipo="texto", mascara=False):
    """Input com validação básica"""
    while True:
        if mascara:
            import getpass
            valor = getpass.getpass(prompt).strip()
        else:
            valor = input(prompt).strip()
        
        if obrigatorio and not valor:
            mostrar_erro("Este campo é obrigatório!")
            continue
        
        if not valor and not obrigatorio:
            return None
        
        if tipo == "numero":
            try:
                return str(int(valor))
            except ValueError:
                mostrar_erro("Digite um número válido!")
                continue
        
        return valor


def confirmar(mensagem):
    """Pergunta confirmação ao utilizador"""
    resposta = input(f"{cor_amarelo(mensagem)} (s/n): ").lower()
    return resposta == 's'


# ============================================
# MÓDULOS PRINCIPAIS
# ============================================
from modules.database_config import db_config
from modules.cadastro import iniciar_cadastro
from modules.presencas import iniciar_presenca
from modules.notas import iniciar_notas
from modules.ranking import iniciar_ranking
from modules.dashboard import iniciar_dashboard
from modules.risco import iniciar_analise_risco
from modules.financeiro import iniciar_financeiro
from modules.financeiro_pay import iniciar_financeiro_pay
from modules.material import iniciar_material
from modules.denuncias import iniciar_denuncias
from modules.alertas import iniciar_alertas, verificar_notificacoes_login
from modules.auth import iniciar_auth


# ============================================
# CLASSE PRINCIPAL
# ============================================

class FinaXOS:
    """Classe principal do sistema FinaX OS"""
    
    def __init__(self):
        self.sessao = None
        self.supabase = db_config.get_client()
    
    def executar(self):
        """Ponto de entrada principal"""
        self._apresentacao()
        
        while True:
            opcao = self._menu_login()
            
            if opcao == "1":
                self.sessao = self._login()
                if self.sessao:
                    self._menu_principal()
            elif opcao == "2":
                self._signup()
            elif opcao == "3":
                break
        
        self._encerrar()
    
    def _apresentacao(self):
        """Apresentação inicial"""
        limpar_tela()
        
        print(f"{cor_azul(Cores.NEGRITO)}")
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║                                                                  ║")
        print("║    ███████╗██╗███╗   ██╗ █████╗ ██╗  ██╗     ██████╗ ███████╗   ║")
        print("║    ██╔════╝██║████╗  ██║██╔══██╗╚██╗██╔╝    ██╔═══██╗██╔════╝   ║")
        print("║    █████╗  ██║██╔██╗ ██║███████║ ╚███╔╝     ██║   ██║███████╗   ║")
        print("║    ██╔══╝  ██║██║╚██╗██║██╔══██║ ██╔██╗     ██║   ██║╚════██║   ║")
        print("║    ██║     ██║██║ ╚████║██║  ██║██╔╝ ██╗    ╚██████╔╝███████║   ║")
        print("║    ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝     ╚═════╝ ╚══════╝   ║")
        print("║                                                                  ║")
        print("║                    SISTEMA DE GESTÃO ESCOLAR                     ║")
        print("║                      Powered by FinaX AI                         ║")
        print("╚══════════════════════════════════════════════════════════════════╝")
        print(f"{Cores.RESET}")
        
        time.sleep(1.5)
    
    def _menu_login(self):
        """Menu inicial de login/signup"""
        limpar_tela()
        mostrar_titulo("🔐 FINAX OS - ACESSO")
        
        print("\n1 - Login")
        print("2 - Criar nova conta (Signup)")
        print("3 - Sair")
        
        opcao = input_com_validacao(
            f"\n{cor_ciano('👉 Escolha uma opção: ')}",
            obrigatorio=True,
            tipo="numero"
        )
        
        return opcao
    
    def _login(self):
        """Realiza login do utilizador"""
        limpar_tela()
        mostrar_titulo("🔐 LOGIN")
        
        tentativas = 0
        max_tentativas = 3
        
        while tentativas < max_tentativas:
            username = input_com_validacao("Username: ", obrigatorio=True)
            password = input_com_validacao("Password: ", obrigatorio=True, mascara=True)
            
            try:
                resultado = self.supabase.table('usuarios')\
                    .select('*')\
                    .eq('username', username.lower())\
                    .eq('password', password)\
                    .execute()
                
                if resultado.data:
                    usuario = resultado.data[0]
                    
                    if usuario.get('status_conta') == "Bloqueada":
                        mostrar_erro("Conta bloqueada! Contacte o administrador.")
                        tentativas += 1
                        continue
                    
                    mostrar_sucesso(f"Bem-vindo, {usuario['nome']}!")
                    time.sleep(1)
                    
                    return {
                        "id": usuario.get('id'),
                        "nome": usuario.get('nome'),
                        "username": usuario.get('username'),
                        "nivel": usuario.get('nivel'),
                        "escola": usuario.get('escola_id'),
                        "classe": usuario.get('classe', 'N/A'),
                        "turma": usuario.get('turma', 'N/A'),
                        "curso": usuario.get('curso', 'N/A'),
                        "tem_divida": usuario.get('tem_divida', False),
                        "status_conta": usuario.get('status_conta', 'Ativa')
                    }
                else:
                    tentativas += 1
                    restantes = max_tentativas - tentativas
                    mostrar_erro(f"Credenciais inválidas. Tentativas restantes: {restantes}")
                    time.sleep(1)
                    
            except Exception as e:
                mostrar_erro(f"Erro: {e}")
                tentativas += 1
        
        mostrar_erro("Número máximo de tentativas excedido.")
        return None
    
    def _signup(self):
        """Menu de criação de nova conta"""
        limpar_tela()
        mostrar_titulo("📝 CRIAR NOVA CONTA")
        
        print("\n1 - Sou Administrador (Criar Escola)")
        print("2 - Sou Estudante (Juntar-me a uma Escola)")
        print("3 - Voltar")
        
        opcao = input_com_validacao(
            f"\n{cor_ciano('👉 Escolha uma opção: ')}",
            obrigatorio=True,
            tipo="numero"
        )
        
        if opcao == "1":
            self._signup_admin()
        elif opcao == "2":
            self._signup_estudante()
    
    def _signup_admin(self):
        """Cadastro de novo administrador e criação de escola"""
        limpar_tela()
        mostrar_titulo("🏫 CADASTRO DE ADMINISTRADOR / ESCOLA")
        
        mostrar_info("Vamos criar a sua conta de administrador e a sua escola.")
        print()
        
        # Dados da escola
        escola_nome = input_com_validacao("Nome da Escola: ", obrigatorio=True)
        escola_endereco = input_com_validacao("Endereço da Escola: ", obrigatorio=True)
        escola_telefone = input_com_validacao("Telefone da Escola: ", obrigatorio=True)
        escola_email = input_com_validacao("Email da Escola: ", obrigatorio=True)
        
        # Gerar ID único da escola
        escola_id = f"ESC_{uuid.uuid4().hex[:8].upper()}"
        
        # Dados do administrador
        print(f"\n{cor_azul('='*50)}")
        print("👤 DADOS DO ADMINISTRADOR")
        print(f"{cor_azul('='*50)}")
        
        nome = input_com_validacao("Nome completo: ", obrigatorio=True)
        username = input_com_validacao("Username: ", obrigatorio=True)
        password = input_com_validacao("Password: ", obrigatorio=True, mascara=True)
        email = input_com_validacao("Email: ", obrigatorio=True)
        telefone = input_com_validacao("Telefone: ", obrigatorio=True)
        
        # Confirmar
        print(f"\n{cor_azul('='*50)}")
        print("📋 CONFIRMAÇÃO")
        print(f"{cor_azul('='*50)}")
        print(f"Escola: {escola_nome}")
        print(f"ID da Escola: {cor_ciano(escola_id)}")
        print(f"Administrador: {nome}")
        print(f"Username: {username}")
        
        if not confirmar("\nConfirmar criação da conta?"):
            mostrar_info("Cadastro cancelado.")
            return
        
        try:
            # 1. Criar escola (tabela escolas)
            try:
                # Verificar se tabela escolas existe
                self.supabase.table('escolas').select('count').limit(1).execute()
            except:
                # Criar tabela escolas se não existir
                self.supabase.table('escolas').insert({
                    "id": escola_id,
                    "nome": escola_nome,
                    "endereco": escola_endereco,
                    "telefone": escola_telefone,
                    "email": escola_email,
                    "data_criacao": datetime.now().isoformat()
                }).execute()
            
            # 2. Criar administrador
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
            
            mostrar_sucesso("✅ Conta criada com sucesso!")
            mostrar_info(f"ID da Escola: {cor_ciano(escola_id)}")
            mostrar_info(f"Username: {username}")
            mostrar_info("Guarde estas informações!")
            
            # Fazer login automático
            self.sessao = {
                "id": admin_id,
                "nome": nome,
                "username": username.lower(),
                "nivel": "Administrador",
                "escola": escola_id,
                "classe": "DIREÇÃO",
                "turma": "GERAL",
                "curso": "ADMINISTRAÇÃO",
                "tem_divida": False,
                "status_conta": "Ativa"
            }
            
            time.sleep(2)
            self._menu_principal()
            
        except Exception as e:
            mostrar_erro(f"Erro ao criar conta: {e}")
    
    def _signup_estudante(self):
        """Cadastro de novo estudante"""
        limpar_tela()
        mostrar_titulo("🎓 CADASTRO DE ESTUDANTE")
        
        mostrar_info("Para se juntar a uma escola, precisa do ID da escola fornecido pelo administrador.")
        print()
        
        escola_id = input_com_validacao("ID da Escola: ", obrigatorio=True)
        
        # Verificar se escola existe
        try:
            # Tentar buscar escola (simplificado - pode criar tabela escolas depois)
            # Por enquanto, verificamos se existe algum admin com este escola_id
            escola_existe = self.supabase.table('usuarios')\
                .select('escola_id')\
                .eq('escola_id', escola_id)\
                .limit(1)\
                .execute()
            
            if not escola_existe.data:
                mostrar_erro("Escola não encontrada! Verifique o ID e tente novamente.")
                return
            
            print(f"\n{cor_azul('='*50)}")
            print("👤 DADOS DO ESTUDANTE")
            print(f"{cor_azul('='*50)}")
            
            nome = input_com_validacao("Nome completo: ", obrigatorio=True)
            username = input_com_validacao("Username: ", obrigatorio=True)
            password = input_com_validacao("Password: ", obrigatorio=True, mascara=True)
            email = input_com_validacao("Email: ", obrigatorio=True)
            telefone = input_com_validacao("Telefone: ", obrigatorio=True)
            
            print(f"\n{cor_azul('='*50)}")
            print("📚 DADOS ACADÉMICOS")
            print(f"{cor_azul('='*50)}")
            
            classe = input_com_validacao("Classe (ex: 10ª, 11ª, 12ª): ", obrigatorio=True)
            turma = input_com_validacao("Turma (ex: A, B, C): ", obrigatorio=True)
            curso = input_com_validacao("Curso (ex: Ciências, Humanidades): ", obrigatorio=True)
            
            # Confirmar
            print(f"\n{cor_azul('='*50)}")
            print("📋 CONFIRMAÇÃO")
            print(f"{cor_azul('='*50)}")
            print(f"Escola ID: {escola_id}")
            print(f"Nome: {nome}")
            print(f"Username: {username}")
            print(f"Classe/Turma: {classe} / {turma}")
            
            if not confirmar("\nConfirmar cadastro?"):
                mostrar_info("Cadastro cancelado.")
                return
            
            # Verificar se username já existe
            existe = self.supabase.table('usuarios').select('id').eq('username', username.lower()).execute()
            if existe.data:
                mostrar_erro("Username já existe! Escolha outro.")
                return
            
            # Criar estudante
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
            
            # Criar registo na tabela alunos
            aluno_id = str(uuid.uuid4())
            dados_aluno = {
                "id": aluno_id,
                "username_ligacao": username.lower(),
                "nome": nome,
                "turma": f"{classe}{turma}",
                "escola_id": escola_id
            }
            
            try:
                self.supabase.table('alunos').insert(dados_aluno).execute()
            except:
                pass  # Tabela alunos pode não existir ainda
            
            mostrar_sucesso(f"✅ Estudante {nome} cadastrado com sucesso!")
            mostrar_info(f"Username: {username}")
            
            # Fazer login automático
            self.sessao = {
                "id": estudante_id,
                "nome": nome,
                "username": username.lower(),
                "nivel": "Estudante",
                "escola": escola_id,
                "classe": classe,
                "turma": turma,
                "curso": curso,
                "tem_divida": True,
                "status_conta": "Ativa"
            }
            
            time.sleep(2)
            self._menu_principal()
            
        except Exception as e:
            mostrar_erro(f"Erro ao cadastrar: {e}")
    
    def _menu_principal(self):
        """Menu principal conforme perfil"""
        nivel = self.sessao.get('nivel')
        nome = self.sessao.get('nome')
        escola_id = self.sessao.get('escola')
        
        # Verificar notificações
        try:
            verificar_notificacoes_login(self.sessao)
        except:
            pass
        
        while True:
            limpar_tela()
            
            print(f"{cor_azul('='*60)}")
            print(f"{cor_azul('🏫 FINAX OS - SISTEMA DE GESTÃO ESCOLAR'.center(60))}")
            print(f"{cor_azul('='*60)}")
            print(f"👤 Utilizador: {cor_ciano(nome)}")
            print(f"🎯 Nível: {cor_ciano(nivel)}")
            print(f"🏛️ Escola ID: {cor_ciano(escola_id)}")
            print(f"{cor_azul('='*60)}")
            
            if nivel == "Administrador":
                self._menu_admin()
            else:
                self._menu_estudante()
            
            print(f"\n{cor_amarelo('0 - Sair do sistema')}")
            
            opcao = input_com_validacao(
                f"\n{cor_ciano('👉 Escolha uma opção: ')}",
                obrigatorio=True,
                tipo="numero"
            )
            
            if opcao == "0":
                break
            
            self._executar_opcao(opcao, nivel, escola_id)
    
    def _menu_admin(self):
        """Menu para administradores"""
        print(f"\n{cor_verde('📋 MENU ADMINISTRADOR')}")
        print(f"{cor_verde('-'*40)}")
        print("""
 1 - 📝 Cadastro de Utilizadores
 2 - 📍 Controlo de Presenças (QR Code)
 3 - 📊 Gestão de Notas
 4 - 🏆 Ranking de Alunos
 5 - 📈 Dashboard Administrativo
 6 - ⚠️ Análise de Risco
 7 - 💰 Gestão Financeira (ERP)
 8 - 💵 FinaX Pay (Pagamentos)
 9 - 📚 Biblioteca Digital (Materiais)
10 - 🕊️ Canal de Ética (Denúncias)
11 - 🔔 Gestão de Alertas
12 - 🔐 Segurança (Alterar Senha)
13 - ⚙️ Configurações
        """)
    
    def _menu_estudante(self):
        """Menu para estudantes"""
        print(f"\n{cor_verde('📋 MENU ESTUDANTE')}")
        print(f"{cor_verde('-'*40)}")
        print("""
 1 - 📍 Registrar Presença (QR Code)
 2 - 📊 Ver Minhas Notas (Boletim)
 3 - 🏆 Ver Ranking da Escola
 4 - 📚 Biblioteca Digital
 5 - 🕊️ Canal de Ética (Denúncias)
 6 - 🔐 Alterar Minha Senha
        """)
    
    def _executar_opcao(self, opcao, nivel, escola_id):
        """Executa a opção escolhida"""
        if nivel == "Administrador":
            self._executar_opcao_admin(opcao, escola_id)
        else:
            self._executar_opcao_estudante(opcao)
    
    def _executar_opcao_admin(self, opcao, escola_id):
        """Executa opções do menu administrador"""
        try:
            if opcao == "1":
                iniciar_cadastro(escola_id)
            elif opcao == "2":
                iniciar_presenca(escola_id)
            elif opcao == "3":
                iniciar_notas(escola_id)
            elif opcao == "4":
                iniciar_ranking(escola_id)
            elif opcao == "5":
                iniciar_dashboard(escola_id)
            elif opcao == "6":
                iniciar_analise_risco(escola_id)
            elif opcao == "7":
                iniciar_financeiro(escola_id)
            elif opcao == "8":
                iniciar_financeiro_pay(escola_id)
            elif opcao == "9":
                iniciar_material(self.sessao)
            elif opcao == "10":
                iniciar_denuncias(self.sessao)
            elif opcao == "11":
                iniciar_alertas(self.sessao)
            elif opcao == "12":
                iniciar_auth(self.sessao)
            elif opcao == "13":
                self._configuracoes_admin()
            else:
                mostrar_erro("Opção inválida!")
        except Exception as e:
            mostrar_erro(f"Erro: {e}")
        
        input(f"\n{cor_amarelo('Pressione ENTER para continuar...')}")
    
    def _executar_opcao_estudante(self, opcao):
        """Executa opções do menu estudante"""
        try:
            aluno_id = self.sessao.get('id')
            escola_id = self.sessao.get('escola')
            
            if opcao == "1":
                from modules.presencas import ControloPresenca
                presenca = ControloPresenca()
                qr_data = input_com_validacao("Digite o código do QR (ou username): ")
                if qr_data:
                    presenca.registar_entrada(qr_data, escola_id)
            elif opcao == "2":
                from modules.notas import GestaoNotas
                notas = GestaoNotas()
                notas.ver_boletim(aluno_id)
            elif opcao == "3":
                from modules.ranking import RankingSistema
                ranking = RankingSistema()
                ranking.exibir_top_10(escola_id)
            elif opcao == "4":
                iniciar_material(self.sessao)
            elif opcao == "5":
                iniciar_denuncias(self.sessao)
            elif opcao == "6":
                iniciar_auth(self.sessao)
            else:
                mostrar_erro("Opção inválida!")
        except Exception as e:
            mostrar_erro(f"Erro: {e}")
        
        input(f"\n{cor_amarelo('Pressione ENTER para continuar...')}")
    
    def _configuracoes_admin(self):
        """Configurações do administrador"""
        limpar_tela()
        mostrar_titulo("⚙️ CONFIGURAÇÕES")
        
        print("1 - 📊 Estatísticas do Sistema")
        print("2 - 🔑 Gerenciar Contas")
        print("3 - ⬅️ Voltar")
        
        opcao = input_com_validacao(
            f"\n{cor_ciano('Escolha: ')}",
            obrigatorio=True,
            tipo="numero"
        )
        
        if opcao == "1":
            self._estatisticas_sistema()
        elif opcao == "2":
            self._gerenciar_contas()
        input("\nPressione ENTER para continuar...")
    
    def _estatisticas_sistema(self):
        """Exibe estatísticas"""
        mostrar_titulo("📊 ESTATÍSTICAS")
        
        try:
            escola_id = self.sessao.get('escola')
            
            # Total de alunos
            alunos = self.supabase.table('usuarios').select('*', count='exact').eq('escola_id', escola_id).eq('nivel', 'Estudante').execute()
            total_alunos = alunos.count
            
            # Total de professores/admins
            admins = self.supabase.table('usuarios').select('*', count='exact').eq('escola_id', escola_id).eq('nivel', 'Administrador').execute()
            total_admins = admins.count
            
            print(f"\n🏛️ Escola ID: {cor_ciano(escola_id)}")
            print(f"👥 Total de Alunos: {total_alunos}")
            print(f"👨‍💼 Total de Administradores: {total_admins}")
            
        except Exception as e:
            mostrar_erro(f"Erro: {e}")
    
    def _gerenciar_contas(self):
        """Gerenciar contas"""
        mostrar_titulo("🔑 GERENCIAR CONTAS")
        
        try:
            escola_id = self.sessao.get('escola')
            
            resultado = self.supabase.table('usuarios')\
                .select('username, nome, nivel, status_conta')\
                .eq('escola_id', escola_id)\
                .execute()
            
            if resultado.data:
                from tabulate import tabulate
                print(f"\n{tabulate(resultado.data, headers='keys', tablefmt='grid')}")
            else:
                mostrar_info("Nenhum utilizador encontrado.")
                
        except Exception as e:
            mostrar_erro(f"Erro: {e}")
    
    def _encerrar(self):
        """Encerra o sistema"""
        limpar_tela()
        
        print(f"{cor_verde(Cores.NEGRITO)}")
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║                                                                  ║")
        print("║  👋 OBRIGADO POR UTILIZAR O FINAX OS!  👋                        ║")
        print("║                                                                  ║")
        print("║  Volte sempre!                                                   ║")
        print("║                                                                  ║")
        print("╚══════════════════════════════════════════════════════════════════╝")
        print(f"{Cores.RESET}")
        
        time.sleep(2)


# ============================================
# PONTO DE ENTRADA
# ============================================

if __name__ == "__main__":
    try:
        sistema = FinaXOS()
        sistema.executar()
    except KeyboardInterrupt:
        print(f"\n\n{cor_amarelo('Sistema interrompido pelo utilizador.')}")
    except Exception as e:
        print(f"\n\n{cor_vermelho(f'Erro inesperado: {e}')}") 