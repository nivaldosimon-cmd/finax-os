"""
MÓDULO WHATSAPP_UTILS - FINAX OS
Integração com WhatsApp para envio de alertas

Funcionalidade:
- Envio de alertas de pagamento pendente via WhatsApp
- Geração de links wa.me para mensagens prontas
- Abertura automática no navegador
- Suporte a múltiplos formatos de número
"""

import sys
import os
import webbrowser
import re
from typing import Optional, List

# Adiciona a pasta raiz ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================
# IMPORTAÇÕES DOS MÓDULOS INTERNOS
# ============================================


# ============================================
# CONSTANTES
# ============================================

# URL base do WhatsApp Web
WHATSAPP_BASE_URL = "https://wa.me/"

# Mensagens padrão
MENSAGEM_PADRAO_PAGAMENTO = "Olá, informamos que a propina do aluno {} está pendente no FinaX OS."
MENSAGEM_PADRAO_ATRASO = "Olá, o aluno {} registou atraso hoje. Por favor, verifique."
MENSAGEM_PADRAO_RISCO = "Olá, o aluno {} está em risco de reprovação. Contacte a escola."

# Código de país padrão (Angola: +244)
CODIGO_PAIS_PADRAO = "244"

# Tamanho mínimo do número (sem código do país)
TAMANHO_MIN_NUMERO = 9
TAMANHO_MAX_NUMERO = 12

# Mensagens de erro
MSG_NUMERO_INVALIDO = "Número de telefone inválido. Use formato: 9XX XXX XXX"
MSG_SEM_NAVEGADOR = "Não foi possível abrir o navegador."
MSG_ENVIO_SUCESSO = "✅ Alerta WhatsApp preparado! Abrindo navegador..."
MSG_ENVIO_CANCELADO = "Envio cancelado."


# ============================================
# CLASSE PRINCIPAL DE WHATSAPP UTILS
# ============================================

class WhatsAppUtils:
    """
    Classe responsável por integração com WhatsApp.
    
    Funcionalidades:
    - Envio de alertas de pagamento pendente
    - Geração de links wa.me
    - Abertura automática no navegador
    - Validação de números de telefone
    """
    
    def __init__(self):
        """Inicializa o módulo de WhatsApp"""
        
    # ============================================
    # 1. VALIDAÇÃO DE NÚMEROS
    # ============================================
    
    def validar_numero(self, numero: str) -> bool:
        """
        Valida se o número de telefone está em formato aceitável.
        
        Args:
            numero (str): Número de telefone
        
        Returns:
            bool: True se válido
        """
        # Remover espaços e caracteres especiais
        numero_limpo = self.limpar_numero(numero)
        
        # Verificar se contém apenas dígitos
        if not numero_limpo.isdigit():
            return False
        
        # Verificar tamanho
        if len(numero_limpo) < TAMANHO_MIN_NUMERO or len(numero_limpo) > TAMANHO_MAX_NUMERO + 3:
            return False
        
        return True
    
    def limpar_numero(self, numero: str) -> str:
        """
        Limpa o número de telefone removendo espaços e caracteres especiais.
        
        Args:
            numero (str): Número bruto
        
        Returns:
            str: Número limpo
        """
        # Remover espaços
        numero = numero.strip()
        
        # Remover + se existir
        if numero.startswith('+'):
            numero = numero[1:]
        
        # Remover caracteres não numéricos
        numero = re.sub(r'[^0-9]', '', numero)
        
        return numero
    
    def formatar_numero_internacional(self, numero: str, codigo_pais: str = CODIGO_PAIS_PADRAO) -> str:
        """
        Formata o número para o formato internacional (sem +).
        
        Args:
            numero (str): Número de telefone
            codigo_pais (str): Código do país
        
        Returns:
            str: Número formatado
        """
        numero_limpo = self.limpar_numero(numero)
        
        # Remover código do país se já estiver presente
        if numero_limpo.startswith(codigo_pais):
            numero_limpo = numero_limpo[len(codigo_pais):]
        
        # Garantir que o número não começa com zero
        if numero_limpo.startswith('0'):
            numero_limpo = numero_limpo[1:]
        
        # Combinar com código do país
        return f"{codigo_pais}{numero_limpo}"
    
    # ============================================
    # 2. GERAÇÃO DE LINK E MENSAGEM
    # ============================================
    
    def gerar_link_whatsapp(self, numero: str, mensagem: str) -> str:
        """
        Gera o link wa.me para abrir o WhatsApp.
        
        Args:
            numero (str): Número de telefone (formato internacional sem +)
            mensagem (str): Mensagem a ser enviada
        
        Returns:
            str: URL completa do WhatsApp
        """
        # Limpar e formatar número
        numero_limpo = self.limpar_numero(numero)
        
        # Remover + se existir
        if numero_limpo.startswith('+'):
            numero_limpo = numero_limpo[1:]
        
        # Codificar mensagem para URL
        mensagem_codificada = self._codificar_mensagem(mensagem)
        
        # Construir URL
        url = f"{WHATSAPP_BASE_URL}{numero_limpo}?text={mensagem_codificada}"
        
        return url
    
    def _codificar_mensagem(self, mensagem: str) -> str:
        """
        Codifica a mensagem para URL.
        
        Args:
            mensagem (str): Mensagem em texto plano
        
        Returns:
            str: Mensagem codificada para URL
        """
        # Substituir espaços por %20
        mensagem_codificada = mensagem.replace(' ', '%20')
        
        # Substituir caracteres especiais
        caracteres_especiais = {
            'á': '%C3%A1',
            'é': '%C3%A9',
            'í': '%C3%AD',
            'ó': '%C3%B3',
            'ú': '%C3%BA',
            'ã': '%C3%A3',
            'õ': '%C3%B5',
            'â': '%C3%A2',
            'ê': '%C3%AA',
            'ô': '%C3%B4',
            'ç': '%C3%A7',
            'Á': '%C3%81',
            'É': '%C3%89',
            'Í': '%C3%8D',
            'Ó': '%C3%93',
            'Ú': '%C3%9A',
            'Ã': '%C3%83',
            'Õ': '%C3%95',
            'Â': '%C3%82',
            'Ê': '%C3%8A',
            'Ô': '%C3%94',
            'Ç': '%C3%87',
            '?': '%3F',
            '!': '%21',
            '.': '%2E',
            ',': '%2C',
            ':': '%3A',
            ';': '%3B',
            '(': '%28',
            ')': '%29',
            '[': '%5B',
            ']': '%5D',
            '{': '%7B',
            '}': '%7D',
            '/': '%2F',
            '\\': '%5C',
            '&': '%26',
            '=': '%3D',
            '+': '%2B',
            '#': '%23',
            '$': '%24',
            '@': '%40'
        }
        
        for char, codificado in caracteres_especiais.items():
            mensagem_codificada = mensagem_codificada.replace(char, codificado)
        
        return mensagem_codificada
    
    # ============================================
    # 3. ENVIO DE ALERTAS
    # ============================================
    
    def enviar_alerta_pagamento(self, numero: str, nome_aluno: str, valor: float = None) -> bool:
        """
        Envia alerta de pagamento pendente via WhatsApp.
        
        Args:
            numero (str): Número de telefone do responsável
            nome_aluno (str): Nome do aluno
            valor (float, optional): Valor pendente
        
        Returns:
            bool: True se sucesso (abriu navegador)
        """
        # Validar número
        if not self.validar_numero(numero):
            self.interface.exibir_mensagem(MSG_NUMERO_INVALIDO, tipo="erro")
            return False
        
        # Construir mensagem
        if valor:
            mensagem = f"Olá, informamos que a propina do aluno {nome_aluno} no valor de {valor:,.2f} Kz está pendente no FinaX OS. Por favor, regularize a situação."
        else:
            mensagem = MENSAGEM_PADRAO_PAGAMENTO.format(nome_aluno)
        
        return self._enviar_mensagem(numero, mensagem)
    
    def enviar_alerta_atraso(self, numero: str, nome_aluno: str, hora: str = None) -> bool:
        """
        Envia alerta de atraso do aluno.
        
        Args:
            numero (str): Número de telefone do responsável
            nome_aluno (str): Nome do aluno
            hora (str, optional): Hora do atraso
        
        Returns:
            bool: True se sucesso
        """
        # Validar número
        if not self.validar_numero(numero):
            self.interface.exibir_mensagem(MSG_NUMERO_INVALIDO, tipo="erro")
            return False
        
        # Construir mensagem
        if hora:
            mensagem = f"Olá, o aluno {nome_aluno} registou atraso às {hora} hoje. Por favor, verifique."
        else:
            mensagem = MENSAGEM_PADRAO_ATRASO.format(nome_aluno)
        
        return self._enviar_mensagem(numero, mensagem)
    
    def enviar_alerta_risco(self, numero: str, nome_aluno: str, media: float = None) -> bool:
        """
        Envia alerta de risco de reprovação.
        
        Args:
            numero (str): Número de telefone do responsável
            nome_aluno (str): Nome do aluno
            media (float, optional): Média do aluno
        
        Returns:
            bool: True se sucesso
        """
        # Validar número
        if not self.validar_numero(numero):
            self.interface.exibir_mensagem(MSG_NUMERO_INVALIDO, tipo="erro")
            return False
        
        # Construir mensagem
        if media:
            mensagem = f"Olá, o aluno {nome_aluno} está em risco de reprovação com média {media:.1f}. Contacte a escola para mais informações."
        else:
            mensagem = MENSAGEM_PADRAO_RISCO.format(nome_aluno)
        
        return self._enviar_mensagem(numero, mensagem)
    
    def enviar_mensagem_personalizada(self, numero: str, mensagem: str) -> bool:
        """
        Envia mensagem personalizada via WhatsApp.
        
        Args:
            numero (str): Número de telefone
            mensagem (str): Mensagem personalizada
        
        Returns:
            bool: True se sucesso
        """
        # Validar número
        if not self.validar_numero(numero):
            self.interface.exibir_mensagem(MSG_NUMERO_INVALIDO, tipo="erro")
            return False
        
        return self._enviar_mensagem(numero, mensagem)
    
    def _enviar_mensagem(self, numero: str, mensagem: str) -> bool:
        """
        Função interna para enviar mensagem via WhatsApp.
        
        Args:
            numero (str): Número de telefone
            mensagem (str): Mensagem a ser enviada
        
        Returns:
            bool: True se sucesso
        """
        # Formatar número
        numero_formatado = self.formatar_numero_internacional(numero)
        
        # Gerar link
        url = self.gerar_link_whatsapp(numero_formatado, mensagem)
        
        # Exibir informações
        self.interface.mostrar_sucesso(MSG_ENVIO_SUCESSO)
        print(f"\n{self.interface.cores.CIANO}📱 Número: +{numero_formatado}{self.interface.cores.RESET}")
        print(f"{self.interface.cores.CIANO}💬 Mensagem: {mensagem[:80]}{'...' if len(mensagem) > 80 else ''}{self.interface.cores.RESET}")
        
        # Perguntar se deseja abrir
        if not self.interface.confirmar("\nAbrir WhatsApp no navegador?"):
            self.interface.mostrar_info(MSG_ENVIO_CANCELADO)
            return False
        
        # Abrir navegador
        try:
            webbrowser.open(url)
            return True
        except Exception as e:
            self.interface.exibir_mensagem(f"{MSG_SEM_NAVEGADOR} {e}", tipo="erro")
            return False
    
    # ============================================
    # 4. FUNÇÕES DE LOTE
    # ============================================
    
    def enviar_alertas_lote(self, alertas: List[dict]) -> dict:
        """
        Envia múltiplos alertas em lote.
        
        Args:
            alertas (list): Lista de dicionários com 'numero', 'tipo', 'nome_aluno', 'valor'
        
        Returns:
            dict: Resultado do envio
        """
        enviados = 0
        falhas = 0
        
        for alerta in alertas:
            numero = alerta.get('numero')
            tipo = alerta.get('tipo', 'pagamento')
            nome_aluno = alerta.get('nome_aluno', '')
            valor = alerta.get('valor')
            hora = alerta.get('hora')
            media = alerta.get('media')
            
            if not numero or not nome_aluno:
                falhas += 1
                continue
            
            if tipo == 'pagamento':
                sucesso = self.enviar_alerta_pagamento(numero, nome_aluno, valor)
            elif tipo == 'atraso':
                sucesso = self.enviar_alerta_atraso(numero, nome_aluno, hora)
            elif tipo == 'risco':
                sucesso = self.enviar_alerta_risco(numero, nome_aluno, media)
            else:
                sucesso = False
            
            if sucesso:
                enviados += 1
            else:
                falhas += 1
        
        return {
            "enviados": enviados,
            "falhas": falhas,
            "total": len(alertas)
        }


# ============================================
# FUNÇÕES DE CONVENIÊNCIA (API SIMPLES)
# ============================================

# Instância global
_whatsapp_instance = None

def get_whatsapp_utils() -> WhatsAppUtils:
    """
    Retorna a instância global do WhatsAppUtils.
    
    Returns:
        WhatsAppUtils: Instância singleton
    """
    global _whatsapp_instance
    if _whatsapp_instance is None:
        _whatsapp_instance = WhatsAppUtils()
    return _whatsapp_instance


def enviar_alerta_pagamento(numero: str, nome_aluno: str, valor: float = None) -> bool:
    """
    Função de conveniência para enviar alerta de pagamento.
    
    Args:
        numero (str): Número de telefone
        nome_aluno (str): Nome do aluno
        valor (float, optional): Valor pendente
    
    Returns:
        bool: True se sucesso
    """
    whatsapp = get_whatsapp_utils()
    return whatsapp.enviar_alerta_pagamento(numero, nome_aluno, valor)


def enviar_alerta_atraso(numero: str, nome_aluno: str, hora: str = None) -> bool:
    """
    Função de conveniência para enviar alerta de atraso.
    
    Args:
        numero (str): Número de telefone
        nome_aluno (str): Nome do aluno
        hora (str, optional): Hora do atraso
    
    Returns:
        bool: True se sucesso
    """
    whatsapp = get_whatsapp_utils()
    return whatsapp.enviar_alerta_atraso(numero, nome_aluno, hora)


def enviar_alerta_risco(numero: str, nome_aluno: str, media: float = None) -> bool:
    """
    Função de conveniência para enviar alerta de risco.
    
    Args:
        numero (str): Número de telefone
        nome_aluno (str): Nome do aluno
        media (float, optional): Média do aluno
    
    Returns:
        bool: True se sucesso
    """
    whatsapp = get_whatsapp_utils()
    return whatsapp.enviar_alerta_risco(numero, nome_aluno, media)


# ============================================
# TESTE DO MÓDULO
# ============================================

if __name__ == "__main__":
    print("🧪 Teste do módulo WhatsApp Utils")
    print("=" * 60)
    
    whatsapp = WhatsAppUtils()
    
    # Testar validação de números
    print("\n📞 TESTE DE VALIDAÇÃO DE NÚMEROS:")
    print("-" * 40)
    
    numeros_teste = [
        "923456789",
        "923 456 789",
        "+244 923 456 789",
        "923-456-789",
        "123",
        "abc123"
    ]
    
    for num in numeros_teste:
        valido = whatsapp.validar_numero(num)
        resultado = "✅ Válido" if valido else "❌ Inválido"
        print(f"   {num:20} → {resultado}")
    
    # Testar formatação
    print("\n🔧 TESTE DE FORMATAÇÃO:")
    print("-" * 40)
    
    num_teste = "923456789"
    formatado = whatsapp.formatar_numero_internacional(num_teste)
    print(f"   Número original: {num_teste}")
    print(f"   Formatado: +{formatado}")
    
    # Testar geração de link
    print("\n🔗 TESTE DE GERAÇÃO DE LINK:")
    print("-" * 40)
    
    mensagem = "Olá, informamos que a propina do aluno João Silva está pendente."
    url = whatsapp.gerar_link_whatsapp("923456789", mensagem)
    print(f"   Link gerado: {url[:80]}...")
    
    # Testar envio de alerta (simulado)
    print("\n📱 TESTE DE ENVIO DE ALERTA (SIMULADO):")
    print("-" * 40)
    print("   ⚠️ Não será aberto automaticamente. Apenas simulação.")
    
    # Simular envio sem abrir navegador
    numero_teste = "923456789"
    nome_teste = "João Silva"
    
    print(f"\n   Enviando alerta para {numero_teste}...")
    print(f"   Aluno: {nome_teste}")
    print(f"   Mensagem: {MENSAGEM_PADRAO_PAGAMENTO.format(nome_teste)}")
    
    print("\n✅ Teste concluído!")
    print("\n💡 Para usar a funcionalidade real, descomente a chamada abaixo:")
    print("   whatsapp.enviar_alerta_pagamento('923456789', 'João Silva')")
