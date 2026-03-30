"""
MÓDULO ALERTAS - FINAX OS
Gestão de notificações importantes da escola

Funcionalidade:
- Criação de comunicados gerais pelo administrador
- Verificação de notificações por perfil (Todos, Estudantes, Administradores)
- Alertas automáticos financeiros
- Filtro por prioridade e período (últimos 7 dias)
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
from utils.interface import Interface

# ============================================
# IMPORTAÇÕES DE TERCEIROS
# ============================================
from tabulate import tabulate

# ============================================
# CONSTANTES
# ============================================

# Destinos possíveis
DESTINO_TODOS = "Todos"
DESTINO_ESTUDANTES = "Estudantes"
DESTINO_ADMINISTRADORES = "Administradores"

# Prioridades
PRIORIDADE_ALTA = "Alta"
PRIORIDADE_MEDIA = "Media"
PRIORIDADE_BAIXA = "Baixa"

# Cores por prioridade
COR_PRIORIDADE = {
    PRIORIDADE_ALTA: "\033[91m",   # Vermelho
    PRIORIDADE_MEDIA: "\033[93m",  # Amarelo
    PRIORIDADE_BAIXA: "\033[92m"   # Verde
}

# Ícones por prioridade
ICONE_PRIORIDADE = {
    PRIORIDADE_ALTA: "🔴",
    PRIORIDADE_MEDIA: "🟡",
    PRIORIDADE_BAIXA: "🟢"
}

# Dias para considerar alertas recentes (últimos 7 dias)
DIAS_RECENTES = 7


# ============================================
# CLASSE PRINCIPAL DE GESTÃO DE ALERTAS
# ============================================

class GestorAlertas:
    """
    Classe responsável pela gestão de notificações da escola.
    
    Funcionalidades:
    - Criação de alertas gerais pelo administrador
    - Verificação de notificações por perfil
    - Alertas automáticos financeiros
    - Filtro por prioridade e período
    """
    
    def __init__(self):
        """Inicializa o módulo com conexão ao banco de dados"""
        self.supabase = db_config.get_client()
        self.interface = Interface()
    
    # ============================================
    # 1. CRIAR ALERTA GERAL (ADMIN)
    # ============================================
    
    def criar_alerta_geral(self, escola_id):
        """
        Cria um comunicado geral para a escola.
        
        Args:
            escola_id (str): ID da escola
        
        Returns:
            dict or None: Dados do alerta criado
        """
        self.interface.limpar_tela()
        self.interface.mostrar_titulo("📢 CRIAR ALERTA / COMUNICADO")
        
        try:
            # Título
            titulo = self.interface.input_com_validação(
                "Título do comunicado: ",
                obrigatorio=True
            )
            
            # Mensagem
            print(f"\n{self.interface.cores.AZUL}📝 MENSAGEM{self.interface.cores.RESET}")
            mensagem = self.interface.input_com_validação(
                "Digite a mensagem: ",
                obrigatorio=True
            )
            
            # Destino
            print(f"\n{self.interface.cores.AZUL}👥 DESTINO{self.interface.cores.RESET}")
            destinos = [DESTINO_TODOS, DESTINO_ESTUDANTES, DESTINO_ADMINISTRADORES]
            for i, d in enumerate(destinos, 1):
                print(f"   {i} - {d}")
            
            destino_opcao = self.interface.input_com_validação(
                "\nEscolha (1-3): ",
                obrigatorio=True,
                tipo="numero"
            )
            
            try:
                destino_idx = int(destino_opcao) - 1
                if destino_idx < 0 or destino_idx >= len(destinos):
                    raise ValueError
                destino = destinos[destino_idx]
            except ValueError:
                self.interface.exibir_mensagem("Destino inválido!", tipo="erro")
                return None
            
            # Prioridade
            print(f"\n{self.interface.cores.AZUL}⚠️ PRIORIDADE{self.interface.cores.RESET}")
            prioridades = [PRIORIDADE_ALTA, PRIORIDADE_MEDIA, PRIORIDADE_BAIXA]
            for i, p in enumerate(prioridades, 1):
                cor = COR_PRIORIDADE.get(p, "")
                print(f"   {i} - {cor}{ICONE_PRIORIDADE[p]} {p}{self.interface.cores.RESET}")
            
            prioridade_opcao = self.interface.input_com_validação(
                "\nEscolha (1-3): ",
                obrigatorio=True,
                tipo="numero"
            )
            
            try:
                prioridade_idx = int(prioridade_opcao) - 1
                if prioridade_idx < 0 or prioridade_idx >= len(prioridades):
                    raise ValueError
                prioridade = prioridades[prioridade_idx]
            except ValueError:
                self.interface.exibir_mensagem("Prioridade inválida!", tipo="erro")
                return None
            
            # Confirmar
            self.interface.mostrar_info("\n📋 CONFIRMAÇÃO")
            print(f"   Título: {titulo}")
            print(f"   Destino: {destino}")
            print(f"   Prioridade: {ICONE_PRIORIDADE[prioridade]} {prioridade}")
            print(f"   Mensagem: {mensagem[:100]}{'...' if len(mensagem) > 100 else ''}")
            
            if not self.interface.confirmar("\nDeseja publicar este comunicado?"):
                self.interface.mostrar_info("Publicação cancelada.")
                return None
            
            # Registrar alerta
            alerta_id = str(uuid.uuid4())
            data_atual = datetime.now().isoformat()
            
            dados_alerta = {
                "id": alerta_id,
                "titulo": titulo,
                "mensagem": mensagem,
                "destino": destino,
                "escola_id": escola_id,
                "data_emissao": data_atual,
                "prioridade": prioridade
            }
            
            resultado = self.supabase.table('alertas').insert(dados_alerta).execute()
            
            if resultado.data:
                print(f"\n{self.interface.cores.VERDE}{self.interface.cores.NEGRITO}")
                print("╔════════════════════════════════════════════════════════════╗")
                print("║  ✅ COMUNICADO PUBLICADO COM SUCESSO!                      ║")
                print("╚════════════════════════════════════════════════════════════╝")
                print(f"{self.interface.cores.RESET}")
                return resultado.data[0]
            else:
                self.interface.exibir_mensagem("Erro ao publicar comunicado.", tipo="erro")
                return None
                
        except Exception as e:
            self.interface.exibir_mensagem(f"Erro ao criar alerta: {e}", tipo="erro")
            return None
    
    # ============================================
    # 2. VERIFICAR NOTIFICAÇÕES (LOGIN)
    # ============================================
    
    def verificar_notificacoes(self, escola_id, nivel_user):
        """
        Verifica e exibe notificações para o utilizador.
        Mostra apenas alertas dos últimos 7 dias.
        
        Args:
            escola_id (str): ID da escola
            nivel_user (str): Nível do utilizador ('Estudante' ou 'Administrador')
        
        Returns:
            list: Lista de alertas para o utilizador
        """
        # Data limite (últimos 7 dias)
        data_limite = (datetime.now() - timedelta(days=DIAS_RECENTES)).isoformat()
        
        try:
            # Buscar alertas para o nível do utilizador
            alertas = self.supabase.table('alertas')\
                .select('*')\
                .eq('escola_id', escola_id)\
                .gte('data_emissao', data_limite)\
                .in_('destino', [DESTINO_TODOS, nivel_user])\
                .order('data_emissao', desc=True)\
                .execute().data
            
            if not alertas:
                return []
            
            # Exibir alertas
            self._exibir_alertas(alertas)
            return alertas
            
        except Exception as e:
            self.interface.exibir_mensagem(f"Erro ao verificar notificações: {e}", tipo="erro")
            return []
    
    def _exibir_alertas(self, alertas):
        """
        Exibe os alertas num quadro visual.
        
        Args:
            alertas (list): Lista de alertas
        """
        print(f"\n{self.interface.cores.CIANO}{self.interface.cores.NEGRITO}")
        print("╔════════════════════════════════════════════════════════════╗")
        print("║  🔔 NOVAS NOTIFICAÇÕES                                     ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print(f"{self.interface.cores.RESET}")
        
        for alerta in alertas:
            # Formatar data
            try:
                data_obj = datetime.fromisoformat(alerta['data_emissao'])
                data_formatada = data_obj.strftime("%d/%m/%Y às %H:%M")
            except:
                data_formatada = alerta['data_emissao'][:16] if alerta['data_emissao'] else "N/A"
            
            # Cor e ícone por prioridade
            prioridade = alerta['prioridade']
            cor = COR_PRIORIDADE.get(prioridade, "")
            icone = ICONE_PRIORIDADE.get(prioridade, "📢")
            
            # Título com destaque para prioridade alta
            if prioridade == PRIORIDADE_ALTA:
                titulo_display = f"{cor}{self.interface.cores.NEGRITO}{icone} {alerta['titulo']}{self.interface.cores.RESET}"
            else:
                titulo_display = f"{cor}{icone} {alerta['titulo']}{self.interface.cores.RESET}"
            
            print(f"\n{self.interface.cores.AZUL}{'─'*60}{self.interface.cores.RESET}")
            print(f"{titulo_display}")
            print(f"{self.interface.cores.CIANO}📅 {data_formatada}{self.interface.cores.RESET}")
            print(f"\n{alerta['mensagem']}")
            print(f"\n{self.interface.cores.AMARELO}🎯 Destino: {alerta['destino']}{self.interface.cores.RESET}")
    
    # ============================================
    # 3. ALERTAS AUTOMÁTICOS FINANCEIROS
    # ============================================
    
    def alertas_automaticos_financeiros(self, aluno_id):
        """
        Gera alerta automático se o aluno tiver débitos pendentes.
        
        Args:
            aluno_id (str): ID do aluno
        
        Returns:
            dict or None: Alerta gerado
        """
        try:
            # Buscar dados do aluno
            aluno = self.supabase.table('usuarios')\
                .select('nome, tem_divida, escola_id')\
                .eq('id', aluno_id)\
                .execute().data
            
            if not aluno:
                return None
            
            aluno = aluno[0]
            
            # Verificar se tem débito
            if aluno.get('tem_divida'):
                # Criar alerta automático
                alerta_id = str(uuid.uuid4())
                data_atual = datetime.now().isoformat()
                
                dados_alerta = {
                    "id": alerta_id,
                    "titulo": "⚠️ Pagamento Pendente",
                    "mensagem": f"Olá {aluno['nome']}! Tens pagamentos pendentes no FinaX Pay. Regularize sua situação para evitar restrições.",
                    "destino": DESTINO_ESTUDANTES,
                    "escola_id": aluno['escola_id'],
                    "data_emissao": data_atual,
                    "prioridade": PRIORIDADE_ALTA
                }
                
                # Verificar se já existe alerta similar nos últimos 3 dias
                data_limite = (datetime.now() - timedelta(days=3)).isoformat()
                alerta_existente = self.supabase.table('alertas')\
                    .select('id')\
                    .eq('escola_id', aluno['escola_id'])\
                    .eq('titulo', "⚠️ Pagamento Pendente")\
                    .eq('aluno_id', aluno_id)\
                    .gte('data_emissao', data_limite)\
                    .execute().data
                
                if not alerta_existente:
                    resultado = self.supabase.table('alertas').insert(dados_alerta).execute()
                    return resultado.data[0] if resultado.data else None
                
        except Exception as e:
            self.interface.exibir_mensagem(f"Erro ao gerar alerta financeiro: {e}", tipo="erro")
        
        return None
    
    # ============================================
    # 4. LISTAR TODOS OS ALERTAS (ADMIN)
    # ============================================
    
    def listar_todos_alertas(self, escola_id):
        """
        Lista todos os alertas da escola (admin).
        
        Args:
            escola_id (str): ID da escola
        """
        self.interface.limpar_tela()
        self.interface.mostrar_titulo("📋 HISTÓRICO DE ALERTAS")
        
        try:
            alertas = self.supabase.table('alertas')\
                .select('*')\
                .eq('escola_id', escola_id)\
                .order('data_emissao', desc=True)\
                .execute().data
            
            if not alertas:
                self.interface.mostrar_info("Nenhum alerta registado.")
                return
            
            # Preparar dados para tabela
            dados_tabela = []
            for a in alertas:
                try:
                    data_obj = datetime.fromisoformat(a['data_emissao'])
                    data_formatada = data_obj.strftime("%d/%m/%Y %H:%M")
                except:
                    data_formatada = a['data_emissao'][:16] if a['data_emissao'] else "N/A"
                
                cor = COR_PRIORIDADE.get(a['prioridade'], "")
                prioridade_display = f"{cor}{ICONE_PRIORIDADE[a['prioridade']]} {a['prioridade']}{self.interface.cores.RESET}"
                
                dados_tabela.append([
                    a['id'][:8],
                    data_formatada,
                    prioridade_display,
                    a['destino'],
                    a['titulo'][:30] + ("..." if len(a['titulo']) > 30 else "")
                ])
            
            tabela = tabulate(
                dados_tabela,
                headers=["ID", "DATA", "PRIORIDADE", "DESTINO", "TÍTULO"],
                tablefmt="grid"
            )
            print(f"\n{tabela}")
            
            print(f"\n{self.interface.cores.AZUL}{'═'*60}{self.interface.cores.RESET}")
            print(f"📊 Total de alertas: {len(alertas)}")
            
        except Exception as e:
            self.interface.exibir_mensagem(f"Erro ao listar alertas: {e}", tipo="erro")
    
    # ============================================
    # 5. MENU PRINCIPAL (ADMIN)
    # ============================================
    
    def menu_admin(self, escola_id):
        """
        Menu interativo para administradores.
        
        Args:
            escola_id (str): ID da escola
        """
        while True:
            self.interface.limpar_tela()
            self.interface.mostrar_titulo("🔔 GESTÃO DE ALERTAS - FINAX OS")
            
            print("\n1 - 📢 Criar Novo Comunicado")
            print("2 - 📋 Ver Histórico de Alertas")
            print("3 - ⬅️ Voltar")
            
            opcao = self.interface.input_com_validação(
                "\nEscolha uma opção",
                obrigatorio=True,
                tipo="numero"
            )
            
            if opcao == "1":
                self.criar_alerta_geral(escola_id)
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)
            elif opcao == "2":
                self.listar_todos_alertas(escola_id)
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)
            elif opcao == "3":
                break
            else:
                self.interface.exibir_mensagem("Opção inválida!", tipo="erro")
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)
    
    # ============================================
    # 6. FUNÇÃO DE INTEGRAÇÃO COM SESSÃO
    # ============================================
    
    def verificar_e_exibir_notificacoes_login(self, sessao):
        """
        Função chamada no login para exibir notificações.
        
        Args:
            sessao (dict): Dados da sessão do utilizador
        """
        escola_id = sessao.get('escola')
        nivel = sessao.get('nivel')
        
        if escola_id and nivel:
            alertas = self.verificar_notificacoes(escola_id, nivel)
            if alertas:
                input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)
    
    def menu_por_perfil(self, sessao):
        """
        Menu adaptado ao perfil do utilizador.
        
        Args:
            sessao (dict): Dados da sessão do utilizador
        """
        nivel = sessao.get('nivel')
        escola_id = sessao.get('escola')
        
        if nivel == 'Administrador':
            self.menu_admin(escola_id)
        else:
            # Para alunos, mostrar apenas alertas recentes
            self.interface.limpar_tela()
            self.verificar_notificacoes(escola_id, nivel)
            input("\n" + self.interface.cores.AMARELO + "Pressione ENTER para continuar..." + self.interface.cores.RESET)


# ============================================
# FUNÇÃO DE INTEGRAÇÃO PARA O MAIN
# ============================================

def iniciar_alertas(sessao):
    """
    Função de integração para ser chamada pelo main.py
    
    Args:
        sessao (dict): Dados da sessão do utilizador logado
    """
    alertas = GestorAlertas()
    alertas.menu_por_perfil(sessao)


# ============================================
# FUNÇÃO PARA VERIFICAR NOTIFICAÇÕES NO LOGIN
# ============================================

def verificar_notificacoes_login(sessao):
    """
    Função chamada no momento do login para exibir notificações.
    
    Args:
        sessao (dict): Dados da sessão do utilizador
    """
    alertas = GestorAlertas()
    alertas.verificar_e_exibir_notificacoes_login(sessao)


# ============================================
# TESTE DO MÓDULO
# ============================================

if __name__ == "__main__":
    print("🧪 Teste do módulo Gestão de Alertas")
    print("⚠️ Para testar, execute o main.py com um utilizador logado.")
    print("   Ou utilize: alertas = GestorAlertas()")