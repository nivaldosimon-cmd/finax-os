"""
MÓDULO FINANCEIRO - FINAX OS
Enterprise Resource Planning (ERP) para gestão escolar

Funcionalidade:
- Gestão completa de entradas e saídas
- Fluxo de caixa e saldo atual
- Relatórios periódicos (diário, mensal, anual)
- Folha salarial e gestão de despesas
- Integração com o módulo FinaX Pay
"""

import sys
import os
import uuid
from datetime import datetime, timedelta

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
# CONSTANTES
# ============================================

# Tipos de transação
TIPO_ENTRADA = "Entrada"
TIPO_SAIDA = "Saída"

# Categorias
CATEGORIAS_ENTRADA = ["Propina", "Matrícula", "Material", "Outros"]
CATEGORIAS_SAIDA = ["Salário", "Manutenção", "Impostos", "Material", "Água/Luz", "Outros"]

# Cores
COR_VERDE = "\033[92m"
COR_VERMELHO = "\033[91m"
COR_RESET = "\033[0m"


# ============================================
# CLASSE PRINCIPAL DE GESTÃO FINANCEIRA
# ============================================

class GestaoFinanceira:
    """
    Classe responsável pela gestão financeira completa da escola.
    
    Funcionalidades:
    - Registo de movimentações (entradas e saídas)
    - Fluxo de caixa e saldo atual
    - Relatórios periódicos
    - Folha salarial
    - Integração com FinaX Pay
    """
    
    def __init__(self):
        """Inicializa o módulo com conexão ao banco de dados"""
        self.supabase = db_config.get_client()
        
    
    # ============================================
    # 1. REGISTAR MOVIMENTAÇÃO
    # ============================================
    
    def registar_movimentacao(self, escola_id):
        """
        Regista uma nova movimentação (entrada ou saída).
        
        Args:
            escola_id (str): ID da escola
        
        Returns:
            dict or None: Dados da transação registada
        """
        self.interface.limpar_tela()
        self.interface.mostrar_titulo("💰 REGISTAR MOVIMENTAÇÃO - FINAX ERP")
        
        try:
            # Escolher tipo de movimentação
            print(f"\n{self.interface.cores.AZUL}📌 TIPO DE MOVIMENTAÇÃO{self.interface.cores.RESET}")
            print("1 - Entrada (Receita)")
            print("2 - Saída (Despesa)")
            
            tipo_opcao = self.interface.input_com_validação(
                "\nEscolha (1-2): ",
                obrigatorio=True,
                tipo="numero"
            )
            
            if tipo_opcao == "1":
                tipo = TIPO_ENTRADA
                categorias = CATEGORIAS_ENTRADA
            elif tipo_opcao == "2":
                tipo = TIPO_SAIDA
                categorias = CATEGORIAS_SAIDA
            else:
                self.interface.exibir_mensagem("Opção inválida!", tipo="erro")
                return None
            
            # Escolher categoria
            print(f"\n{self.interface.cores.AZUL}📂 CATEGORIA{self.interface.cores.RESET}")
            for i, cat in enumerate(categorias, 1):
                print(f"   {i} - {cat}")
            
            cat_opcao = self.interface.input_com_validação(
                "\nEscolha (1-{}): ".format(len(categorias)),
                obrigatorio=True,
                tipo="numero"
            )
            
            try:
                cat_idx = int(cat_opcao) - 1
                if cat_idx < 0 or cat_idx >= len(categorias):
                    raise ValueError
                categoria = categorias[cat_idx]
            except ValueError:
                self.interface.exibir_mensagem("Categoria inválida!", tipo="erro")
                return None
            
            # Valor
            valor = self.interface.input_com_validação(
                "Valor (Kz): ",
                obrigatorio=True,
                tipo="numero"
            )
            valor = float(valor)
            
            # Descrição
            descricao = self.interface.input_com_validação(
                "Descrição: ",
                obrigatorio=True
            )
            
            # Data (opcional, padrão hoje)
            data_padrao = datetime.now().strftime("%Y-%m-%d")
            data = self.interface.input_com_validação(
                f"Data ({data_padrao}): ",
                obrigatorio=False
            )
            if not data:
                data = data_padrao
            
            # Confirmar
            self.interface.mostrar_info("\n📋 CONFIRMAÇÃO")
            print(f"   Tipo: {tipo}")
            print(f"   Categoria: {categoria}")
            print(f"   Valor: {valor:,.2f} Kz")
            print(f"   Descrição: {descricao}")
            print(f"   Data: {data}")
            
            if not self.interface.confirmar("\nDeseja registar esta movimentação?"):
                self.interface.mostrar_info("Operação cancelada.")
                return None
            
            # Registrar no banco
            transacao_id = str(uuid.uuid4())
            
            dados_transacao = {
                "id": transacao_id,
                "tipo": tipo,
                "categoria": categoria,
                "valor": valor,
                "descricao": descricao,
                "escola_id": escola_id,
                "data": data
            }
            
            resultado = self.supabase.table('transacoes').insert(dados_transacao).execute()
            
            if resultado.data:
                self.interface.mostrar_sucesso("Movimentação registada com sucesso!")
                return resultado.data[0]
            else:
                self.interface.exibir_mensagem("Erro ao registar movimentação.", tipo="erro")
                return None
                
        except Exception as e:
            self.interface.exibir_mensagem(f"Erro ao registar movimentação: {e}", tipo="erro")
            return None
    
    # ============================================
    # 2. GERAR FLUXO DE CAIXA
    # ============================================
    
    def gerar_fluxo_caixa(self, escola_id, data_inicio=None, data_fim=None):
        """
        Gera o fluxo de caixa consolidado.
        
        Args:
            escola_id (str): ID da escola
            data_inicio (str, optional): Data inicial (YYYY-MM-DD)
            data_fim (str, optional): Data final (YYYY-MM-DD)
        
        Returns:
            dict: Dicionário com totais
        """
        self.interface.limpar_tela()
        self.interface.mostrar_titulo("📊 FLUXO DE CAIXA - FINAX ERP")
        
        try:
            # Construir query base
            query = self.supabase.table('transacoes')\
                .select('*')\
                .eq('escola_id', escola_id)
            
            if data_inicio:
                query = query.gte('data', data_inicio)
            if data_fim:
                query = query.lte('data', data_fim)
            
            transacoes = query.execute().data
            
            # Buscar receitas do FinaX Pay
            receitas_query = self.supabase.table('receitas')\
                .select('*')\
                .eq('escola_id', escola_id)
            
            if data_inicio:
                receitas_query = receitas_query.gte('data_pagamento', data_inicio)
            if data_fim:
                receitas_query = receitas_query.lte('data_pagamento', data_fim)
            
            receitas = receitas_query.execute().data
            
            # Calcular totais
            total_entradas = sum(t['valor'] for t in transacoes if t['tipo'] == TIPO_ENTRADA)
            total_saidas = sum(t['valor'] for t in transacoes if t['tipo'] == TIPO_SAIDA)
            
            # Lucro do FinaX (2%)
            total_lucro_finax = sum(r['lucro_finax'] for r in receitas)
            
            # Saldo atual
            saldo_atual = total_entradas - total_saidas
            
            # Exibir resumo
            print(f"\n{self.interface.cores.AZUL}{'═'*60}{self.interface.cores.RESET}")
            print(f"{self.interface.cores.CIANO}📈 RESUMO FINANCEIRO{self.interface.cores.RESET}")
            print(f"{self.interface.cores.AZUL}{'═'*60}{self.interface.cores.RESET}")
            
            print(f"\n💰 ENTRADAS:")
            print(f"   Total de Entradas: {self._formatar_valor(total_entradas, is_positivo=True)}")
            
            print(f"\n💸 SAÍDAS:")
            print(f"   Total de Saídas: {self._formatar_valor(total_saidas, is_positivo=False)}")
            
            print(f"\n🏦 SALDO ATUAL:")
            if saldo_atual >= 0:
                print(f"   {self._formatar_valor(saldo_atual, is_positivo=True)}")
            else:
                print(f"   {self._formatar_valor(saldo_atual, is_positivo=False)}")
            
            print(f"\n🤖 LUCRO FINAX (2%):")
            print(f"   {self._formatar_valor(total_lucro_finax, is_positivo=True)}")
            
            # Detalhes por categoria
            print(f"\n{self.interface.cores.AZUL}{'═'*60}{self.interface.cores.RESET}")
            print(f"{self.interface.cores.CIANO}📊 DETALHES POR CATEGORIA{self.interface.cores.RESET}")
            
            # Entradas por categoria
            entradas_por_categoria = {}
            saidas_por_categoria = {}
            
            for t in transacoes:
                if t['tipo'] == TIPO_ENTRADA:
                    entradas_por_categoria[t['categoria']] = entradas_por_categoria.get(t['categoria'], 0) + t['valor']
                else:
                    saidas_por_categoria[t['categoria']] = saidas_por_categoria.get(t['categoria'], 0) + t['valor']
            
            if entradas_por_categoria:
                print(f"\n{self.interface.cores.VERDE}📥 ENTRADAS:{self.interface.cores.RESET}")
                for cat, val in entradas_por_categoria.items():
                    print(f"   {cat}: {self._formatar_valor(val, is_positivo=True)}")
            
            if saidas_por_categoria:
                print(f"\n{self.interface.cores.VERMELHO}📤 SAÍDAS:{self.interface.cores.RESET}")
                for cat, val in saidas_por_categoria.items():
                    print(f"   {cat}: {self._formatar_valor(val, is_positivo=False)}")
            
            return {
                "total_entradas": total_entradas,
                "total_saidas": total_saidas,
                "saldo_atual": saldo_atual,
                "total_lucro_finax": total_lucro_finax
            }
            
        except Exception as e:
            self.interface.exibir_mensagem(f"Erro ao gerar fluxo de caixa: {e}", tipo="erro")
            return None
    
    # ============================================
    # 3. RELATÓRIOS PERIÓDICOS
    # ============================================
    
    def relatorios_periodicos(self, escola_id):
        """
        Gera relatórios financeiros por período.
        
        Args:
            escola_id (str): ID da escola
        """
        self.interface.limpar_tela()
        self.interface.mostrar_titulo("📅 RELATÓRIOS PERIÓDICOS - FINAX ERP")
        
        print("1 - Relatório Diário")
        print("2 - Relatório Mensal")
        print("3 - Relatório Anual")
        print("4 - Período Personalizado")
        
        opcao = self.interface.input_com_validação(
            "\nEscolha uma opção",
            obrigatorio=True,
            tipo="numero"
        )
        
        hoje = datetime.now()
        
        if opcao == "1":
            data = hoje.strftime("%Y-%m-%d")
            self._gerar_relatorio_periodo(escola_id, data, data, "Diário")
            
        elif opcao == "2":
            primeiro_dia = hoje.replace(day=1).strftime("%Y-%m-%d")
            ultimo_dia = hoje.replace(day=28) + timedelta(days=4)
            ultimo_dia = (ultimo_dia - timedelta(days=ultimo_dia.day)).strftime("%Y-%m-%d")
            self._gerar_relatorio_periodo(escola_id, primeiro_dia, ultimo_dia, "Mensal")
            
        elif opcao == "3":
            primeiro_dia = hoje.replace(month=1, day=1).strftime("%Y-%m-%d")
            ultimo_dia = hoje.replace(month=12, day=31).strftime("%Y-%m-%d")
            self._gerar_relatorio_periodo(escola_id, primeiro_dia, ultimo_dia, "Anual")
            
        elif opcao == "4":
            print(f"\n{self.interface.cores.CIANO}Formato: YYYY-MM-DD (ex: 2026-03-01){self.interface.cores.RESET}")
            data_inicio = self.interface.input_com_validação(
                "Data início: ",
                obrigatorio=True
            )
            data_fim = self.interface.input_com_validação(
                "Data fim: ",
                obrigatorio=True
            )
            self._gerar_relatorio_periodo(escola_id, data_inicio, data_fim, "Personalizado")
            
        else:
            self.interface.exibir_mensagem("Opção inválida!", tipo="erro")
    
    def _gerar_relatorio_periodo(self, escola_id, data_inicio, data_fim, titulo):
        """
        Gera relatório para um período específico.
        
        Args:
            escola_id (str): ID da escola
            data_inicio (str): Data inicial
            data_fim (str): Data final
            titulo (str): Título do relatório
        """
        try:
            # Buscar transações
            transacoes = self.supabase.table('transacoes')\
                .select('*')\
                .eq('escola_id', escola_id)\
                .gte('data', data_inicio)\
                .lte('data', data_fim)\
                .order('data', asc=True)\
                .execute().data
            
            # Buscar receitas FinaX
            receitas = self.supabase.table('receitas')\
                .select('*')\
                .eq('escola_id', escola_id)\
                .gte('data_pagamento', data_inicio)\
                .lte('data_pagamento', data_fim)\
                .execute().data
            
            # Calcular totais
            total_entradas = sum(t['valor'] for t in transacoes if t['tipo'] == TIPO_ENTRADA)
            total_saidas = sum(t['valor'] for t in transacoes if t['tipo'] == TIPO_SAIDA)
            total_lucro = sum(r['lucro_finax'] for r in receitas)
            
            # Preparar dados para tabela
            dados_tabela = []
            for t in transacoes:
                valor_formatado = self._formatar_valor(t['valor'], t['tipo'] == TIPO_ENTRADA)
                dados_tabela.append([
                    t['data'],
                    t['categoria'],
                    t['descricao'][:40],
                    t['tipo'],
                    valor_formatado
                ])
            
            self.interface.limpar_tela()
            self.interface.mostrar_titulo(f"📊 RELATÓRIO {titulo} - FINAX ERP")
            print(f"{self.interface.cores.CIANO}Período: {data_inicio} a {data_fim}{self.interface.cores.RESET}")
            print()
            
            if dados_tabela:
                tabela = tabulate(
                    dados_tabela,
                    headers=["DATA", "CATEGORIA", "DESCRIÇÃO", "TIPO", "VALOR"],
                    tablefmt="grid"
                )
                print(tabela)
            else:
                self.interface.mostrar_info("Nenhuma movimentação no período.")
            
            print(f"\n{self.interface.cores.AZUL}{'═'*60}{self.interface.cores.RESET}")
            print(f"💰 Total Entradas: {self._formatar_valor(total_entradas, is_positivo=True)}")
            print(f"💸 Total Saídas: {self._formatar_valor(total_saidas, is_positivo=False)}")
            print(f"🏦 Saldo do Período: {self._formatar_valor(total_entradas - total_saidas, total_entradas >= total_saidas)}")
            print(f"🤖 Lucro FinaX (2%): {self._formatar_valor(total_lucro, is_positivo=True)}")
            
        except Exception as e:
            self.interface.exibir_mensagem(f"Erro ao gerar relatório: {e}", tipo="erro")
    
    # ============================================
    # 4. FOLHA SALARIAL
    # ============================================
    
    def folha_salarial(self, escola_id):
        """
        Gera resumo da folha salarial mensal.
        
        Args:
            escola_id (str): ID da escola
        """
        self.interface.limpar_tela()
        self.interface.mostrar_titulo("👥 FOLHA SALARIAL - FINAX ERP")
        
        try:
            # Buscar transações de salário
            transacoes = self.supabase.table('transacoes')\
                .select('*')\
                .eq('escola_id', escola_id)\
                .eq('categoria', 'Salário')\
                .order('data', desc=True)\
                .execute().data
            
            if not transacoes:
                self.interface.mostrar_info("Nenhum registo salarial encontrado.")
                return
            
            # Agrupar por mês
            salarios_por_mes = {}
            for t in transacoes:
                mes_ano = t['data'][:7]  # YYYY-MM
                salarios_por_mes[mes_ano] = salarios_por_mes.get(mes_ano, 0) + t['valor']
            
            # Preparar dados para tabela
            dados_tabela = []
            for mes_ano, total in sorted(salarios_por_mes.items(), reverse=True):
                data_obj = datetime.strptime(mes_ano, "%Y-%m")
                mes_nome = data_obj.strftime("%B/%Y")
                dados_tabela.append([
                    mes_nome,
                    self._formatar_valor(total, is_positivo=False)
                ])
            
            print(f"\n{self.interface.cores.AZUL}{'═'*60}{self.interface.cores.RESET}")
            tabela = tabulate(
                dados_tabela,
                headers=["MÊS", "TOTAL SALÁRIOS"],
                tablefmt="grid"
            )
            print(tabela)
            
            # Total anual
            total_anual = sum(salarios_por_mes.values())
            print(f"\n{self.interface.cores.AZUL}{'═'*60}{self.interface.cores.RESET}")
            print(f"💰 Total anual com salários: {self._formatar_valor(total_anual, is_positivo=False)}")
            
        except Exception as e:
            self.interface.exibir_mensagem(f"Erro ao gerar folha salarial: {e}", tipo="erro")
    
    # ============================================
    # 5. FUNÇÕES AUXILIARES
    # ============================================
    
    def _formatar_valor(self, valor, is_positivo=True):
        """
        Formata valor com cor adequada.
        
        Args:
            valor (float): Valor a formatar
            is_positivo (bool): True para entrada, False para saída
        
        Returns:
            str: Valor formatado com cor
        """
        if is_positivo:
            return f"{COR_VERDE}{valor:,.2f} Kz{COR_RESET}"
        else:
            return f"{COR_VERMELHO}{valor:,.2f} Kz{COR_RESET}"
    
    # ============================================
    # 6. MENU PRINCIPAL
    # ============================================
    
    def menu(self, escola_id):
        """
        Menu interativo do módulo financeiro.
        
        Args:
            escola_id (str): ID da escola do administrador
        """
        while True:
            self.interface.limpar_tela()
            self.interface.mostrar_titulo("💰 FINAX ERP - GESTÃO FINANCEIRA")
            
            print("1 - 📝 Registar Movimentação")
            print("2 - 📊 Fluxo de Caixa")
            print("3 - 📅 Relatórios Periódicos")
            print("4 - 👥 Folha Salarial")
            print("5 - ⬅️ Voltar ao Menu Principal")
            
            opcao = self.interface.input_com_validação(
                "\nEscolha uma opção",
                obrigatorio=True,
                tipo="numero"
            )
            
            if opcao == "1":
                self.registar_movimentacao(escola_id)
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)
                
            elif opcao == "2":
                self.gerar_fluxo_caixa(escola_id)
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)
                
            elif opcao == "3":
                self.relatorios_periodicos(escola_id)
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)
                
            elif opcao == "4":
                self.folha_salarial(escola_id)
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)
                
            elif opcao == "5":
                break
                
            else:
                self.interface.exibir_mensagem("Opção inválida!", tipo="erro")
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)


# ============================================
# FUNÇÃO DE INTEGRAÇÃO PARA O MAIN
# ============================================

def iniciar_financeiro(escola_id):
    """
    Função de integração para ser chamada pelo main.py
    
    Args:
        escola_id (str): ID da escola do administrador logado
    """
    financeiro = GestaoFinanceira()
    financeiro.menu(escola_id)


# ============================================
# TESTE DO MÓDULO
# ============================================

if __name__ == "__main__":
    print("🧪 Teste do módulo Gestão Financeira (ERP)")
    print("⚠️ Para testar, execute le main.py com um administrador logado.")
    print("   Ou utilize: financeiro = GestaoFinanceira()")