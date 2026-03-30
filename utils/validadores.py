"""
MÓDULO VALIDADORES - FINAX OS
Validação de dados para o sistema angolano

Funcionalidade:
- Validação de Bilhete de Identidade (BI) de Angola
- Validação de números de telefone (Angola)
- Validação de email com regex
- Validação de nome completo (mínimo 2 palavras)
- Funções de limpeza e formatação
"""

import sys
import os
import re
from typing import Tuple, Optional

# Adiciona a pasta raiz ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================
# IMPORTAÇÕES DOS MÓDULOS INTERNOS
# ============================================


# ============================================
# CONSTANTES
# ============================================

# Padrões de validação
PADRAO_BI = r'^\d{9,12}[A-Z]{2}\d{2}$'  # Ex: 000123456LA012
PADRAO_EMAIL = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
PADRAO_NOME = r'^[A-Za-zÀ-ÖØ-öø-ÿ\s]{2,}$'

# Prefixos válidos para telefone em Angola
PREFIXOS_VALIDOS = ['91', '92', '93', '94', '95', '99']

# Mensagens de erro
MSG_BI_INVALIDO = "BI inválido! Formato: 9-12 dígitos + 2 letras + 2 dígitos. Ex: 000123456LA012"
MSG_TELEFONE_INVALIDO = "Telefone inválido! Deve ter 9 dígitos e começar com 91, 92, 93, 94, 95 ou 99."
MSG_EMAIL_INVALIDO = "Email inválido! Formato: nome@dominio.com"
MSG_NOME_INCOMPLETO = "Nome incompleto! Digite o nome completo (mínimo 2 palavras)."


# ============================================
# CLASSE PRINCIPAL DE VALIDAÇÃO
# ============================================

class Validadores:
    """
    Classe responsável por validações de dados para Angola.
    
    Funcionalidades:
    - Validação de Bilhete de Identidade (BI)
    - Validação de números de telefone (Angola)
    - Validação de email
    - Validação de nome completo
    - Funções de limpeza e formatação
    """
    
    def __init__(self):
        """Inicializa o módulo de validação"""
      
    
    # ============================================
    # 1. FUNÇÕES DE LIMPEZA E FORMATAÇÃO
    # ============================================
    
    def limpar_formatacao(self, texto: str) -> str:
        """
        Remove caracteres especiais, mantendo apenas letras e números.
        
        Args:
            texto (str): Texto a ser limpo
        
        Returns:
            str: Texto sem formatação (apenas letras e números)
        """
        if not texto:
            return ""
        
        # Remover espaços extras
        texto = texto.strip()
        
        # Remover pontos, traços, espaços e outros caracteres especiais
        texto_limpo = re.sub(r'[^a-zA-Z0-9]', '', texto)
        
        return texto_limpo
    
    def formatar_bi(self, bi: str) -> str:
        """
        Formata o BI para exibição padrão.
        
        Args:
            bi (str): BI bruto
        
        Returns:
            str: BI formatado
        """
        bi_limpo = self.limpar_formatacao(bi)
        
        if len(bi_limpo) == 14:
            # Formato: 000123456LA012 -> 000123456 LA 012
            return f"{bi_limpo[:9]} {bi_limpo[9:11]} {bi_limpo[11:]}"
        
        return bi_limpo
    
    def formatar_telefone(self, numero: str) -> str:
        """
        Formata o número de telefone para exibição.
        
        Args:
            numero (str): Número bruto
        
        Returns:
            str: Número formatado (ex: 923 456 789)
        """
        numero_limpo = self.limpar_formatacao(numero)
        
        if len(numero_limpo) == 9:
            return f"{numero_limpo[:3]} {numero_limpo[3:6]} {numero_limpo[6:]}"
        elif len(numero_limpo) == 12 and numero_limpo.startswith('244'):
            return f"+{numero_limpo[:3]} {numero_limpo[3:6]} {numero_limpo[6:9]} {numero_limpo[9:]}"
        
        return numero
    
    # ============================================
    # 2. VALIDAÇÃO DE BILHETE DE IDENTIDADE (BI)
    # ============================================
    
    def validar_bi(self, bi_string: str) -> bool:
        """
        Valida o Bilhete de Identidade de Angola.
        
        Formato: 9-12 dígitos + 2 letras + 2 dígitos
        Exemplo: 000123456LA012
        
        Args:
            bi_string (str): BI a ser validado
        
        Returns:
            bool: True se válido, False caso contrário
        """
        if not bi_string or not bi_string.strip():
            self.interface.exibir_mensagem(MSG_BI_INVALIDO, tipo="erro")
            return False
        
        # Limpar formatação
        bi_limpo = self.limpar_formatacao(bi_string)
        
        # Verificar comprimento (13 ou 14 caracteres)
        if len(bi_limpo) not in [13, 14]:
            self.interface.exibir_mensagem(MSG_BI_INVALIDO, tipo="erro")
            return False
        
        # Padrão: números + letras + números
        # Parte 1: números (9-12 dígitos)
        # Parte 2: letras (2 letras maiúsculas)
        # Parte 3: números (2 dígitos)
        
        # Tentar encontrar o padrão
        # O padrão aceita diferentes comprimentos para os números iniciais
        padrao_completo = r'^(\d{9,12})([A-Z]{2})(\d{2})$'
        
        match = re.match(padrao_completo, bi_limpo)
        
        if not match:
            self.interface.exibir_mensagem(MSG_BI_INVALIDO, tipo="erro")
            return False
        
        # Validar que as letras são maiúsculas (já garantido pelo regex)
        letras = match.group(2)
        
        # Validar que as letras são válidas (apenas A-Z)
        if not letras.isalpha() or not letras.isupper():
            self.interface.exibir_mensagem(MSG_BI_INVALIDO, tipo="erro")
            return False
        
        return True
    
    # ============================================
    # 3. VALIDAÇÃO DE TELEFONE (ANGOLA)
    # ============================================
    
    def validar_telefone(self, numero: str) -> bool:
        """
        Valida números de telefone de Angola.
        
        Regras:
        - 9 dígitos
        - Começa com 91, 92, 93, 94, 95 ou 99
        
        Args:
            numero (str): Número de telefone
        
        Returns:
            bool: True se válido, False caso contrário
        """
        if not numero or not numero.strip():
            self.interface.exibir_mensagem(MSG_TELEFONE_INVALIDO, tipo="erro")
            return False
        
        # Limpar formatação
        numero_limpo = self.limpar_formatacao(numero)
        
        # Verificar comprimento (9 dígitos)
        if len(numero_limpo) != 9:
            self.interface.exibir_mensagem(MSG_TELEFONE_INVALIDO, tipo="erro")
            return False
        
        # Verificar se começa com 9
        if not numero_limpo.startswith('9'):
            self.interface.exibir_mensagem(MSG_TELEFONE_INVALIDO, tipo="erro")
            return False
        
        # Verificar prefixo válido (2 primeiros dígitos)
        prefixo = numero_limpo[:2]
        if prefixo not in PREFIXOS_VALIDOS:
            self.interface.exibir_mensagem(MSG_TELEFONE_INVALIDO, tipo="erro")
            return False
        
        return True
    
    # ============================================
    # 4. VALIDAÇÃO DE EMAIL
    # ============================================
    
    def validar_email(self, email: str) -> bool:
        """
        Valida formato de email.
        
        Args:
            email (str): Endereço de email
        
        Returns:
            bool: True se válido, False caso contrário
        """
        if not email or not email.strip():
            self.interface.exibir_mensagem(MSG_EMAIL_INVALIDO, tipo="erro")
            return False
        
        # Limpar espaços
        email_limpo = email.strip().lower()
        
        # Verificar padrão
        if not re.match(PADRAO_EMAIL, email_limpo):
            self.interface.exibir_mensagem(MSG_EMAIL_INVALIDO, tipo="erro")
            return False
        
        return True
    
    # ============================================
    # 5. VALIDAÇÃO DE NOME COMPLETO
    # ============================================
    
    def validar_nome_completo(self, nome: str) -> bool:
        """
        Valida nome completo (mínimo 2 palavras).
        
        Args:
            nome (str): Nome completo
        
        Returns:
            bool: True se válido, False caso contrário
        """
        if not nome or not nome.strip():
            self.interface.exibir_mensagem(MSG_NOME_INCOMPLETO, tipo="erro")
            return False
        
        nome_limpo = nome.strip()
        
        # Verificar se tem pelo menos 2 palavras
        palavras = nome_limpo.split()
        
        if len(palavras) < 2:
            self.interface.exibir_mensagem(MSG_NOME_INCOMPLETO, tipo="erro")
            return False
        
        # Verificar se cada palavra tem pelo menos 2 caracteres
        for palavra in palavras:
            if len(palavra) < 2:
                self.interface.exibir_mensagem(MSG_NOME_INCOMPLETO, tipo="erro")
                return False
        
        return True
    
    # ============================================
    # 6. VALIDAÇÃO COMBINADA
    # ============================================
    
    def validar_dados_completos(self, nome: str, email: str, telefone: str, bi: str) -> Tuple[bool, dict]:
        """
        Valida todos os dados de um utilizador.
        
        Args:
            nome (str): Nome completo
            email (str): Email
            telefone (str): Telefone
            bi (str): Bilhete de Identidade
        
        Returns:
            tuple: (sucesso, dict com resultados)
        """
        resultados = {
            "nome": {"valido": False, "mensagem": ""},
            "email": {"valido": False, "mensagem": ""},
            "telefone": {"valido": False, "mensagem": ""},
            "bi": {"valido": False, "mensagem": ""}
        }
        
        # Validar nome
        if self.validar_nome_completo(nome):
            resultados["nome"]["valido"] = True
        else:
            resultados["nome"]["mensagem"] = MSG_NOME_INCOMPLETO
        
        # Validar email
        if self.validar_email(email):
            resultados["email"]["valido"] = True
        else:
            resultados["email"]["mensagem"] = MSG_EMAIL_INVALIDO
        
        # Validar telefone
        if self.validar_telefone(telefone):
            resultados["telefone"]["valido"] = True
        else:
            resultados["telefone"]["mensagem"] = MSG_TELEFONE_INVALIDO
        
        # Validar BI
        if self.validar_bi(bi):
            resultados["bi"]["valido"] = True
        else:
            resultados["bi"]["mensagem"] = MSG_BI_INVALIDO
        
        # Verificar se todos são válidos
        sucesso = all(r["valido"] for r in resultados.values())
        
        return sucesso, resultados


# ============================================
# FUNÇÕES DE CONVENIÊNCIA (API SIMPLES)
# ============================================

# Instância global
_validadores_instance = None

def get_validadores() -> Validadores:
    """
    Retorna a instância global dos validadores.
    
    Returns:
        Validadores: Instância singleton
    """
    global _validadores_instance
    if _validadores_instance is None:
        _validadores_instance = Validadores()
    return _validadores_instance


def validar_bi(bi_string: str) -> bool:
    """
    Função de conveniência para validar BI.
    
    Args:
        bi_string (str): BI a validar
    
    Returns:
        bool: True se válido
    """
    val = get_validadores()
    return val.validar_bi(bi_string)


def validar_telefone(numero: str) -> bool:
    """
    Função de conveniência para validar telefone.
    
    Args:
        numero (str): Número de telefone
    
    Returns:
        bool: True se válido
    """
    val = get_validadores()
    return val.validar_telefone(numero)


def validar_email(email: str) -> bool:
    """
    Função de conveniência para validar email.
    
    Args:
        email (str): Endereço de email
    
    Returns:
        bool: True se válido
    """
    val = get_validadores()
    return val.validar_email(email)


def validar_nome_completo(nome: str) -> bool:
    """
    Função de conveniência para validar nome.
    
    Args:
        nome (str): Nome completo
    
    Returns:
        bool: True se válido
    """
    val = get_validadores()
    return val.validar_nome_completo(nome)


def limpar_formatacao(texto: str) -> str:
    """
    Função de conveniência para limpar formatação.
    
    Args:
        texto (str): Texto a limpar
    
    Returns:
        str: Texto sem formatação
    """
    val = get_validadores()
    return val.limpar_formatacao(texto)


# ============================================
# TESTE DO MÓDULO
# ============================================

if __name__ == "__main__":
    print("🧪 Teste do módulo Validadores")
    print("=" * 60)
    
    val = Validadores()
    
    # Teste de BI
    print("\n📋 TESTE DE VALIDAÇÃO DE BI:")
    print("-" * 40)
    
    test_bi = [
        "000123456LA012",
        "123456789AB01",
        "00123456789CD01",
        "123456789",
        "ABCDEFGHIJKL"
    ]
    
    for bi in test_bi:
        valido = val.validar_bi(bi)
        print(f"   {bi:20} → {'✅ Válido' if valido else '❌ Inválido'}")
    
    # Teste de Telefone
    print("\n📱 TESTE DE VALIDAÇÃO DE TELEFONE:")
    print("-" * 40)
    
    test_telefone = [
        "923456789",
        "923 456 789",
        "912345678",
        "991234567",
        "123456789",
        "800123456"
    ]
    
    for tel in test_telefone:
        valido = val.validar_telefone(tel)
        print(f"   {tel:15} → {'✅ Válido' if valido else '❌ Inválido'}")
    
    # Teste de Email
    print("\n📧 TESTE DE VALIDAÇÃO DE EMAIL:")
    print("-" * 40)
    
    test_email = [
        "joao.silva@escola.com",
        "maria@gmail.com",
        "admin@finax.ao",
        "email_invalido",
        "sem@arroba",
        "@semnome.com"
    ]
    
    for email in test_email:
        valido = val.validar_email(email)
        print(f"   {email:25} → {'✅ Válido' if valido else '❌ Inválido'}")
    
    # Teste de Nome
    print("\n👤 TESTE DE VALIDAÇÃO DE NOME:")
    print("-" * 40)
    
    test_nome = [
        "João Silva",
        "Maria Santos Costa",
        "Pedro",
        "A B",
        "João"
    ]
    
    for nome in test_nome:
        valido = val.validar_nome_completo(nome)
        print(f"   {nome:25} → {'✅ Válido' if valido else '❌ Inválido'}")
    
    # Teste de limpeza de formatação
    print("\n🧹 TESTE DE LIMPEZA DE FORMATAÇÃO:")
    print("-" * 40)
    
    test_formatacao = [
        "123.456.789-LA-01",
        "923 456 789",
        "joao.silva@escola.com",
        "  texto com espaços  "
    ]
    
    for texto in test_formatacao:
        limpo = val.limpar_formatacao(texto)
        print(f"   Original: {texto}")
        print(f"   Limpo   : {limpo}")
        print()
    
    print("✅ Teste concluído!")