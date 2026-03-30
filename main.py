#!/usr/bin/env python3
"""
UMBRELLA AI - SISTEMA DE GESTÃO ESCOLAR
Versão Terminal Profissional
"""

import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.super_perfil import SuperPerfil, iniciar_login
from modules.database_config import db_config
from modules.cadastro import iniciar_cadastro

# ============================================
# CORES
# ============================================
class Colors:
    VERDE = '\033[92m'; AMARELO = '\033[93m'; VERMELHO = '\033[91m'
    AZUL = '\033[94m'; CIANO = '\033[96m'; RESET = '\033[0m'; NEGRITO = '\033[1m'


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


def input_validacao(prompt, obrigatorio=True):
    while True:
        valor = input(prompt).strip()
        if obrigatorio and not valor:
            mostrar_erro("Campo obrigatório!")
            continue
        return valor


# ============================================
# MÓDULOS (PLACEHOLDERS)
# ============================================
def modulo_presencas(sessao):
    limpar_tela(); mostrar_titulo("📍 Presenças"); print("\nEm desenvolvimento..."); input("\nENTER...")


def modulo_notas(sessao):
    limpar_tela(); mostrar_titulo("📊 Notas"); print("\nEm desenvolvimento..."); input("\nENTER...")


def modulo_ranking(sessao):
    limpar_tela(); mostrar_titulo("🏆 Ranking"); print("\nEm desenvolvimento..."); input("\nENTER...")


def modulo_dashboard(sessao):
    limpar_tela(); mostrar_titulo("📈 Dashboard"); print("\nEm desenvolvimento..."); input("\nENTER...")


def modulo_risco(sessao):
    limpar_tela(); mostrar_titulo("⚠️ Risco"); print("\nEm desenvolvimento..."); input("\nENTER...")


def modulo_financeiro(sessao):
    limpar_tela(); mostrar_titulo("💰 Financeiro"); print("\nEm desenvolvimento..."); input("\nENTER...")


def modulo_material(sessao):
    limpar_tela(); mostrar_titulo("📚 Biblioteca"); print("\nEm desenvolvimento..."); input("\nENTER...")


def modulo_denuncias(sessao):
    limpar_tela(); mostrar_titulo("🕊️ Ética"); print("\nEm desenvolvimento..."); input("\nENTER...")


def modulo_alertas(sessao):
    limpar_tela(); mostrar_titulo("🔔 Alertas"); print("\nEm desenvolvimento..."); input("\nENTER...")


def modulo_auth(sessao):
    limpar_tela(); mostrar_titulo("🔐 Segurança"); print("\nEm desenvolvimento..."); input("\nENTER...")


# ============================================
# MENUS
# ============================================
def menu_admin(sessao):
    while True:
        limpar_tela()
        mostrar_titulo("UMBRELLA AI - MENU ADMINISTRADOR")
        print(f"\n{cor_ciano(f'👤 {sessao["nome"]}')}")
        print(f"{cor_ciano(f'🏛️ Escola: {sessao["escola"]}')}")
        print(f"{cor_ciano(f'📊 Nível: {sessao["nivel"]}{f" ({sessao["sub_nivel"]})" if sessao.get("sub_nivel") else ""}')}")
        if sessao.get('iban'):
            print(f"{cor_ciano(f'🏦 IBAN: {sessao["iban"][:15]}...')}")

        print("\n1 - 📝 Cadastro")
        print("2 - 📍 Presenças")
        print("3 - 📊 Notas")
        print("4 - 🏆 Ranking")
        print("5 - 📈 Dashboard")
        print("6 - ⚠️ Risco")
        print("7 - 💰 Financeiro")
        print("8 - 📚 Biblioteca")
        print("9 - 🕊️ Ética")
        print("10 - 🔔 Alertas")
        print("11 - 🔐 Segurança")
        print("0 - Sair")

        opcao = input_validacao("\n👉 Escolha: ")

        if opcao == "1":
            iniciar_cadastro(sessao)
        elif opcao == "2":
            modulo_presencas(sessao)
        elif opcao == "3":
            modulo_notas(sessao)
        elif opcao == "4":
            modulo_ranking(sessao)
        elif opcao == "5":
            modulo_dashboard(sessao)
        elif opcao == "6":
            modulo_risco(sessao)
        elif opcao == "7":
            modulo_financeiro(sessao)
        elif opcao == "8":
            modulo_material(sessao)
        elif opcao == "9":
            modulo_denuncias(sessao)
        elif opcao == "10":
            modulo_alertas(sessao)
        elif opcao == "11":
            modulo_auth(sessao)
        elif opcao == "0":
            break
        else:
            mostrar_erro("Opção inválida!")


def menu_estudante(sessao):
    while True:
        limpar_tela()
        mostrar_titulo("UMBRELLA AI - MENU ESTUDANTE")
        print(f"\n{cor_ciano(f'👤 {sessao["nome"]}')}")
        print(f"{cor_ciano(f'🏛️ Escola: {sessao["escola"]}')}")
        if sessao.get('qrcode_id'):
            print(f"{cor_ciano(f'📱 QR ID: {sessao["qrcode_id"]}')}")

        print("\n1 - 📍 Registrar Presença")
        print("2 - 📊 Minhas Notas")
        print("3 - 🏆 Ranking")
        print("4 - 📚 Biblioteca")
        print("5 - 🕊️ Canal de Ética")
        print("6 - 🔐 Alterar Senha")
        print("0 - Sair")

        opcao = input_validacao("\n👉 Escolha: ")

        if opcao == "1":
            print("\nEm desenvolvimento...")
            input("\nENTER...")
        elif opcao == "2":
            print("\nEm desenvolvimento...")
            input("\nENTER...")
        elif opcao == "3":
            print("\nEm desenvolvimento...")
            input("\nENTER...")
        elif opcao == "4":
            modulo_material(sessao)
        elif opcao == "5":
            modulo_denuncias(sessao)
        elif opcao == "6":
            modulo_auth(sessao)
        elif opcao == "0":
            break
        else:
            mostrar_erro("Opção inválida!")


# ============================================
# MAIN
# ============================================
def main():
    while True:
        limpar_tela()
        mostrar_titulo("☂️ UMBRELLA AI")
        print("\n1 - 🔐 Login")
        print("2 - 🏫 Criar Nova Escola (Primeiro Acesso)")
        print("0 - Sair")

        opcao = input_validacao("\n👉 Escolha: ")

        if opcao == "1":
            sessao = iniciar_login()
            if sessao:
                if sessao['nivel'] == 'Administrador':
                    menu_admin(sessao)
                else:
                    menu_estudante(sessao)
        elif opcao == "2":
            cadastro = Cadastro()
            sessao = cadastro.criar_escola()
            if sessao:
                mostrar_sucesso("Escola criada! Faça login.")
                input("\nENTER...")
        elif opcao == "0":
            break
        else:
            mostrar_erro("Opção inválida!")

    limpar_tela()
    print(f"\n{cor_verde('👋 Obrigado por utilizar o Umbrella AI!')}\n")
    time.sleep(1)


if __name__ == "__main__":
    try:
        from modules.cadastro import Cadastro
        main()
    except KeyboardInterrupt:
        print(f"\n\n{cor_amarelo('Sistema interrompido.')}")
    except Exception as e:
        print(f"\n\n{cor_vermelho(f'Erro: {e}')}")