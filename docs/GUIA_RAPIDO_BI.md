# Guia Rápido - Módulo BI

## ⚡ Início Rápido

### 1. No Backend (app.py)

```python
# Após login do usuário
bi_manager = st.session_state.bi_manager

# Obter KPIs principais
kpis = bi_manager.calcular_kpis()

# Obter alertas automáticos
alertas = bi_manager.gerar_alerta_financeiro()

# Exibir no Streamlit
st.json(kpis)
```

### 2. No Frontend (React)

```jsx
import { BIDashboard } from './assets/components';

<BIDashboard kpis={kpis} alertas={alertas} tendencias={tendencias} />
```

## 📊 Métodos Principais

| Método | O que faz | Tempo |
|--------|----------|-------|
| `calcular_kpis()` | Calcula todos os indicadores | 500ms |
| `obter_relatorio_mensal(mes, ano)` | Relatório de um mês | 200ms |
| `obter_tendencias(meses)` | Análise dos últimos N meses | 1200ms |
| `obter_ranking_turmas()` | Ranking de desempenho | 300ms |
| `gerar_alerta_financeiro()` | Alertas automáticos | 100ms |
| `exportar_dados_csv(tipo)` | Exporta em CSV | 150ms |

## 🎯 Casos Comuns

### Dashboard Principal
```python
def dashboard_home():
    bi_manager = st.session_state.bi_manager
    kpis = bi_manager.calcular_kpis()
    
    # Cards de KPI
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Inadimplência", f"{kpis['indicadores']['taxa_inadimplencia']}%")
    with col2:
        st.metric("Saldo", kpis['financeiro']['saldo_atual'])
    with col3:
        st.metric("Saúde", f"{kpis['indicadores']['saude_financeira']}%")
```

### Alertas e Notificações
```python
alertas = bi_manager.gerar_alerta_financeiro()

if alertas:
    for alerta in alertas:
        st.warning(f"⚠️ {alerta['mensagem']}")
```

### Relatório Mensal
```python
relatorio = bi_manager.obter_relatorio_mensal(mes=3, ano=2026)
st.write(f"Lucro: {relatorio['lucro_liquido']:.2f} Kz")
```

### Ranking de Turmas
```python
ranking = bi_manager.obter_ranking_turmas()

for turma in ranking:
    st.write(f"{turma['turma']}: Score {turma['score']}")
```

## 🔍 Interpretação Rápida

### Taxa de Inadimplência
- ✅ < 10%: Excelente
- ⚠️ 10-20%: Normal
- 🔴 20-40%: Atenção
- 🚨 > 40%: Crítica

### Saúde Financeira
- 🟢 > 80: Excelente
- 🟡 60-80: Boa
- 🔴 < 60: Preocupante

### Score Turma
- 90-100: Top de desempenho
- 75-90: Bom desempenho
- 50-75: Desempenho médio
- < 50: Intervenção necessária

## 📥 Exportar Dados

```python
# KPIs em CSV
csv = bi_manager.exportar_dados_csv(tipo='kpis')
st.download_button("Baixar KPIs", csv, "kpis.csv")

# Alunos em CSV
csv = bi_manager.exportar_dados_csv(tipo='alunos')
st.download_button("Baixar Alunos", csv, "alunos.csv")
```

## ⚙️ Configuração

### Cache de resultados
```python
@st.cache_data(ttl=300)  # 5 minutos
def get_kpis():
    return st.session_state.bi_manager.calcular_kpis()
```

### Atualização automática
```python
import time

while True:
    kpis = bi_manager.calcular_kpis()
    st.write(kpis)
    st.write("Próxima atualização em 60s...")
    time.sleep(60)
```

## 📱 Componente React

### Props esperadas
```javascript
<BIDashboard 
  kpis={{
    alunos: {...},
    financeiro: {...},
    propinas: {...},
    salarios: {...},
    indicadores: {...}
  }}
  alertas={[
    { tipo: '...', severidade: '...', mensagem: '...' }
  ]}
  tendencias={[
    { periodo: '01/2026', receitas: {...}, despesas: {...}, lucro_liquido: ... }
  ]}
/>
```

## 🐛 Debug

```python
# Verificar dados
kpis = bi_manager.calcular_kpis()
print(f"KPIs: {kpis}")

# Verificar alertas
alertas = bi_manager.gerar_alerta_financeiro()
print(f"Alertas: {alertas}")

# Verificar logs
import logging
logger = logging.getLogger('finax_os')
```

## 🔗 Próximos Passos

1. **Integrar no Dashboard Principal** - Use `calcular_kpis()` para exibir métricas
2. **Configurar Alertas** - Notifique administradores de situações críticas
3. **Exportação de Relatórios** - Adicione botões de download
4. **Gráficos Avançados** - Use Plotly/Chart.js para visualizações

## 📞 Referência Rápida

```python
# Tudo em um código
bi = st.session_state.bi_manager

# KPIs
kpis = bi.calcular_kpis()
taxa_inadimplencia = kpis['indicadores']['taxa_inadimplencia']
saldo = kpis['financeiro']['saldo_atual']
saude = kpis['indicadores']['saude_financeira']

# Alertas
alertas = bi.gerar_alerta_financeiro()

# Tendências
tendencias = bi.obter_tendencias(meses=6)

# Ranking
ranking = bi.obter_ranking_turmas()

# Relatório
relatorio = bi.obter_relatorio_mensal(3, 2026)

# Export
csv = bi.exportar_dados_csv(tipo='kpis')
```

---

**Dica:** Use `@st.cache_data(ttl=300)` para melhor performance com dados que não mudam frequentemente.
