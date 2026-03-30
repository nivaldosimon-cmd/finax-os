"""
MÓDULO QR_UTILS - FINAX OS
Geração de QR codes visuais para alunos e pagamentos

Funcionalidade:
- Gerar QR code visual (imagem PNG) para cada aluno
- QR code com informações do aluno (username, nome, turma)
- QR code para pagamentos FinaX Pay
- Salvar em pasta qrcodes/ com nome do aluno
"""

import sys
import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

# Adiciona a pasta raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================
# CONSTANTES
# ============================================

PASTA_QRCODES = "qrcodes"

# Configurações do QR Code
QR_VERSION = 1
QR_BOX_SIZE = 10
QR_BORDER = 4
QR_FILL_COLOR = "black"
QR_BACK_COLOR = "white"

# ============================================
# CORES PARA O TERMINAL
# ============================================
class Cores:
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    VERMELHO = '\033[91m'
    AZUL = '\033[94m'
    CIANO = '\033[96m'
    RESET = '\033[0m'


def cor_verde(texto):
    return f"{Cores.VERDE}{texto}{Cores.RESET}"

def cor_vermelho(texto):
    return f"{Cores.VERMELHO}{texto}{Cores.RESET}"


# ============================================
# FUNÇÕES PRINCIPAIS
# ============================================

def criar_pasta_qrcodes():
    """Cria a pasta de QR codes se não existir"""
    if not os.path.exists(PASTA_QRCODES):
        os.makedirs(PASTA_QRCODES)
        print(f"📁 Pasta criada: {PASTA_QRCODES}/")


def gerar_qr_code_aluno(username, nome, turma, escola_id):
    """
    Gera um QR code visual para o aluno.
    
    Args:
        username (str): Username do aluno
        nome (str): Nome completo do aluno
        turma (str): Turma do aluno
        escola_id (str): ID da escola
    
    Returns:
        str: Caminho do arquivo gerado
    """
    criar_pasta_qrcodes()
    
    # Dados que serão codificados no QR code
    dados_qr = f"FINAX_ALUNO|{username}|{nome}|{turma}|{escola_id}"
    
    # Criar QR code
    qr = qrcode.QRCode(
        version=QR_VERSION,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=QR_BOX_SIZE,
        border=QR_BORDER
    )
    qr.add_data(dados_qr)
    qr.make(fit=True)
    
    # Criar imagem do QR code
    img_qr = qr.make_image(fill_color=QR_FILL_COLOR, back_color=QR_BACK_COLOR)
    
    # Criar imagem final com informações do aluno
    img_final = adicionar_informacoes_aluno(img_qr, nome, turma, username)
    
    # Salvar imagem
    nome_arquivo = f"{PASTA_QRCODES}/aluno_{username}_{nome.replace(' ', '_')}.png"
    img_final.save(nome_arquivo, "PNG")
    
    print(f"{cor_verde('✅')} QR Code gerado: {nome_arquivo}")
    return nome_arquivo


def gerar_qr_code_pagamento(username, nome, valor, referencia):
    """
    Gera um QR code visual para pagamento.
    
    Args:
        username (str): Username do aluno
        nome (str): Nome do aluno
        valor (float): Valor do pagamento
        referencia (str): Referência do pagamento
    
    Returns:
        str: Caminho do arquivo gerado
    """
    criar_pasta_qrcodes()
    
    # Dados que serão codificados no QR code
    dados_qr = f"FINAX_PAY|{username}|{nome}|{valor:.2f}|{referencia}"
    
    # Criar QR code
    qr = qrcode.QRCode(
        version=QR_VERSION,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=QR_BOX_SIZE,
        border=QR_BORDER
    )
    qr.add_data(dados_qr)
    qr.make(fit=True)
    
    # Criar imagem do QR code
    img_qr = qr.make_image(fill_color=QR_FILL_COLOR, back_color=QR_BACK_COLOR)
    
    # Criar imagem final com informações do pagamento
    img_final = adicionar_informacoes_pagamento(img_qr, nome, valor, referencia)
    
    # Salvar imagem
    data_atual = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"{PASTA_QRCODES}/pagamento_{username}_{data_atual}.png"
    img_final.save(nome_arquivo, "PNG")
    
    print(f"{cor_verde('✅')} QR Code de pagamento gerado: {nome_arquivo}")
    return nome_arquivo


def adicionar_informacoes_aluno(img_qr, nome, turma, username):
    """
    Adiciona informações do aluno abaixo do QR code.
    
    Args:
        img_qr (Image): Imagem do QR code
        nome (str): Nome do aluno
        turma (str): Turma do aluno
        username (str): Username do aluno
    
    Returns:
        Image: Imagem final com informações
    """
    largura_qr, altura_qr = img_qr.size
    
    # Altura adicional para o texto
    altura_texto = 100
    nova_altura = altura_qr + altura_texto
    
    # Criar nova imagem branca
    img_final = Image.new('RGB', (largura_qr, nova_altura), color='white')
    
    # Colar QR code no topo
    img_final.paste(img_qr, (0, 0))
    
    # Adicionar texto
    draw = ImageDraw.Draw(img_final)
    
    # Tentar usar uma fonte, se disponível
    try:
        fonte_titulo = ImageFont.truetype("arial.ttf", 16)
        fonte_texto = ImageFont.truetype("arial.ttf", 12)
    except:
        fonte_titulo = ImageFont.load_default()
        fonte_texto = ImageFont.load_default()
    
    y_texto = altura_qr + 10
    
    # Título
    draw.text((10, y_texto), "FINAX OS - CARTÃO DE ESTUDANTE", fill='black', font=fonte_titulo)
    
    # Nome do aluno
    y_texto += 25
    draw.text((10, y_texto), f"Aluno: {nome}", fill='black', font=fonte_texto)
    
    # Turma
    y_texto += 20
    draw.text((10, y_texto), f"Turma: {turma}", fill='black', font=fonte_texto)
    
    # Username
    y_texto += 20
    draw.text((10, y_texto), f"Username: {username}", fill='black', font=fonte_texto)
    
    # Data de emissão
    y_texto += 25
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
    draw.text((10, y_texto), f"Emissão: {data_atual}", fill='gray', font=fonte_texto)
    
    return img_final


def adicionar_informacoes_pagamento(img_qr, nome, valor, referencia):
    """
    Adiciona informações de pagamento abaixo do QR code.
    
    Args:
        img_qr (Image): Imagem do QR code
        nome (str): Nome do aluno
        valor (float): Valor do pagamento
        referencia (str): Referência do pagamento
    
    Returns:
        Image: Imagem final com informações
    """
    largura_qr, altura_qr = img_qr.size
    
    # Altura adicional para o texto
    altura_texto = 120
    nova_altura = altura_qr + altura_texto
    
    # Criar nova imagem branca
    img_final = Image.new('RGB', (largura_qr, nova_altura), color='white')
    
    # Colar QR code no topo
    img_final.paste(img_qr, (0, 0))
    
    # Adicionar texto
    draw = ImageDraw.Draw(img_final)
    
    # Tentar usar uma fonte, se disponível
    try:
        fonte_titulo = ImageFont.truetype("arial.ttf", 16)
        fonte_texto = ImageFont.truetype("arial.ttf", 12)
        fonte_valor = ImageFont.truetype("arial.ttf", 14)
    except:
        fonte_titulo = ImageFont.load_default()
        fonte_texto = ImageFont.load_default()
        fonte_valor = ImageFont.load_default()
    
    y_texto = altura_qr + 10
    
    # Título
    draw.text((10, y_texto), "FINAX PAY - COMPROVANTE DE PAGAMENTO", fill='black', font=fonte_titulo)
    
    # Nome do aluno
    y_texto += 25
    draw.text((10, y_texto), f"Aluno: {nome}", fill='black', font=fonte_texto)
    
    # Valor
    y_texto += 20
    draw.text((10, y_texto), f"Valor: {valor:,.2f} Kz", fill='#10B981', font=fonte_valor)
    
    # Referência
    y_texto += 20
    draw.text((10, y_texto), f"Referência: {referencia}", fill='black', font=fonte_texto)
    
    # Data
    y_texto += 20
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
    draw.text((10, y_texto), f"Data: {data_atual}", fill='gray', font=fonte_texto)
    
    return img_final


def listar_qr_codes():
    """
    Lista todos os QR codes gerados.
    
    Returns:
        list: Lista de arquivos
    """
    if not os.path.exists(PASTA_QRCODES):
        return []
    
    arquivos = [f for f in os.listdir(PASTA_QRCODES) if f.endswith('.png')]
    return sorted(arquivos, reverse=True)


def exibir_qr_code_no_terminal(caminho):
    """
    Exibe o QR code no terminal (ASCII art).
    
    Args:
        caminho (str): Caminho do arquivo PNG
    """
    try:
        from PIL import Image
        import numpy as np
        
        img = Image.open(caminho).convert('L')
        img = img.resize((50, 50))
        pixels = np.array(img)
        
        print("\n" + "="*60)
        print("📱 QR CODE (escaneie com o telemóvel)")
        print("="*60)
        
        for row in pixels:
            linha = ""
            for pixel in row:
                if pixel < 128:
                    linha += "██"
                else:
                    linha += "  "
            print(linha)
        
        print("="*60)
        
    except Exception as e:
        print(f"Erro ao exibir QR code: {e}")


# ============================================
# TESTE DO MÓDULO
# ============================================

if __name__ == "__main__":
    print("🧪 Teste do módulo QR Utils")
    print("="*50)
    
    # Gerar QR code para aluno
    caminho = gerar_qr_code_aluno("joao.silva", "João Silva", "10ªA", "ESC_001")
    print(f"Arquivo: {caminho}")
    
    # Gerar QR code para pagamento
    caminho_pag = gerar_qr_code_pagamento("joao.silva", "João Silva", 35000, "REF_001")
    print(f"Arquivo: {caminho_pag}")
    
    # Listar QR codes
    print("\n📋 QR CODES GERADOS:")
    for arquivo in listar_qr_codes():
        print(f"   • {arquivo}")
    
    print(f"\n{cor_verde('✅ Teste concluído!')}")