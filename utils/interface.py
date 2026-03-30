# utils/interface.py - Versão simplificada
import os
import time

class Cores:
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    VERMELHO = '\033[91m'
    AZUL = '\033[94m'
    CIANO = '\033[96m'
    ROXO = '\033[95m'
    NEGRITO = '\033[1m'
    RESET = '\033[0m'


class Interface:
    """Classe simplificada para compatibilidade com módulos existentes"""
    
    def __init__(self):
        self.cores = Cores()
    
    def limpar_tela(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def mostrar_titulo(self, titulo):
        print(f"\n{Cores.AZUL}{'='*50}{Cores.RESET}")
        print(f"{Cores.AZUL}{titulo}{Cores.RESET}")
        print(f"{Cores.AZUL}{'='*50}{Cores.RESET}")
    
    def mostrar_sucesso(self, mensagem):
        print(f"{Cores.VERDE}✅ {mensagem}{Cores.RESET}")
    
    def mostrar_erro(self, mensagem):
        print(f"{Cores.VERMELHO}❌ {mensagem}{Cores.RESET}")
    
    def mostrar_info(self, mensagem):
        print(f"{Cores.CIANO}ℹ️ {mensagem}{Cores.RESET}")
    
    def mostrar_alerta(self, mensagem):
        print(f"{Cores.AMARELO}⚠️ {mensagem}{Cores.RESET}")
    
    def mostrar_processando(self, mensagem):
        print(f"{Cores.AMARELO}⏳ {mensagem}{Cores.RESET}")
    
    def mostrar_linha(self):
        print(f"{Cores.AZUL}{'='*50}{Cores.RESET}")
    
    def input_com_validacao(self, prompt, obrigatorio=True, tipo="texto", mascara=False):
        while True:
            valor = input(prompt).strip()
            
            if obrigatorio and not valor:
                self.mostrar_erro("Este campo é obrigatório!")
                continue
            
            if not valor and not obrigatorio:
                return None
            
            if tipo == "numero":
                try:
                    return str(int(valor))
                except ValueError:
                    self.mostrar_erro("Digite um número válido!")
                    continue
            
            return valor
    
    def confirmar(self, mensagem):
        resposta = input(f"{Cores.AMARELO}{mensagem} (s/n): {Cores.RESET}").lower()
        return resposta == 's'
    
    def exibir_mensagem(self, mensagem, tipo="info"):
        if tipo == "erro":
            self.mostrar_erro(mensagem)
        elif tipo == "sucesso":
            self.mostrar_sucesso(mensagem)
        elif tipo == "alerta":
            self.mostrar_alerta(mensagem)
        else:
            self.mostrar_info(mensagem)