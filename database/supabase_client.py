import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

# Isso força o Python a buscar o .env na pasta de cima (raiz do projeto)
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

# DEBUG: Vamos ver se as chaves estão a ser lidas (vai aparecer no terminal)
if not url or not key:
    print(f"ERRO: .env não encontrado em: {env_path}")
    raise ValueError("Chaves do Supabase não encontradas!")

# Se chegar aqui, ele tenta conectar
supabase: Client = create_client(url, key)