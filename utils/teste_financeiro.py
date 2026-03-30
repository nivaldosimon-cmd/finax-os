"""
TESTE DO MÓDULO FINANCEIRO - UMBRELLA AI
"""

import sys
import os

# Adiciona a pasta raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.financeiro import Financeiro
from database.supabase_client import supabase
from utils.interface import verde, vermelho, amarelo, azul

def criar_funcionario_teste():
    """Cria um funcionário de exemplo para teste"""
    print("\n📝 Criando funcionário de teste...")
    
    dados = {
        "nome": "Maria Silva",
        "bi": "001234567LA040",
        "cargo": "Professor",
        "setor": "Ensino",
        "data_contratacao": "15/01/2024",
        "salario_base": 150000,
        "email": "maria.silva@escola.com",
        "telefone": "923456789",
        "status": "ATIVO"
    }
    
    try:
        # Verificar se já existe
        existe = supabase.table('funcionarios').select('*').eq('bi', dados['bi']).execute().data
        if existe:
            print(amarelo("⚠️ Funcionário já existe!"))
            return existe[0]
        
        resultado = supabase.table('funcionarios').insert(dados).execute()
        print(verde("✅ Funcionário criado!"))
        return resultado.data[0] if resultado.data else None
    except Exception as e:
        print(vermelho(f"❌ Erro: {e}"))
        return None

def criar_aluno_teste():
    """Cria um aluno de exemplo para teste"""
    print("\n📝 Criando aluno de teste...")
    
    # Verificar se já existe
    existe = supabase.table('alunos').select('*').eq('qrcode', 'ALUNO_TESTE').execute().data
    if existe:
        print(amarelo("⚠️ Aluno já existe!"))
        return existe[0]
    
    dados = {
        "nome": "João Teste",
        "turma": "7ªA",
        "qrcode": "ALUNO_TESTE",
        "data_cadastro": "26/03/2026"
    }
    
    try:
        resultado = supabase.table('alunos').insert(dados).execute()
        print(verde("✅ Aluno criado!"))
        return resultado.data[0] if resultado.data else None
    except Exception as e:
        print(vermelho(f"❌ Erro: {e}"))
        return None

def main():
    print(azul("="*60))
    print(azul("🧪 TESTE DO MÓDULO FINANCEIRO - UMBRELLA AI"))
    print(azul("="*60))
    
    financeiro = Financeiro()
    
    # 1. Criar dados de teste
    print("\n📋 CRIANDO DADOS DE TESTE")
    print("-"*40)
    
    funcionario = criar_funcionario_teste()
    aluno = criar_aluno_teste()
    
    # 2. Listar funcionários
    print("\n📋 FUNCIONÁRIOS CADASTRADOS")
    print("-"*40)
    financeiro.listar_funcionarios()
    
    # 3. Listar alunos
    print("\n📋 ALUNOS CADASTRADOS")
    print("-"*40)
    alunos = supabase.table('alunos').select('*').execute().data
    for a in alunos:
        print(f"   {a['id']} - {a['nome']} - {a['turma']}")
    
    # 4. Criar mensalidade de teste (se tiver aluno)
    if aluno:
        print("\n💰 CRIANDO MENSALIDADE DE TESTE")
        print("-"*40)
        
        mes = input("Mês (ex: MARCO): ").upper() or "MARCO"
        ano = input("Ano: ") or "2026"
        valor = float(input("Valor (Kz): ") or "50000")
        
        dados_mensalidade = {
            "aluno_id": aluno['id'],
            "mes": mes,
            "ano": ano,
            "valor": valor,
            "data_vencimento": "10/04/2026",
            "status": "PENDENTE"
        }
        
        try:
            resultado = supabase.table('mensalidades').insert(dados_mensalidade).execute()
            print(verde(f"✅ Mensalidade criada! ID: {resultado.data[0]['id']}"))
        except Exception as e:
            print(vermelho(f"❌ Erro: {e}"))
    
    # 5. Gerar folha de pagamento (se tiver funcionário)
    if funcionario:
        print("\n📄 GERAR FOLHA DE PAGAMENTO")
        print("-"*40)
        
        mes = input("Mês (ex: MARCO): ").upper() or "MARCO"
        ano = input("Ano: ") or "2026"
        
        salario_base = funcionario['salario_base']
        print(f"Salário Base: {salario_base:,.0f} Kz")
        
        subsidio_alimentacao = float(input("Subsídio Alimentação (Kz): ") or "50000")
        subsidio_transporte = float(input("Subsídio Transporte (Kz): ") or "25000")
        horas_extras = float(input("Horas Extras (Kz): ") or "0")
        descontos_falta = float(input("Descontos por faltas (Kz): ") or "0")
        
        dados_folha = {
            "funcionario_id": funcionario['id'],
            "mes": mes,
            "ano": ano,
            "salario_base": salario_base,
            "subsidio_alimentacao": subsidio_alimentacao,
            "subsidio_transporte": subsidio_transporte,
            "horas_extras": horas_extras,
            "descontos_falta": descontos_falta,
            "salario_liquido": salario_base + subsidio_alimentacao + subsidio_transporte + horas_extras - descontos_falta,
            "status": "PENDENTE"
        }
        
        try:
            resultado = supabase.table('folha_pagamento').insert(dados_folha).execute()
            print(verde(f"✅ Folha gerada! ID: {resultado.data[0]['id']}"))
            print(f"💰 Salário Líquido: {dados_folha['salario_liquido']:,.0f} Kz")
        except Exception as e:
            print(vermelho(f"❌ Erro: {e}"))
    
    # 6. Ver relatório financeiro
    print("\n📊 RELATÓRIO FINANCEIRO")
    print("-"*40)
    financeiro.relatorio_financeiro()
    
    # 7. Estatísticas finais
    print("\n📈 ESTATÍSTICAS FINAIS")
    print("-"*40)
    
    funcionarios_count = supabase.table('funcionarios').select('*', count='exact').execute().count
    folha_count = supabase.table('folha_pagamento').select('*', count='exact').execute().count
    mensalidades_count = supabase.table('mensalidades').select('*', count='exact').execute().count
    
    print(f"   Funcionários: {funcionarios_count}")
    print(f"   Folhas geradas: {folha_count}")
    print(f"   Mensalidades: {mensalidades_count}")
    
    print(f"\n{verde('✅ Teste concluído com sucesso!')}")
    
    # 8. Perguntar se quer abrir o menu interativo
    print("\n" + azul("="*60))
    resposta = input("Quer abrir o menu interativo do módulo financeiro? (s/n): ").lower()
    
    if resposta == 's':
        financeiro.menu()
    else:
        print("\n👋 Teste finalizado!")

if __name__ == "__main__":
    main()