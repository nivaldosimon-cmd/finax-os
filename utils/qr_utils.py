"""
MÓDULO QR_UTILS - UMBRELLA AI
Geração de QR codes visuais com ID numérico
"""

import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

PASTA_QRCODES = "qrcodes"


def criar_pasta_qrcodes():
    """Cria a pasta de QR codes se não existir"""
    if not os.path.exists(PASTA_QRCODES):
        os.makedirs(PASTA_QRCODES)


def obter_fonte(tamanho):
    """Tenta obter uma fonte, fallback para padrão"""
    try:
        fontes = ["arial.ttf", "DejaVuSans.ttf", "FreeSans.ttf", "Arial.ttf"]
        for f in fontes:
            try:
                return ImageFont.truetype(f, tamanho)
            except:
                continue
        return ImageFont.load_default()
    except:
        return ImageFont.load_default()


def gerar_qr_code_aluno(aluno_id, nome, turma, qrcode_id):
    """
    Gera QR code visual para o aluno.
    
    Args:
        aluno_id (str): UUID do aluno
        nome (str): Nome do aluno
        turma (str): Turma do aluno
        qrcode_id (str): ID numérico (ex: 1001)
    
    Returns:
        str: Caminho do arquivo gerado
    """
    criar_pasta_qrcodes()
    
    dados_qr = qrcode_id

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=2
    )
    qr.add_data(dados_qr)
    qr.make(fit=True)

    img_qr = qr.make_image(fill_color="black", back_color="white")
    if img_qr.mode != 'RGB':
        img_qr = img_qr.convert('RGB')

    img_final = adicionar_informacoes_aluno(img_qr, nome, turma, qrcode_id)

    nome_arquivo = f"{PASTA_QRCODES}/qr_{qrcode_id}_{nome.replace(' ', '_')}.png"
    img_final.save(nome_arquivo, "PNG")
    return nome_arquivo


def gerar_qr_code_pagamento(username, nome, valor, referencia):
    """
    Gera QR code visual para pagamento.
    
    Args:
        username (str): Username do aluno
        nome (str): Nome do aluno
        valor (float): Valor do pagamento
        referencia (str): Referência do pagamento
    
    Returns:
        str: Caminho do arquivo gerado
    """
    criar_pasta_qrcodes()
    
    dados_qr = f"FINAX_PAY|{username}|{nome}|{valor:.2f}|{referencia}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=2
    )
    qr.add_data(dados_qr)
    qr.make(fit=True)

    img_qr = qr.make_image(fill_color="black", back_color="white")
    if img_qr.mode != 'RGB':
        img_qr = img_qr.convert('RGB')

    img_final = adicionar_informacoes_pagamento(img_qr, nome, valor, referencia)

    data_atual = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"{PASTA_QRCODES}/pagamento_{username}_{data_atual}.png"
    img_final.save(nome_arquivo, "PNG")
    return nome_arquivo


def adicionar_informacoes_aluno(img_qr, nome, turma, qrcode_id):
    """Adiciona informações do aluno abaixo do QR code"""
    largura_qr, altura_qr = img_qr.size
    
    altura_texto = 100
    nova_altura = altura_qr + altura_texto
    
    img_final = Image.new('RGB', (largura_qr, nova_altura), color='white')
    img_final.paste(img_qr, (0, 0))
    
    draw = ImageDraw.Draw(img_final)
    fonte_titulo = obter_fonte(14)
    fonte_texto = obter_fonte(12)
    
    y_texto = altura_qr + 10
    
    # Título
    draw.text((10, y_texto), "UMBRELLA AI - CARTAO DE ESTUDANTE", fill='#1E3A8A', font=fonte_titulo)
    
    # Nome
    y_texto += 25
    draw.text((10, y_texto), f"Aluno: {nome}", fill='black', font=fonte_texto)
    
    # Turma
    y_texto += 20
    draw.text((10, y_texto), f"Turma: {turma}", fill='black', font=fonte_texto)
    
    # ID do QR Code
    y_texto += 20
    draw.text((10, y_texto), f"ID: {qrcode_id}", fill='#10B981', font=fonte_texto)
    
    # Data
    y_texto += 25
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
    draw.text((10, y_texto), f"Emissao: {data_atual}", fill='gray', font=fonte_texto)
    
    return img_final


def adicionar_informacoes_pagamento(img_qr, nome, valor, referencia):
    """Adiciona informações de pagamento abaixo do QR code"""
    largura_qr, altura_qr = img_qr.size
    
    altura_texto = 120
    nova_altura = altura_qr + altura_texto
    
    img_final = Image.new('RGB', (largura_qr, nova_altura), color='white')
    img_final.paste(img_qr, (0, 0))
    
    draw = ImageDraw.Draw(img_final)
    fonte_titulo = obter_fonte(14)
    fonte_texto = obter_fonte(12)
    fonte_valor = obter_fonte(13)
    
    y_texto = altura_qr + 10
    
    # Título
    draw.text((10, y_texto), "FINAX PAY - COMPROVANTE DE PAGAMENTO", fill='#1E3A8A', font=fonte_titulo)
    
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
    """Lista todos os QR codes gerados"""
    if not os.path.exists(PASTA_QRCODES):
        return []
    arquivos = [f for f in os.listdir(PASTA_QRCODES) if f.endswith('.png')]
    return sorted(arquivos, reverse=True)


if __name__ == "__main__":
    print("🧪 Teste do módulo QR Utils")
    print("=" * 50)
    
    # Teste
    caminho = gerar_qr_code_aluno("teste_id", "João Teste", "10ªA", "1001")
    print(f"Arquivo: {caminho}")
    
    print("\n✅ Teste concluído!")