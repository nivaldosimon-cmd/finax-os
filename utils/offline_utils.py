"""
MÓDULO OFFLINE_UTILS - FINAX OS
Cache Local para operações sem internet

Funcionalidade:
- Salvar operações localmente quando offline
- Sincronizar com Supabase quando a conexão retorna
- Gerenciar fila de operações pendentes
- Modo offline ativo com aviso visual
"""

import os
import sys
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

# Adiciona a pasta raiz ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================
# IMPORTAÇÕES DOS MÓDULOS INTERNOS
# ============================================


# ============================================
# CONSTANTES
# ============================================

# Arquivos de cache
PASTA_CACHE = "cache"
ARQUIVO_PENDENTES = os.path.join(PASTA_CACHE, "operacoes_pendentes.json")
ARQUIVO_CONFIG = os.path.join(PASTA_CACHE, "offline_config.json")

# Mensagens
MSG_MODO_OFFLINE_ATIVO = "⚠️ MODO OFFLINE ATIVO: Dados salvos localmente"
MSG_MODO_ONLINE_RESTAURADO = "✅ Modo Online restaurado! Sincronizando dados..."
MSG_SINCRONIZACAO_SUCESSO = "✅ Dados sincronizados com sucesso!"
MSG_SINCRONIZACAO_ERRO = "❌ Erro ao sincronizar: {}"
MSG_SEM_PENDENTES = "📭 Nenhuma operação pendente para sincronizar."


# ============================================
# CLASSE PRINCIPAL DE OFFLINE UTILS
# ============================================

class OfflineUtils:
    """
    Classe responsável por cache local e sincronização offline.
    
    Funcionalidades:
    - Salvar operações localmente em JSON
    - Gerenciar fila de operações pendentes
    - Sincronizar com Supabase quando online
    - Modo offline ativo com aviso visual
    """
    
    def __init__(self):
        """Inicializa o módulo de cache offline"""
        
        self._criar_pasta_cache()
        self._carregar_pendentes()
        self._modo_offline = False
    
    # ============================================
    # 1. GESTÃO DE PASTA E ARQUIVOS
    # ============================================
    
    def _criar_pasta_cache(self):
        """Cria a pasta de cache se não existir"""
        if not os.path.exists(PASTA_CACHE):
            os.makedirs(PASTA_CACHE)
            print(f"📁 Pasta de cache criada: {PASTA_CACHE}")
    
    def _carregar_pendentes(self) -> List[Dict]:
        """
        Carrega operações pendentes do arquivo JSON.
        
        Returns:
            list: Lista de operações pendentes
        """
        if os.path.exists(ARQUIVO_PENDENTES):
            try:
                with open(ARQUIVO_PENDENTES, 'r', encoding='utf-8') as f:
                    self.pendentes = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.pendentes = []
        else:
            self.pendentes = []
        
        return self.pendentes
    
    def _salvar_pendentes(self):
        """
        Salva operações pendentes no arquivo JSON.
        """
        try:
            with open(ARQUIVO_PENDENTES, 'w', encoding='utf-8') as f:
                json.dump(self.pendentes, f, ensure_ascii=False, indent=2)
        except IOError as e:
            self.interface.exibir_mensagem(f"Erro ao salvar cache: {e}", tipo="erro")
    
    # ============================================
    # 2. SALVAR OPERAÇÃO OFFLINE
    # ============================================
    
    def salvar_offline(self, tipo: str, dados: Dict, tabela: str = None) -> str:
        """
        Salva uma operação localmente para sincronização futura.
        
        Args:
            tipo (str): Tipo de operação ('INSERT', 'UPDATE', 'DELETE')
            dados (dict): Dados da operação
            tabela (str): Nome da tabela no Supabase
        
        Returns:
            str: ID da operação pendente
        """
        # Gerar ID único para a operação
        operacao_id = str(uuid.uuid4())
        
        # Criar registro da operação
        operacao = {
            "id": operacao_id,
            "tipo": tipo,
            "tabela": tabela,
            "dados": dados,
            "timestamp": datetime.now().isoformat(),
            "status": "pendente"
        }
        
        # Adicionar à fila
        self.pendentes.append(operacao)
        self._salvar_pendentes()
        
        # Ativar modo offline visual
        if not self._modo_offline:
            self._modo_offline = True
            self._exibir_aviso_offline()
        
        return operacao_id
    
    def _exibir_aviso_offline(self):
        """
        Exibe aviso visual de modo offline ativo.
        """
        print(f"\n{self.interface.cores.AMARELO}{self.interface.cores.NEGRITO}")
        print("╔════════════════════════════════════════════════════════════╗")
        print("║  ⚠️  MODO OFFLINE ATIVO                                    ║")
        print("║                                                            ║")
        print("║  Sem conexão com a internet.                               ║")
        print("║  Suas operações estão sendo salvas localmente.             ║")
        print("║  Os dados serão sincronizados quando a conexão voltar.     ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print(f"{self.interface.cores.RESET}")
    
    # ============================================
    # 3. SINCronizar COM ONLINE
    # ============================================
    
    def sincronizar_online(self, supabase_client=None) -> Dict[str, Any]:
        """
        Tenta sincronizar todas as operações pendentes com o Supabase.
        
        Args:
            supabase_client: Cliente Supabase (opcional)
        
        Returns:
            dict: Resultado da sincronização
        """
        if not self.pendentes:
            self.interface.mostrar_info(MSG_SEM_PENDENTES)
            return {"sincronizados": 0, "erros": 0, "pendentes": 0}
        
        if supabase_client is None:
            try:
                from modules.database_config import db_config
                supabase_client = db_config.get_client()
            except ImportError:
                self.interface.exibir_mensagem(
                    "Não foi possível conectar ao Supabase.",
                    tipo="erro"
                )
                return {"sincronizados": 0, "erros": len(self.pendentes), "pendentes": len(self.pendentes)}
        
        self.interface.mostrar_processando("Sincronizando dados com o servidor...")
        
        sincronizados = 0
        erros = 0
        pendentes_atualizados = []
        
        for operacao in self.pendentes:
            try:
                sucesso = self._executar_operacao(supabase_client, operacao)
                
                if sucesso:
                    sincronizados += 1
                    # Não adicionar à nova lista (operação concluída)
                else:
                    erros += 1
                    pendentes_atualizados.append(operacao)
                    
            except Exception as e:
                erros += 1
                operacao["erro"] = str(e)
                pendentes_atualizados.append(operacao)
                self.interface.exibir_mensagem(
                    f"Erro na operação {operacao['id']}: {e}",
                    tipo="erro"
                )
        
        # Atualizar lista de pendentes
        self.pendentes = pendentes_atualizados
        self._salvar_pendentes()
        
        # Verificar se ainda há pendentes
        if self.pendentes:
            self._modo_offline = True
            self.interface.exibir_mensagem(
                f"⚠️ {len(self.pendentes)} operação(ões) ainda pendentes.",
                tipo="info"
            )
        else:
            self._modo_offline = False
            self.interface.mostrar_sucesso(MSG_SINCRONIZACAO_SUCESSO)
        
        resultado = {
            "sincronizados": sincronizados,
            "erros": erros,
            "pendentes": len(self.pendentes)
        }
        
        return resultado
    
    def _executar_operacao(self, client, operacao: Dict) -> bool:
        """
        Executa uma operação no Supabase.
        
        Args:
            client: Cliente Supabase
            operacao (dict): Dados da operação
        
        Returns:
            bool: True se sucesso
        """
        tabela = operacao.get("tabela")
        dados = operacao.get("dados", {})
        tipo = operacao.get("tipo")
        
        if not tabela:
            return False
        
        if tipo == "INSERT":
            # Remover ID se presente (deixar Supabase gerar)
            if "id" in dados:
                dados.pop("id")
            result = client.table(tabela).insert(dados).execute()
            return bool(result.data)
            
        elif tipo == "UPDATE":
            operacao_id = dados.get("id")
            if not operacao_id:
                return False
            result = client.table(tabela).update(dados).eq("id", operacao_id).execute()
            return bool(result.data)
            
        elif tipo == "DELETE":
            operacao_id = dados.get("id")
            if not operacao_id:
                return False
            result = client.table(tabela).delete().eq("id", operacao_id).execute()
            return bool(result.data)
        
        return False
    
    # ============================================
    # 4. FUNÇÕES DE CONVENIÊNCIA
    # ============================================
    
    def esta_offline(self) -> bool:
        """
        Verifica se o sistema está em modo offline.
        
        Returns:
            bool: True se offline
        """
        return self._modo_offline or len(self.pendentes) > 0
    
    def tem_pendentes(self) -> bool:
        """
        Verifica se há operações pendentes.
        
        Returns:
            bool: True se há pendentes
        """
        return len(self.pendentes) > 0
    
    def listar_pendentes(self) -> List[Dict]:
        """
        Retorna lista de operações pendentes.
        
        Returns:
            list: Lista de operações pendentes
        """
        return self.pendentes.copy()
    
    def limpar_cache(self) -> bool:
        """
        Limpa todo o cache de operações pendentes.
        
        Returns:
            bool: True se sucesso
        """
        try:
            self.pendentes = []
            self._salvar_pendentes()
            self._modo_offline = False
            self.interface.mostrar_sucesso("Cache limpo com sucesso!")
            return True
        except Exception as e:
            self.interface.exibir_mensagem(f"Erro ao limpar cache: {e}", tipo="erro")
            return False
    
    def exibir_relatorio_pendentes(self):
        """
        Exibe relatório de operações pendentes.
        """
        if not self.pendentes:
            self.interface.mostrar_info("Nenhuma operação pendente.")
            return
        
        self.interface.mostrar_titulo("📋 OPERAÇÕES PENDENTES")
        
        print(f"\n{self.interface.cores.CIANO}{'─'*60}{self.interface.cores.RESET}")
        
        for i, op in enumerate(self.pendentes, 1):
            print(f"\n{i}. ID: {op['id'][:8]}...")
            print(f"   Tipo: {op['tipo']}")
            print(f"   Tabela: {op['tabela']}")
            print(f"   Data: {op['timestamp'][:19]}")
            
            # Mostrar resumo dos dados
            dados = op.get('dados', {})
            if 'nome' in dados:
                print(f"   Aluno: {dados['nome']}")
            elif 'titulo' in dados:
                print(f"   Título: {dados['titulo'][:40]}")
            
            if op.get('erro'):
                print(f"   ❌ Erro: {op['erro']}")
        
        print(f"\n{self.interface.cores.CIANO}{'─'*60}{self.interface.cores.RESET}")
        print(f"📊 Total: {len(self.pendentes)} operação(ões) pendente(s)")
    
    def obter_estatisticas(self) -> Dict:
        """
        Retorna estatísticas do cache offline.
        
        Returns:
            dict: Estatísticas
        """
        tipos = {}
        for op in self.pendentes:
            tipo = op.get('tipo', 'DESCONHECIDO')
            tipos[tipo] = tipos.get(tipo, 0) + 1
        
        return {
            "total_pendentes": len(self.pendentes),
            "por_tipo": tipos,
            "modo_offline": self._modo_offline,
            "pasta_cache": PASTA_CACHE
        }


# ============================================
# FUNÇÕES DE CONVENIÊNCIA (API SIMPLES)
# ============================================

# Instância global (singleton)
_offline_instance = None

def get_offline_utils() -> OfflineUtils:
    """
    Retorna a instância global do OfflineUtils.
    
    Returns:
        OfflineUtils: Instância singleton
    """
    global _offline_instance
    if _offline_instance is None:
        _offline_instance = OfflineUtils()
    return _offline_instance


def salvar_offline(tipo: str, dados: Dict, tabela: str = None) -> str:
    """
    Função de conveniência para salvar operação offline.
    
    Args:
        tipo (str): Tipo de operação
        dados (dict): Dados da operação
        tabela (str): Nome da tabela
    
    Returns:
        str: ID da operação
    """
    offline = get_offline_utils()
    return offline.salvar_offline(tipo, dados, tabela)


def sincronizar_online(supabase_client=None) -> Dict:
    """
    Função de conveniência para sincronizar.
    
    Args:
        supabase_client: Cliente Supabase
    
    Returns:
        dict: Resultado da sincronização
    """
    offline = get_offline_utils()
    return offline.sincronizar_online(supabase_client)


def esta_offline() -> bool:
    """
    Verifica se está em modo offline.
    
    Returns:
        bool: True se offline
    """
    offline = get_offline_utils()
    return offline.esta_offline()


def tem_pendentes() -> bool:
    """
    Verifica se há operações pendentes.
    
    Returns:
        bool: True se há pendentes
    """
    offline = get_offline_utils()
    return offline.tem_pendentes()


# ============================================
# TESTE DO MÓDULO
# ============================================

if __name__ == "__main__":
    print("🧪 Teste do módulo Offline Utils")
    print("=" * 60)
    
    offline = OfflineUtils()
    
    # Testar salvar operações offline
    print("\n📝 TESTE DE SALVAMENTO OFFLINE:")
    print("-" * 40)
    
    # Simular operações offline
    offline.salvar_offline("INSERT", {"nome": "João Teste", "turma": "10ªA"}, "alunos")
    offline.salvar_offline("INSERT", {"nome": "Maria Teste", "turma": "10ªB"}, "alunos")
    offline.salvar_offline("UPDATE", {"id": "123", "status": "pago"}, "mensalidades")
    
    print(f"✅ {len(offline.listar_pendentes())} operações salvas localmente")
    
    # Listar pendentes
    offline.exibir_relatorio_pendentes()
    
    # Testar estatísticas
    print("\n📊 ESTATÍSTICAS DO CACHE:")
    print("-" * 40)
    stats = offline.obter_estatisticas()
    for k, v in stats.items():
        print(f"   {k}: {v}")
    
    # Testar limpeza
    print("\n🧹 LIMPANDO CACHE:")
    print("-" * 40)
    offline.limpar_cache()
    print(f"   Pendentes após limpeza: {offline.tem_pendentes()}")
    
    print("\n✅ Teste concluído!")