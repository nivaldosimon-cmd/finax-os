"""
TESTE SIMPLES DO MÓDULO FINANCEIRO - UMBRELLA AI
"""

print("="*50)
print("🧪 TESTE DO MÓDULO FINANCEIRO")
print("="*50)

try:
    # Testar importação do Supabase
    from database.supabase_client import supabase
    print("✅ Conexão com Supabase: OK")
    
    # Testar importação do módulo financeiro
    from modules.financeiro import Financeiro
    print("✅ Módulo financeiro importado: OK")
    
    # Testar cores
    from utils.interface import verde, vermelho, amarelo, azul
    print("✅ Cores importadas: OK")
    
    print("\n🎉 TUDO CERTO! Os arquivos estão no lugar certo.")
    print("\nAbrindo módulo financeiro...")
    
    # Criar instância
    financeiro = Financeiro()
    
    # Mostrar menu
    financeiro.menu()
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    print("\nVerifica se os arquivos estão no lugar certo:")
    print("   - database/supabase_client.py")
    print("   - modules/financeiro.py")
    print("   - utils/cores.py")
    print("   - .env com as credenciais do Supabase")