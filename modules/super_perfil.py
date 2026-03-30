"""
MÓDULO SUPER PERFIL - UMBRELLA AI
Sistema de autenticação com níveis de administrador e segurança SHA-256
"""

import sys
import os
import time
import uuid
import hashlib
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.database_config import db_config

# ============================================
# CORES E UTILITÁRIOS
# ============================================
class Colors:
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    VERMELHO = '\033[91m'
    AZUL = '\033[94m'
    CIANO = '\033[96m'
    RESET = '\033[0m'
    NEGRITO = '\033[1m'


def cor_verde(t): return f"{Colors.VERDE}{t}{Colors.RESET}"
def cor_vermelho(t): return f"{Colors.VERMELHO}{t}{Colors.RESET}"
def cor_amarelo(t): return f"{Colors.AMARELO}{t}{Colors.RESET}"
def cor_azul(t): return f"{Colors.AZUL}{t}{Colors.RESET}"
def cor_ciano(t): return f"{Colors.CIANO}{t}{Colors.RESET}"


def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')


def mostrar_titulo(titulo):
    print(f"\n{cor_azul('='*60)}")
    print(f"{cor_azul(titulo.center(60))}")
    print(f"{cor_azul('='*60)}")


def mostrar_sucesso(m): print(f"{cor_verde('✅')} {m}")
def mostrar_erro(m): print(f"{cor_vermelho('❌')} {m}")
def mostrar_info(m): print(f"{cor_ciano('ℹ️')} {m}")
def mostrar_alerta(m): print(f"{cor_amarelo('⚠️')} {m}")


def input_com_validacao(prompt, obrigatorio=True, tipo="texto", mascara=False):
    while True:
        if mascara:
            import getpass
            valor = getpass.getpass(prompt).strip()
        else:
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
        if tipo == "phone":
            if not valor.isdigit() or len(valor) < 9:
                mostrar_erro("Telefone inválido! 9 dígitos")
                continue
        return valor


def confirmar(mensagem):
    resposta = input(f"{cor_amarelo(mensagem)} (s/n): ").lower()
    return resposta == 's'


# ============================================
# CLASSE PRINCIPAL
# ============================================

class SuperPerfil:
    def __init__(self):
        self.supabase = db_config.get_client()
        self.usuario_logado = None

    def _hash_senha(self, senha):
        return hashlib.sha256(senha.encode()).hexdigest()

    def _verificar_senha(self, senha, hash_armazenado):
        return self._hash_senha(senha) == hash_armazenado

    def fazer_login(self, username, password):
        username_limpo = username.lower().strip()
        if not username_limpo or not password:
            mostrar_erro("Username e password são obrigatórios!")
            return None

        try:
            resultado = self.supabase.table('usuarios')\
                .select('*')\
                .eq('username', username_limpo)\
                .execute()

            if not resultado.data:
                mostrar_erro("Username ou password incorretos!")
                return None

            usuario = resultado.data[0]

            if not self._verificar_senha(password, usuario.get('password', '')):
                mostrar_erro("Username ou password incorretos!")
                return None

            if usuario.get('status_conta') == "Bloqueada":
                mostrar_erro("Conta bloqueada! Contacte o administrador.")
                return None

            dados_sessao = {
                "id": usuario.get('id'),
                "nome": usuario.get('nome'),
                "username": usuario.get('username'),
                "nivel": usuario.get('nivel'),
                "sub_nivel": usuario.get('sub_nivel', ''),
                "escola": usuario.get('escola_id'),
                "classe": usuario.get('classe', 'N/A'),
                "turma": usuario.get('turma', 'N/A'),
                "curso": usuario.get('curso', 'N/A'),
                "tem_divida": usuario.get('tem_divida', False),
                "email": usuario.get('email', ''),
                "telefone": usuario.get('telefone', ''),
                "qrcode_id": usuario.get('qrcode_id', ''),
                "iban": usuario.get('iban', ''),
                "iban_nome": usuario.get('iban_nome', '')
            }

            self.usuario_logado = dados_sessao
            self._exibir_boas_vindas(dados_sessao)
            return dados_sessao

        except Exception as e:
            mostrar_erro(f"Erro: {e}")
            return None

    def _exibir_boas_vindas(self, dados):
        nome = dados.get('nome', 'Utilizador')
        nivel = dados.get('nivel', '')
        sub_nivel = dados.get('sub_nivel', '')

        limpar_tela()
        mostrar_titulo("UMBRELLA AI - SISTEMA DE GESTÃO ESCOLAR")

        print(f"\n{cor_verde('╔════════════════════════════════════════════════════════════╗')}")
        print(f"{cor_verde(f'║  🎉 BEM-VINDO(A), {nome.upper()}!  🎉')}")
        print(f"{cor_verde('╚════════════════════════════════════════════════════════════╝')}")

        print(f"\n{cor_azul('📋 PERFIL')}")
        print(f"   • Nível: {cor_ciano(nivel)}{f' ({sub_nivel})' if sub_nivel else ''}")
        print(f"   • Username: {dados.get('username')}")
        print(f"   • Escola ID: {cor_ciano(dados.get('escola'))}")

        if dados.get('iban'):
            print(f"   • IBAN: {cor_verde(dados.get('iban'))}")
            print(f"   • Titular: {dados.get('iban_nome')}")

        if dados.get('qrcode_id'):
            print(f"   • QR Code ID: {cor_verde(dados.get('qrcode_id'))}")

        if nivel == "Estudante":
            print(f"\n{cor_azul('📚 DADOS ACADÉMICOS')}")
            print(f"   • Classe: {dados.get('classe', 'N/A')}")
            print(f"   • Turma: {dados.get('turma', 'N/A')}")
            print(f"   • Curso: {dados.get('curso', 'N/A')}")
            status = "DÉBITO PENDENTE" if dados.get('tem_divida') else "EM DIA"
            cor_status = cor_vermelho if dados.get('tem_divida') else cor_verde
            print(f"   • Status Financeiro: {cor_status(status)}")

        print(f"\n{cor_azul('═'*60)}")
        print(f"{cor_amarelo(f'⏰ {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')}")

    def get_usuario(self): return self.usuario_logado
    def is_autenticado(self): return self.usuario_logado is not None
    def is_admin(self): return self.usuario_logado and self.usuario_logado.get('nivel') == 'Administrador'
    def is_super_admin(self): return self.usuario_logado and self.usuario_logado.get('sub_nivel') == 'SuperAdmin'

    def logout(self):
        if self.usuario_logado:
            mostrar_info(f"Até logo, {self.usuario_logado.get('nome')}!")
            self.usuario_logado = None


def iniciar_login():
    limpar_tela()
    mostrar_titulo("🔐 UMBRELLA AI - LOGIN")
    print(f"\n{cor_ciano('Por favor, insira as suas credenciais.')}\n")

    tentativas = 0
    perfil = SuperPerfil()

    while tentativas < 3:
        username = input_com_validacao("Username: ", obrigatorio=True)
        password = input_com_validacao("Password: ", obrigatorio=True, mascara=True)

        sessao = perfil.fazer_login(username, password)
        if sessao:
            return sessao

        tentativas += 1
        if tentativas < 3:
            mostrar_info(f"Tentativas restantes: {3 - tentativas}")
            time.sleep(1)

    mostrar_erro("Número máximo de tentativas excedido.")
    return None


def iniciar_login_simples(username, password):
    try:
        supabase = db_config.get_client()
        resultado = supabase.table('usuarios').select('*').eq('username', username.lower()).execute()

        if not resultado.data:
            return None

        usuario = resultado.data[0]
        senha_hash = hashlib.sha256(password.encode()).hexdigest()

        if usuario.get('password') != senha_hash:
            return None
        if usuario.get('status_conta') == "Bloqueada":
            return None

        return {
            "id": usuario.get('id'),
            "nome": usuario.get('nome'),
            "username": usuario.get('username'),
            "nivel": usuario.get('nivel'),
            "sub_nivel": usuario.get('sub_nivel', ''),
            "escola": usuario.get('escola_id'),
            "classe": usuario.get('classe', 'N/A'),
            "turma": usuario.get('turma', 'N/A'),
            "curso": usuario.get('curso', 'N/A'),
            "tem_divida": usuario.get('tem_divida', False),
            "email": usuario.get('email', ''),
            "telefone": usuario.get('telefone', ''),
            "qrcode_id": usuario.get('qrcode_id', ''),
            "iban": usuario.get('iban', ''),
            "iban_nome": usuario.get('iban_nome', '')
        }
    except Exception:
        return None


if __name__ == "__main__":
    print("🧪 Módulo Super Perfil carregado")