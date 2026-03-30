"""
MÓDULO FINANCEIRO PAY - FINAX OS
Sistema de gestão escolar com Supabase Cloud

Funcionalidade:
- Processamento de pagamentos de propinas
- Cálculo automático de lucro do FinaX (2%)
- Atualização automática do status de débito
- Histórico de pagamentos
- Emissão de recibo digital
"""

import sys
import os
import uuid
from datetime import datetime

# Adiciona a pasta raiz ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================
# IMPORTAÇÕES DOS MÓDULOS INTERNOS
# ============================================
from modules.database_config import db_config

# ============================================
# IMPORTAÇÕES DE TERCEIROS
# ============================================
from tabulate import tabulate

# ============================================
# CORES SIMPLIFICADAS (SEM DEPENDÊNCIA EXTERNA)
# ============================================
class Cores:
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    VERMELHO = '\033[91m'
    AZUL = '\033[94m'
    CIANO = '\033[96m'
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
    print(f"\n{cor_azul('='*50)}")
    print(f"{cor_azul(titulo.center(50))}")
    print(f"{cor_azul('='*50)}")


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


def mostrar_linha():
    """Mostra linha de separação"""
    print(f"{cor_azul('═'*50)}")


def input_com_validacao(prompt, obrigatorio=True, tipo="texto"):
    """Input com validação básica"""
    while True:
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
# CONSTANTES
# ============================================

# Percentual do lucro do FinaX (2%)
PERCENTUAL_LUCRO_FINAX = 0.02


# ============================================
# CLASSE PRINCIPAL DO MÓDULO FINANCEIRO
# ============================================

class FinanceiroPay:
    """
    Classe responsável pela gestão financeira do sistema FinaX OS
    
    Funcionalidades:
    - Processamento de pagamentos de propinas
    - Cálculo automático de lucro (2% para o FinaX)
    - Atualização do status de débito do aluno
    - Histórico de pagamentos
    - Emissão de recibo digital
    """
    
    def __init__(self):
        """Inicializa o módulo financeiro com conexão ao banco de dados"""
        self.supabase = db_config.get_client()
    
    # ============================================
    # 1. PROCESSAR PAGAMENTO
    # ============================================
    
    def processar_pagamento(self, user_id, nome_aluno, escola_id, valor_propina=None):
        """
        Processa o pagamento da propina de um aluno.
        
        Args:
            user_id (str): ID do aluno na tabela usuarios
            nome_aluno (str): Nome do aluno para exibição
            escola_id (str): ID da escola (para validação)
            valor_propina (float, optional): Valor da propina
        
        Returns:
            dict: Dados do pagamento processado ou None se erro
        """
        limpar_tela()
        mostrar_titulo("💰 PROCESSAR PAGAMENTO")
        
        try:
            # ============================================
            # 1.1 VALIDAR ALUNO
            # ============================================
            print(f"\n{cor_amarelo('⏳ Validando dados do aluno...')}")
            
            # Buscar aluno no banco
            resposta = self.supabase.table('usuarios')\
                .select('id, nome, tem_divida, escola_id')\
                .eq('id', user_id)\
                .eq('escola_id', escola_id)\
                .execute()
            
            if not resposta.data:
                mostrar_erro("Aluno não encontrado ou não pertence a esta escola.")
                return None
            
            aluno = resposta.data[0]
            
            # Verificar se aluno já está em dia
            if not aluno['tem_divida']:
                mostrar_info(f"Aluno {aluno['nome']} já está em dia.")
                return None
            
            # ============================================
            # 1.2 DEFINIR VALOR DA PROPINA
            # ============================================
            if valor_propina is None:
                mostrar_info("\n📌 DEFINIÇÃO DO VALOR DA PROPINA")
                print(f"   Aluno: {cor_ciano(aluno['nome'])}")
                
                valor_str = input_com_validacao(
                    "Valor da propina (Kz): ",
                    obrigatorio=True,
                    tipo="numero"
                )
                valor_propina = float(valor_str)
            
            # ============================================
            # 1.3 CÁLCULOS FINANCEIROS
            # ============================================
            lucro_finax = valor_propina * PERCENTUAL_LUCRO_FINAX
            valor_escola = valor_propina - lucro_finax
            
            # ============================================
            # 1.4 CONFIRMAÇÃO DO PAGAMENTO
            # ============================================
            mostrar_info("\n📋 RESUMO DA TRANSAÇÃO")
            
            dados_resumo = [
                ["Aluno", aluno['nome']],
                ["ID do Aluno", user_id],
                ["Valor da Propina", f"{valor_propina:,.2f} Kz"],
                ["Lucro FinaX (2%)", f"{lucro_finax:,.2f} Kz"],
                ["Valor para Escola (98%)", f"{valor_escola:,.2f} Kz"],
                ["Data/Hora", datetime.now().strftime("%d/%m/%Y %H:%M:%S")]
            ]
            
            tabela_resumo = tabulate(dados_resumo, tablefmt="simple", colalign=("left", "right"))
            print(f"\n{tabela_resumo}")
            
            if not confirmar("\nConfirmar pagamento"):
                mostrar_info("Pagamento cancelado.")
                return None
            
            # ============================================
            # 1.5 REGISTAR PAGAMENTO NA TABELA RECEITAS
            # ============================================
            print(f"\n{cor_amarelo('⏳ Registando pagamento...')}")
            
            pagamento_id = str(uuid.uuid4())
            data_pagamento = datetime.now().isoformat()
            
            dados_receita = {
                "id": pagamento_id,
                "aluno_id": user_id,
                "valor_pago": valor_propina,
                "lucro_finax": lucro_finax,
                "data_pagamento": data_pagamento
            }
            
            try:
                # Inserir na tabela receitas
                self.supabase.table('receitas').insert(dados_receita).execute()
                
                # ============================================
                # 1.6 ATUALIZAR STATUS DO ALUNO (tem_divida = False)
                # ============================================
                self.supabase.table('usuarios')\
                    .update({"tem_divida": False})\
                    .eq("id", user_id)\
                    .execute()
                
                # ============================================
                # 1.7 EMITIR RECIBO DIGITAL
                # ============================================
                self._emitir_recibo_digital(
                    aluno=aluno,
                    valor_propina=valor_propina,
                    lucro_finax=lucro_finax,
                    valor_escola=valor_escola,
                    data_pagamento=datetime.now()
                )
                
                return {
                    "pagamento_id": pagamento_id,
                    "aluno": aluno,
                    "valor_propina": valor_propina,
                    "lucro_finax": lucro_finax,
                    "valor_escola": valor_escola,
                    "data_pagamento": data_pagamento
                }
                
            except Exception as e:
                mostrar_erro(f"Erro ao registar pagamento: {e}")
                return None
                
        except Exception as e:
            mostrar_erro(f"Erro ao processar pagamento: {e}")
            return None
    
    # ============================================
    # 2. CONSULTAR HISTÓRICO DE PAGAMENTOS
    # ============================================
    
    def consultar_historico(self, user_id):
        """
        Consulta o histórico de pagamentos de um aluno.
        
        Args:
            user_id (str): ID do aluno na tabela usuarios
            
        Returns:
            list: Lista de pagamentos do aluno
        """
        limpar_tela()
        mostrar_titulo("📜 HISTÓRICO DE PAGAMENTOS")
        
        try:
            # Buscar dados do aluno
            aluno = self.supabase.table('usuarios')\
                .select('id, nome')\
                .eq('id', user_id)\
                .execute()
            
            if not aluno.data:
                mostrar_erro("Aluno não encontrado.")
                return []
            
            nome_aluno = aluno.data[0]['nome']
            
            # Buscar histórico de pagamentos
            pagamentos = self.supabase.table('receitas')\
                .select('*')\
                .eq('aluno_id', user_id)\
                .order('data_pagamento', desc=True)\
                .execute()
            
            if not pagamentos.data:
                mostrar_info(f"Nenhum pagamento registado para o aluno {nome_aluno}.")
                return []
            
            # Preparar dados para exibição
            dados_tabela = []
            total_pago = 0
            total_lucro = 0
            
            for p in pagamentos.data:
                try:
                    data = datetime.fromisoformat(p['data_pagamento']).strftime("%d/%m/%Y %H:%M")
                except:
                    data = p['data_pagamento'][:16] if p['data_pagamento'] else "N/A"
                
                dados_tabela.append([
                    p['id'][:8] + "...",
                    data,
                    f"{p['valor_pago']:,.2f} Kz",
                    f"{p['lucro_finax']:,.2f} Kz"
                ])
                total_pago += p['valor_pago']
                total_lucro += p['lucro_finax']
            
            mostrar_info(f"Aluno: {cor_ciano(nome_aluno)}")
            
            print("\n")
            tabela = tabulate(
                dados_tabela,
                headers=["ID", "DATA", "VALOR PAGO", "LUCRO FINAX"],
                tablefmt="grid"
            )
            print(tabela)
            
            # Totais
            mostrar_linha()
            print(f"📊 TOTAL PAGO: {cor_verde(f'{total_pago:,.2f} Kz')}")
            print(f"💰 LUCRO FINAX: {cor_amarelo(f'{total_lucro:,.2f} Kz')}")
            mostrar_linha()
            
            return pagamentos.data
            
        except Exception as e:
            mostrar_erro(f"Erro ao consultar histórico: {e}")
            return []
    
    # ============================================
    # 3. EMITIR RECIBO DIGITAL
    # ============================================
    
    def _emitir_recibo_digital(self, aluno, valor_propina, lucro_finax, valor_escola, data_pagamento):
        """
        Emite um recibo digital formatado no terminal.
        """
        print("\n")
        mostrar_linha()
        print(f"{cor_verde(cor_verde('='*60))}")
        print(f"{cor_verde('🧾 RECIBO DIGITAL - FINAX OS'.center(60))}")
        print(f"{cor_verde('='*60)}")
        
        print(f"\n{cor_azul('📌 DADOS DO PAGAMENTO')}")
        print(f"   Nº Recibo: {cor_ciano(str(uuid.uuid4())[:8])}")
        print(f"   Data/Hora: {data_pagamento.strftime('%d/%m/%Y às %H:%M:%S')}")
        
        print(f"\n{cor_azul('👤 DADOS DO ALUNO')}")
        print(f"   Nome: {cor_ciano(aluno['nome'])}")
        print(f"   ID: {aluno['id']}")
        
        print(f"\n{cor_azul('💰 DETALHES DA TRANSAÇÃO')}")
        print(f"   Valor da Propina: {cor_verde(f'{valor_propina:,.2f} Kz')}")
        print(f"   Lucro FinaX (2%): {cor_amarelo(f'{lucro_finax:,.2f} Kz')}")
        print(f"   Valor para Escola: {cor_verde(f'{valor_escola:,.2f} Kz')}")
        
        print(f"\n{cor_azul('📊 STATUS')}")
        print(f"   Situação: {cor_verde('PAGAMENTO CONFIRMADO')}")
        print(f"   Débito: {cor_verde('REGULARIZADO')}")
        
        print(f"\n{cor_verde('='*60)}")
        print(f"{cor_verde('✓ Pagamento processado com sucesso!'.center(60))}")
        print(f"{cor_verde('='*60)}")
    
    # ============================================
    # 4. RELATÓRIO DE LUCROS (PARA O ADMIN)
    # ============================================
    
    def relatorio_lucros(self, escola_id, data_inicio=None, data_fim=None):
        """
        Gera relatório de lucros do FinaX para uma escola.
        """
        limpar_tela()
        mostrar_titulo("📊 RELATÓRIO DE LUCROS")
        
        try:
            # Construir query base
            query = self.supabase.table('receitas')\
                .select('*, usuarios!inner(nome, escola_id)')\
                .eq('usuarios.escola_id', escola_id)
            
            if data_inicio:
                query = query.gte('data_pagamento', data_inicio)
            if data_fim:
                query = query.lte('data_pagamento', data_fim)
            
            pagamentos = query.order('data_pagamento', desc=True).execute()
            
            if not pagamentos.data:
                mostrar_info("Nenhum pagamento registado para o período selecionado.")
                return
            
            # Preparar dados
            dados_tabela = []
            total_pago = 0
            total_lucro = 0
            
            for p in pagamentos.data:
                try:
                    data = datetime.fromisoformat(p['data_pagamento']).strftime("%d/%m/%Y %H:%M")
                except:
                    data = p['data_pagamento'][:16] if p['data_pagamento'] else "N/A"
                
                nome_aluno = p['usuarios']['nome']
                
                dados_tabela.append([
                    nome_aluno,
                    data,
                    f"{p['valor_pago']:,.2f} Kz",
                    f"{p['lucro_finax']:,.2f} Kz"
                ])
                total_pago += p['valor_pago']
                total_lucro += p['lucro_finax']
            
            print("\n")
            tabela = tabulate(
                dados_tabela,
                headers=["ALUNO", "DATA", "VALOR PAGO", "LUCRO FINAX"],
                tablefmt="grid"
            )
            print(tabela)
            
            mostrar_linha()
            print(f"📊 TOTAL PAGO: {cor_verde(f'{total_pago:,.2f} Kz')}")
            print(f"💰 TOTAL LUCRO FINAX: {cor_amarelo(f'{total_lucro:,.2f} Kz')}")
            mostrar_linha()
            
        except Exception as e:
            mostrar_erro(f"Erro ao gerar relatório: {e}")
    
    # ============================================
    # 5. MENU PRINCIPAL
    # ============================================
    
    def menu(self, escola_id):
        """
        Menu interativo do módulo financeiro.
        
        Args:
            escola_id (str): ID da escola do administrador logado
        """
        while True:
            limpar_tela()
            mostrar_titulo("💰 FINAX PAY - GESTÃO FINANCEIRA")
            
            print("1 - 💵 Processar Pagamento")
            print("2 - 📜 Consultar Histórico de Aluno")
            print("3 - 📊 Relatório de Lucros")
            print("4 - ⬅️ Voltar ao Menu Principal")
            
            opcao = input_com_validacao(
                "\nEscolha uma opção",
                obrigatorio=True,
                tipo="numero"
            )
            
            if opcao == "1":
                # Processar pagamento
                user_id = input_com_validacao(
                    "ID do aluno: ",
                    obrigatorio=True
                )
                
                # Buscar nome do aluno
                aluno = self.supabase.table('usuarios')\
                    .select('nome')\
                    .eq('id', user_id)\
                    .eq('escola_id', escola_id)\
                    .execute()
                
                if not aluno.data:
                    mostrar_erro("Aluno não encontrado.")
                    input("\nPressione ENTER para continuar...")
                    continue
                
                nome_aluno = aluno.data[0]['nome']
                
                valor_str = input_com_validacao(
                    "Valor da propina (Kz): ",
                    obrigatorio=True,
                    tipo="numero"
                )
                
                self.processar_pagamento(user_id, nome_aluno, escola_id, float(valor_str))
                input("\nPressione ENTER para continuar...")
                
            elif opcao == "2":
                user_id = input_com_validacao(
                    "ID do aluno: ",
                    obrigatorio=True
                )
                self.consultar_historico(user_id)
                input("\nPressione ENTER para continuar...")
                
            elif opcao == "3":
                self.relatorio_lucros(escola_id)
                input("\nPressione ENTER para continuar...")
                
            elif opcao == "4":
                break
                
            else:
                mostrar_erro("Opção inválida!")
                input("\nPressione ENTER para continuar...")


# ============================================
# FUNÇÃO DE INTEGRAÇÃO PARA O MAIN
# ============================================

def iniciar_financeiro_pay(escola_id):
    """
    Função de integração para ser chamada pelo main.py
    
    Args:
        escola_id (str): ID da escola do administrador logado
    """
    try:
        financeiro = FinanceiroPay()
        financeiro.menu(escola_id)
    except Exception as e:
        mostrar_erro(f"Erro ao iniciar FinaX Pay: {e}")
        input("\nPressione ENTER para continuar...")


# ============================================
# TESTE DO MÓDULO
# ============================================

if __name__ == "__main__":
    print("🧪 Teste do módulo Financeiro Pay")
    print("⚠️ Para testar, execute o main.py com um administrador logado.")