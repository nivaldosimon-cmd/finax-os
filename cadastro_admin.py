from database.supabase_client import supabase  # A tua conexão central
import qrcode
import os
import random

def cadastrar_aluno_finax():
    print("\n" + "="*40)
    print("      FINAX SYSTEM - PAINEL ADMIN      ")
    print("="*40)
    
    # 1. Identificação da Escola (A Assinatura do Cliente)
    escola = input("Digite o ID da Escola (ex: PUNIV, IPEL, FINA_HQ): ").strip().upper()
    
    # 2. Dados do Aluno
    nome = input("Nome do Aluno: ").strip()
    turma = input("Turma/Curso: ").strip()
    
    # 3. Gerar ID Único com a 'assinatura' da escola
    # Exemplo: PUNIV-NIV-1234
    id_unico = f"{escola}-{nome[:3].upper()}-{random.randint(1000, 9999)}"
    
    try:
    
        dados = {
            "nome": nome,
            "turma": turma,
            "qrcode_id": id_unico,  # Mudamos para qrcode_id para bater com o SQL
            "escola_id": escola  
        }
        
        # Faz o INSERT na tabela 'alunos'
        res = supabase.table("alunos").insert(dados).execute()
        
        if res.data:
            print(f"\n✅ SUCESSO! {nome} foi guardado na base da {escola}.")
            
            # 5. Organização Local: Criar pasta e imagem do QR Code
            pasta_escola = f"qrcodes/{escola}"
            os.makedirs(pasta_escola, exist_ok=True)
            
            img = qrcode.make(id_unico)
            caminho_img = f"{pasta_escola}/{nome.replace(' ', '_')}_qr.png"
            img.save(caminho_img)
            
            print(f"🖼️ QR Code gerado em: {caminho_img}")
            print("="*40)

    except Exception as e:
        print(f"❌ ERRO AO CONECTAR: {e}")

if __name__ == "__main__":
    cadastrar_aluno_finax()