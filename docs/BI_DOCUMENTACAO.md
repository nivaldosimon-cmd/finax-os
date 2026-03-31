# Módulo BI (Business Intelligence) - FINAX OS

Documentação completa do módulo de Business Intelligence para análise e relatórios.

## 📊 Visão Geral

O módulo BI fornece análise avançada de dados, cálculo de KPIs, relatórios financeiros e alertas automáticos para suportar decisões estratégicas na instituição.

## 🚀 Utilização no Backend (Python)

### Inicializar o BIManager

```python
from modules.bi import BIManager

# Após autenticação
bi_manager = BIManager(supabase, instituicao_id)
```

### 1. Calcular KPIs Principais

```python
kpis = bi_manager.calcular_kpis()

# Retorna:
{
    "timestamp": "2026-03-31T10:30:00",
    "alunos": {
        "total": 150,
        "devedores": 22,
        "adimplentes": 128
    },
    "financeiro": {
        "total_receitas": 2500000,
        "total_despesas": 1800000,
        "saldo_atual": 700000,
        "margem_lucro": 28.5
    },
    "propinas": {
        "pendentes": 550000,
        "pagas": 2500000,
        "total": 3050000
    },
    "salarios": {
        "pendentes": 120000
    },
    "indicadores": {
        "taxa_inadimplencia": 14.7,
        "projecao_caixa": 1130000,
        "saude_financeira": 85
    }
}
```

**Explicação dos campos:**
- **taxa_inadimplencia**: Percentual de alunos com débito
- **projecao_caixa**: Saldo + Propinas Pendentes - Salários Pendentes
- **saude_financeira**: Score 0-100 da saúde financeira da instituição
- **margem_lucro**: Percentual de lucro sobre receitas

### 2. Relatório Mensal

```python
relatorio = bi_manager.obter_relatorio_mensal(mes=3, ano=2026)

# Retorna:
{
    "periodo": "03/2026",
    "receitas": {
        "total": 450000,
        "quantidade": 15
    },
    "despesas": {
        "total": 380000,
        "quantidade": 8,
        "por_categoria": {
            "Salário": 250000,
            "Aluguel": 80000,
            "Utilities": 50000
        }
    },
    "propinas": {
        "pendentes": 120000,
        "pagas": 450000,
        "total": 570000
    },
    "lucro_liquido": 70000
}
```

### 3. Análise de Tendências

```python
tendencias = bi_manager.obter_tendencias(meses=6)

# Retorna últimos 6 meses com comparação de variação
{
    "periodo": "Últimos 6 meses",
    "tendencias": [
        # ... relatórios dos últimos 6 meses
    ],
    "variacao_receita": 12.5  # Variação % entre meses
}
```

### 4. Ranking de Turmas

```python
ranking = bi_manager.obter_ranking_turmas()

# Retorna:
[
    {
        "turma": "10º A",
        "total_alunos": 35,
        "adimplentes": 32,
        "taxa_inadimplencia": 8.6,
        "media_notas": 14.5,
        "score": 92.3  # Score de desempenho (0-100)
    },
    {
        "turma": "11º B",
        "total_alunos": 38,
        "adimplentes": 31,
        "taxa_inadimplencia": 18.4,
        "media_notas": 12.8,
        "score": 78.5
    }
]
```

**Score de desempenho:**
- 60% baseado em média de notas
- 40% baseado em taxa de adimplência

### 5. Alertas Automáticos

```python
alertas = bi_manager.gerar_alerta_financeiro()

# Retorna:
[
    {
        "tipo": "INADIMPLENCIA",
        "severidade": "ALTA",
        "mensagem": "Taxa de inadimplência em 22%"
    },
    {
        "tipo": "CAIXA_INSUFICIENTE",
        "severidade": "CRÍTICA",
        "mensagem": "Caixa insuficiente para pagar salários"
    }
]
```

**Tipos de alertas:**
- `INADIMPLENCIA`: Quando > 20% (CRÍTICA se > 40%)
- `CAIXA_INSUFICIENTE`: Saldo < Salários Pendentes
- `SALDO_BAIXO`: Saldo < 50% dos Salários Pendentes
- `PROPINAS_ALTAS`: Propinas Pendentes > 50% das Propinas Pagas

**Severidades:**
- `CRÍTICA`: Ação imediata necessária
- `ALTA`: Atenção urgente
- `MÉDIA`: Monitoramento

### 6. Exportar para CSV

```python
# Exportar KPIs
csv_data = bi_manager.exportar_dados_csv(tipo='kpis')

# Exportar lista de alunos
csv_data = bi_manager.exportar_dados_csv(tipo='alunos')

# Exportar relatório
csv_data = bi_manager.exportar_dados_csv(tipo='relatorio')
```

## 🎨 Utilização no Frontend (React)

### Importar o componente

```javascript
import { BIDashboard } from './assets/components';
```

### Exemplo de uso com dados

```jsx
import BIDashboard from './assets/components/BIDashboard';
import { useState, useEffect } from 'react';

export default function IntelligencePage() {
  const [kpis, setKpis] = useState(null);
  const [alertas, setAlertas] = useState([]);
  const [tendencias, setTendencias] = useState([]);

  useEffect(() => {
    // Simular fetch de dados
    fetch('/api/bi/kpis')
      .then(r => r.json())
      .then(setKpis);

    fetch('/api/bi/alertas')
      .then(r => r.json())
      .then(setAlertas);

    fetch('/api/bi/tendencias')
      .then(r => r.json())
      .then(data => setTendencias(data.tendencias));
  }, []);

  return (
    <div>
      <h1>Business Intelligence</h1>
      <BIDashboard 
        kpis={kpis} 
        alertas={alertas} 
        tendencias={tendencias}
      />
    </div>
  );
}
```

### Props do BIDashboard

| Prop | Tipo | Descrição |
|------|------|-----------|
| `kpis` | object | Objeto retornado por `calcular_kpis()` |
| `alertas` | array | Array de alertas retornado por `gerar_alerta_financeiro()` |
| `tendencias` | array | Array de tendências retornado por `obter_tendencias()` |

## 📈 Métricas Explicadas

### Taxa de Inadimplência
**Fórmula:** (Alunos Devedores / Total Alunos) × 100

**Interpretação:**
- < 10%: Excelente
- 10-20%: Boa
- 20-40%: Atenção
- > 40%: Crítica

### Saúde Financeira (Score 0-100)
**Baseado em:** Cobertura de Despesas = Saldo / Despesas Pendentes

| Cobertura | Score |
|-----------|-------|
| ≥ 3x | 100 (Excelente) |
| ≥ 2x | 80 (Boa) |
| ≥ 1x | 60 (Adequada) |
| ≥ 0.5x | 30 (Preocupante) |
| < 0.5x | 10 (Crítica) |

### Margem de Lucro
**Fórmula:** ((Receitas - Despesas) / Receitas) × 100

**Benchmark:**
- < 10%: Margem baixa
- 10-20%: Margem normal
- 20-30%: Margem boa
- > 30%: Margem excelente

### Score de Desempenho de Turma
**Fórmula:** (Média Notas / 20 × 60%) + ((100 - Taxa Inadimplência) / 100 × 40%)

Varia de 0-100, considerando:
- 60% desempenho acadêmico
- 40% saúde financeira

## 🔄 Integrações Comuns

### Com Dashboard Principal

```python
def dashboard_home():
    user = st.session_state.user
    bi_manager = st.session_state.bi_manager
    
    kpis = bi_manager.calcular_kpis()
    alertas = bi_manager.gerar_alerta_financeiro()
    
    # Exibir KPIs em cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Taxa Inadimplência", f"{kpis['indicadores']['taxa_inadimplencia']}%")
    # ...
```

### Com Sistema de Notificações

```python
alertas = bi_manager.gerar_alerta_financeiro()

for alerta in alertas:
    if alerta['severidade'] == 'CRÍTICA':
        # Enviar email/SMS
        send_alert_notification(alerta)
```

### Com Exportação de Relatórios

```python
if st.button("📥 Exportar Relatório"):
    csv = bi_manager.exportar_dados_csv(tipo='relatorio')
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="relatorio_bi.csv"
    )
```

## 📊 Casos de Uso

### 1. Monitoramento Executivo
Use `calcular_kpis()` para dashboard executivo em tempo real.

### 2. Análise Comparativa
Use `obter_relatorio_mensal()` para comparar períodos.

### 3. Decisões Estratégicas
Use `obter_tendencias()` para identificar padrões.

### 4. Planejamento Acadêmico
Use `obter_ranking_turmas()` para intervenções pedagógicas.

### 5. Gestão de Risco
Use `gerar_alerta_financeiro()` para alertas automáticos.

## 🛠️ Performance

- Cálculo de KPIs: ~500ms
- Relatório mensal: ~200ms
- Tendências (6 meses): ~1200ms
- Alertas: ~100ms

Para otimizar:
- Cache resultados com TTL de 5 minutos
- Calcular tendências em background
- Usar índices no banco de dados

## 🔒 Permissões

Recomenda-se:
- Apenas Administradores podem acessar BI
- Relatórios podem ser consultados por coordenadores
- Alertas devem ser notificados aos responsáveis

## 📞 Suporte

Para dúvidas sobre interpretação de métricas, consulte o manual de gestão.

---

**Versão**: 1.0.0  
**Última atualização**: 2026-03-31
