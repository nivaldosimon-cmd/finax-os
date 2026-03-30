"""
MÓDULO CADASTRO - UMBRELLA AI
Sistema de cadastro com ID da Escola, IBAN e encarregados de educação
"""

import sys
import os
import uuid
import hashlib
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.database_config import db_config
from utils.qr_utils import gerar_qr_code_aluno

# ============================================
# CORES E UTILITÁRIOS
# ============================================
class Colors:
    VERDE = '\033[92m'; AMARELO = '\033[93m'; VERMELHO = '\033[91m'
    AZUL = '\033[94m'; CIANO = '\033[96m'; RESET = '\033[0m'


def cor_verde(t): return f"{Colors.VERDE}{t}{Colors.RESET}"
def cor_vermelho(t): return f"{Colors.VERMELHO}{t}{Colors.RESET}"
def cor_amarelo(t): return f"{Colors.AMARELO}{t}{Colors.RESET}"
def cor_azul(t): return f"{Colors.AZUL}{t}{Colors.RESET}"
def cor_ciano(t): return f"{Colors.CIANO}{t}{Colors.RESET}"


def limpar_tela(): os.system('cls' if os.name == 'nt' else 'clear')
def mostrar_titulo(t): print(f"\n{cor_azul('='*60)}\n{cor_azul(t.center(60))}\n{cor_azul('='*60)}")
def mostrar_sucesso(m): print(f"{cor_verde('✅')} {m}")
def mostrar_erro(m): print(f"{cor_vermelho('❌')} {m}")
def mostrar_info(m): print(f"{cor_ciano('ℹ️')} {m}")
def mostrar_alerta(m): print(f"{cor_amarelo('⚠️')} {m}")


def input_com_validacao(prompt, obrigatorio=True, tipo="texto"):
    while True:
        valor = input(prompt).strip()
        if obrigatorio and not valor:
            mostrar_erro("Campo obrigatório!")
            continue
        if not valor and not obrigatorio:
            return None
        if tipo == "numero":
            try:
                return str(int(valor))
            except:
                mostrar_erro("Digite um número válido!")
                continue
        if tipo == "email":
            if '@' not in valor or '.' not in valor:
                mostrar_erro("Email inválido!")
                continue
        return valor


def confirmar(mensagem):
    resposta = input(f"{cor_amarelo(mensagem)} (s/n): ").lower()
    return resposta == 's'


# ============================================
# CLASSE DE CADASTRO
# ============================================

class Cadastro:
    def __init__(self):
        self.supabase = db_config.get_client()

    def _hash_senha(self, senha):
        return hashlib.sha256(senha.encode()).hexdigest()

    def _gerar_qrcode_id(self, escola_id):
        try:
            ultimo = self.supabase.table('usuarios')\
                .select('qrcode_id')\
                .eq('escola_id', escola_id)\
                .not_.is_('qrcode_id', 'null')\
                .order('qrcode_id', desc=True)\
                .limit(1)\
                .execute()
            if ultimo.data and ultimo.data[0]['qrcode_id']:
                return str(int(ultimo.data[0]['qrcode_id']) + 1)
            return "1001"
        except:
            return "1001"

    def criar_escola(self):
        limpar_tela()
        mostrar_titulo("🏫 CRIAÇÃO DE NOVA ESCOLA")

        print(f"\n{cor_ciano('DADOS DA ESCOLA')}")
        print("-" * 40)
        escola_nome = input_com_validacao("Nome da Escola: ", obrigatorio=True)
        escola_endereco = input_com_validacao("Endereço: ", obrigatorio=True)
        escola_telefone = input_com_validacao("Telefone: ", obrigatorio=True)
        escola_email = input_com_validacao("Email: ", obrigatorio=True, tipo="email")

        print(f"\n{cor_ciano('DADOS BANCÁRIOS (IBAN)')}")
        print("-" * 40)
        iban = input_com_validacao("IBAN (ex: AO06.0066.0000.1234.5678.9012.3): ", obrigatorio=True)
        iban_nome = input_com_validacao("Nome do Titular da Conta: ", obrigatorio=True)

        print(f"\n{cor_ciano('DADOS DO SUPER ADMINISTRADOR')}")
        print("-" * 40)
        nome = input_com_validacao("Nome completo: ", obrigatorio=True)
        username = input_com_validacao("Username: ", obrigatorio=True).lower()
        password = input_com_validacao("Password: ", obrigatorio=True)
        email = input_com_validacao("Email: ", obrigatorio=True, tipo="email")
        telefone = input_com_validacao("Telefone: ", obrigatorio=True)

        print(f"\n{cor_azul('='*40)}")
        print("Confirmação:")
        print(f"Escola: {escola_nome}")
        print(f"IBAN: {iban}")
        print(f"Admin: {nome}")
        if not confirmar("\nConfirmar criação da escola?"):
            mostrar_info("Cancelado.")
            return None

        try:
            escola_id = f"ESC_{uuid.uuid4().hex[:8].upper()}"
            admin_id = str(uuid.uuid4())
            senha_hash = self._hash_senha(password)

            dados_admin = {
                "id": admin_id, "username": username, "password": senha_hash,
                "nivel": "Administrador", "sub_nivel": "SuperAdmin", "nome": nome,
                "email": email, "telefone": telefone, "escola_id": escola_id,
                "classe": "DIREÇÃO", "turma": "GERAL", "curso": "ADMINISTRAÇÃO",
                "tem_divida": False, "status_conta": "Ativa", "iban": iban,
                "iban_nome": iban_nome, "created_at": datetime.now().isoformat()
            }

            self.supabase.table('usuarios').insert(dados_admin).execute()

            mostrar_sucesso("Escola criada com sucesso!")
            mostrar_info(f"ID da Escola: {cor_ciano(escola_id)}")
            mostrar_info(f"IBAN: {cor_verde(iban)}")
            mostrar_info(f"Username: {username}")
            return dados_admin
        except Exception as e:
            mostrar_erro(f"Erro: {e}")
            return None

    def criar_admin(self, escola_id, admin_nivel="Admin"):
        limpar_tela()
        mostrar_titulo("👨‍💼 CADASTRO DE ADMINISTRADOR")
        print(f"\n{cor_ciano(f'Escola ID: {escola_id}')}\n")

        nome = input_com_validacao("Nome completo: ", obrigatorio=True)
        username = input_com_validacao("Username: ", obrigatorio=True).lower()
        password = input_com_validacao("Password: ", obrigatorio=True)
        email = input_com_validacao("Email: ", obrigatorio=True, tipo="email")
        telefone = input_com_validacao("Telefone: ", obrigatorio=True)

        if not confirmar(f"\nConfirmar cadastro de {nome}?"):
            return None

        try:
            admin_id = str(uuid.uuid4())
            dados_admin = {
                "id": admin_id, "username": username, "password": self._hash_senha(password),
                "nivel": "Administrador", "sub_nivel": admin_nivel, "nome": nome,
                "email": email, "telefone": telefone, "escola_id": escola_id,
                "classe": "DIREÇÃO", "turma": "GERAL", "curso": "ADMINISTRAÇÃO",
                "tem_divida": False, "status_conta": "Ativa",
                "created_at": datetime.now().isoformat()
            }
            self.supabase.table('usuarios').insert(dados_admin).execute()
            mostrar_sucesso(f"Admin {nome} cadastrado!")
            mostrar_info(f"Username: {username}")
            return dados_admin
        except Exception as e:
            mostrar_erro(f"Erro: {e}")
            return None

    def criar_estudante(self, escola_id):
        limpar_tela()
        mostrar_titulo("🎓 CADASTRO DE ESTUDANTE")
        print(f"\n{cor_ciano(f'Escola ID: {escola_id}')}\n")

        # Dados pessoais
        print(f"{cor_ciano('DADOS PESSOAIS')}")
        nome = input_com_validacao("Nome completo: ", obrigatorio=True)
        username = input_com_validacao("Username: ", obrigatorio=True).lower()
        password = input_com_validacao("Password: ", obrigatorio=True)
        email = input_com_validacao("Email: ", obrigatorio=True, tipo="email")
        telefone = input_com_validacao("Telefone: ", obrigatorio=True)
        data_nascimento = input_com_validacao("Data Nascimento (dd/mm/aaaa): ", obrigatorio=True)

        # Dados académicos
        print(f"\n{cor_ciano('DADOS ACADÉMICOS')}")
        classe = input_com_validacao("Classe (ex: 10ª, 11ª, 12ª): ", obrigatorio=True)
        turma = input_com_validacao("Turma (ex: A, B, C): ", obrigatorio=True)
        curso = input_com_validacao("Curso (ex: Ciências, Humanidades): ", obrigatorio=True)

        # Encarregados
        print(f"\n{cor_ciano('ENCARREGADOS DE EDUCAÇÃO')}")
        print(f"{cor_amarelo('(Opcional - deixe em branco se não tiver)')}")
        nome_pai = input_com_validacao("Nome do Pai: ", obrigatorio=False) or ""
        telefone_pai = input_com_validacao("Telefone do Pai: ", obrigatorio=False) or ""
        nome_mae = input_com_validacao("Nome da Mãe: ", obrigatorio=False) or ""
        telefone_mae = input_com_validacao("Telefone da Mãe: ", obrigatorio=False) or ""
        nome_responsavel = input_com_validacao("Nome do Responsável: ", obrigatorio=False) or ""
        telefone_responsavel = input_com_validacao("Telefone do Responsável: ", obrigatorio=False) or ""

        print(f"\n{cor_azul('='*40)}")
        print(f"Nome: {nome}\nUsername: {username}\nClasse/Turma: {classe}/{turma}")
        if not confirmar("\nConfirmar cadastro?"):
            return None

        try:
            estudante_id = str(uuid.uuid4())
            qrcode_id = self._gerar_qrcode_id(escola_id)

            dados = {
                "id": estudante_id, "username": username, "password": self._hash_senha(password),
                "nivel": "Estudante", "nome": nome, "email": email, "telefone": telefone,
                "escola_id": escola_id, "classe": classe, "turma": turma, "curso": curso,
                "tem_divida": True, "status_conta": "Ativa", "qrcode_id": qrcode_id,
                "data_nascimento": data_nascimento, "created_at": datetime.now().isoformat(),
                "nome_pai": nome_pai, "telefone_pai": telefone_pai, "nome_mae": nome_mae,
                "telefone_mae": telefone_mae, "nome_responsavel": nome_responsavel,
                "telefone_responsavel": telefone_responsavel
            }

            self.supabase.table('usuarios').insert(dados).execute()

            # Gerar QR Code visual
            turma_completa = f"{classe} {turma}".strip()
            qr_path = gerar_qr_code_aluno(estudante_id, nome, turma_completa, qrcode_id)

            mostrar_sucesso(f"Estudante {nome} cadastrado!")
            mostrar_info(f"Username: {username}")
            mostrar_info(f"QR Code ID: {cor_verde(qrcode_id)}")
            if qr_path:
                mostrar_info(f"QR Code salvo em: {qr_path}")
            return dados
        except Exception as e:
            mostrar_erro(f"Erro: {e}")
            return None

    def _listar_utilizadores(self, escola_id):
        try:
            usuarios = self.supabase.table('usuarios')\
                .select('username, nome, nivel, sub_nivel, status_conta, qrcode_id, iban')\
                .eq('escola_id', escola_id).execute()

            if not usuarios.data:
                mostrar_info("Nenhum utilizador encontrado.")
                return

            print(f"\n{cor_azul('='*60)}")
            print(f"{cor_azul('LISTA DE UTILIZADORES'.center(60))}")
            print(f"{cor_azul('='*60)}")

            for u in usuarios.data:
                iban_info = f" | IBAN: {u['iban'][:15]}..." if u.get('iban') else ""
                qr_info = f" (QR: {u['qrcode_id']})" if u.get('qrcode_id') else ""
                print(f"\n📌 {u['nome']} - @{u['username']}{qr_info}{iban_info}")
                print(f"   Nível: {u['nivel']}{f' ({u["sub_nivel"]})' if u.get('sub_nivel') else ''}")
                print(f"   Status: {cor_verde('Ativo') if u['status_conta'] == 'Ativa' else cor_vermelho('Bloqueado')}")

            print(f"\n{cor_azul('='*60)}")
            print(f"Total: {len(usuarios.data)} utilizador(es)")
        except Exception as e:
            mostrar_erro(f"Erro: {e}")

    def menu(self, sessao):
        escola_id = sessao.get('escola')
        nivel = sessao.get('nivel')
        sub_nivel = sessao.get('sub_nivel', '')

        while True:
            limpar_tela()
            mostrar_titulo("📝 MÓDULO DE CADASTRO")
            print(f"\n{cor_ciano(f'Escola ID: {escola_id}')}")
            print(f"{cor_ciano(f'Nível: {nivel}')}{f' ({sub_nivel})' if sub_nivel else ''}\n")

            print("1 - 🏫 Criar Nova Escola (SuperAdmin apenas)")
            print("2 - 👨‍💼 Cadastrar Administrador")
            print("3 - 🎓 Cadastrar Estudante")
            print("4 - 📋 Listar Utilizadores")
            print("5 - ⬅️ Voltar")

            opcao = input_com_validacao("\nEscolha: ", obrigatorio=True, tipo="numero")

            if opcao == "1":
                if sub_nivel == "SuperAdmin":
                    self.criar_escola()
                else:
                    mostrar_erro("Apenas SuperAdmin pode criar escolas!")
                input("\nPressione ENTER...")
            elif opcao == "2":
                self.criar_admin(escola_id)
                input("\nPressione ENTER...")
            elif opcao == "3":
                self.criar_estudante(escola_id)
                input("\nPressione ENTER...")
            elif opcao == "4":
                self._listar_utilizadores(escola_id)
                input("\nPressione ENTER...")
            elif opcao == "5":
                break
            else:
                mostrar_erro("Opção inválida!")
                input("\nPressione ENTER...")


def iniciar_cadastro(sessao):
    cadastro = Cadastro()
    cadastro.menu(sessao)


if __name__ == "__main__":
    print("🧪 Módulo Cadastro carregado")