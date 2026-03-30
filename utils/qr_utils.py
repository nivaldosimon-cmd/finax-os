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
    if not os.path.exists(PASTA_QRCODES):
        os.makedirs(PASTA_QRCODES)


def obter_fonte(tamanho):
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
    criar_pasta_qrcodes()
    dados_qr = qrcode_id

    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=8, border=2)
    qr.add_data(dados_qr)
    qr.make(fit=True)

    img_qr = qr.make_image(fill_color="black", back_color="white")
    if img_qr.mode != 'RGB':
        img_qr = img_qr.convert('RGB')

    largura, altura = img_qr.size
    altura_texto = 100
    nova_altura = altura + altura_texto

    img_final = Image.new('RGB', (largura, nova_altura), color='white')
    img_final.paste(img_qr, (0, 0))

    draw = ImageDraw.Draw(img_final)
    fonte_titulo = obter_fonte(14)
    fonte_texto = obter_fonte(12)

    y = altura + 10
    draw.text((10, y), "UMBRELLA AI - CARTÃO DE ESTUDANTE", fill='#1E3A8A', font=fonte_titulo)
    y += 25
    draw.text((10, y), f"Aluno: {nome}", fill='black', font=fonte_texto)
    y += 20
    draw.text((10, y), f"Turma: {turma}", fill='black', font=fonte_texto)
    y += 20
    draw.text((10, y), f"ID: {qrcode_id}", fill='#10B981', font=fonte_texto)
    y += 25
    draw.text((10, y), f"Emissão: {datetime.now().strftime('%d/%m/%Y %H:%M')}", fill='gray', font=fonte_texto)

    nome_arquivo = f"{PASTA_QRCODES}/qr_{qrcode_id}_{nome.replace(' ', '_')}.png"
    img_final.save(nome_arquivo, "PNG")
    return nome_arquivo


def listar_qr_codes():
    if not os.path.exists(PASTA_QRCODES):
        return []
    return sorted([f for f in os.listdir(PASTA_QRCODES) if f.endswith('.png')], reverse=True)