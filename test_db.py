# Salva como test_db.py e executa
from modules.database_config import db_config
from tabulate import tabulate

def testar_sistema():
    print("🛰️  A tentar conectar ao Supabase...")
    sucesso, msg = db_config.testar_conexao()
    
    if sucesso:
        print(f"✅ {msg}")
        # Teste de leitura de usuários
        try:
            client = db_config.conectar()
            res = client.table("usuarios").select("*").limit(5).execute()
            print("\n👥 Usuários encontrados na DB:")
            print(tabulate(res.data, headers="keys", tablefmt="fancy_grid"))
        except Exception as e:
            print(f"⚠️  Conectou, mas houve erro na tabela: {e}")
    else:
        print(f"❌ {msg}")

if __name__ == "__main__":
    testar_sistema()