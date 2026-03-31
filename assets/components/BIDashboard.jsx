import { AlertCircle, TrendingUp, TrendingDown, BarChart3, PieChart } from 'lucide-react';

export default function BIDashboard({ kpis, alertas, tendencias }) {
  if (!kpis) return <div>Carregando dados...</div>;

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-AO', { style: 'currency', currency: 'AOA' }).format(value);
  };

  const getSaúdeColor = (score) => {
    if (score >= 80) return '#10B981';
    if (score >= 60) return '#F59E0B';
    return '#EF4444';
  };

  return (
    <div className="bi-dashboard">
      {/* Alertas */}
      {alertas && alertas.length > 0 && (
        <div className="alertas-section">
          <h3>⚠️ Alertas Automáticos</h3>
          {alertas.map((alerta, idx) => (
            <div key={idx} className={`alerta alerta-${alerta.severidade.toLowerCase()}`}>
              <AlertCircle size={20} />
              <div className="alerta-conteudo">
                <strong>{alerta.tipo}</strong>
                <p>{alerta.mensagem}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Grid de KPIs principais */}
      <div className="kpi-grid-bi">
        {/* Total Alunos */}
        <div className="kpi-item">
          <div className="kpi-header">
            <span>👥 Total Alunos</span>
          </div>
          <div className="kpi-value">{kpis.alunos.total}</div>
          <div className="kpi-subinfo">
            <span className="badge-success">✓ {kpis.alunos.adimplentes} Adimplentes</span>
            <span className="badge-danger">✗ {kpis.alunos.devedores} Devedores</span>
          </div>
        </div>

        {/* Taxa de Inadimplência */}
        <div className="kpi-item">
          <div className="kpi-header">
            <span>📊 Inadimplência</span>
          </div>
          <div className="kpi-value">{kpis.indicadores.taxa_inadimplencia}%</div>
          <div className="progress-bar-bi">
            <div className="progress-fill" style={{
              width: `${Math.min(kpis.indicadores.taxa_inadimplencia, 100)}%`,
              background: kpis.indicadores.taxa_inadimplencia > 30 ? '#EF4444' : '#F59E0B'
            }}></div>
          </div>
        </div>

        {/* Saldo Atual */}
        <div className="kpi-item">
          <div className="kpi-header">
            <span>💰 Saldo em Caixa</span>
          </div>
          <div className="kpi-value" style={{
            color: kpis.financeiro.saldo_atual >= 0 ? '#10B981' : '#EF4444'
          }}>
            {formatCurrency(kpis.financeiro.saldo_atual)}
          </div>
          <div className="kpi-subinfo">
            <span>Margem: {kpis.financeiro.margem_lucro.toFixed(1)}%</span>
          </div>
        </div>

        {/* Projeção de Caixa */}
        <div className="kpi-item">
          <div className="kpi-header">
            <span>📈 Projeção Caixa</span>
          </div>
          <div className="kpi-value" style={{
            color: kpis.indicadores.projecao_caixa >= 0 ? '#10B981' : '#EF4444'
          }}>
            {formatCurrency(kpis.indicadores.projecao_caixa)}
          </div>
          <div className="kpi-indicator">
            Saúde: <span style={{
              color: getSaúdeColor(kpis.indicadores.saude_financeira),
              fontWeight: 'bold'
            }}>
              {kpis.indicadores.saude_financeira}%
            </span>
          </div>
        </div>
      </div>

      {/* Seção de Receitas/Despesas */}
      <div className="financeiro-section">
        <div className="financeiro-card">
          <h4>📥 Receitas</h4>
          <div className="valor">{formatCurrency(kpis.financeiro.total_receitas)}</div>
          <div className="info">Propinas pagas: {formatCurrency(kpis.propinas.pagas)}</div>
        </div>
        <div className="financeiro-card">
          <h4>📤 Despesas</h4>
          <div className="valor">{formatCurrency(kpis.financeiro.total_despesas)}</div>
          <div className="info">Salários pendentes: {formatCurrency(kpis.salarios.pendentes)}</div>
        </div>
        <div className="financeiro-card">
          <h4>⏳ Pendências</h4>
          <div className="valor">{formatCurrency(kpis.propinas.pendentes + kpis.salarios.pendentes)}</div>
          <div className="info">Propinas: {formatCurrency(kpis.propinas.pendentes)}</div>
        </div>
      </div>

      {/* Tendências */}
      {tendencias && (
        <div className="tendencias-section">
          <h3>📊 Tendências (Últimos 6 meses)</h3>
          <div className="tendencias-chart">
            {tendencias.map((mes, idx) => (
              <div key={idx} className="tendencia-bar">
                <div className="bar-value" style={{
                  height: `${Math.min((mes.lucro_liquido / 100000) * 100, 100)}%`,
                  background: mes.lucro_liquido >= 0 ? '#10B981' : '#EF4444'
                }}></div>
                <div className="bar-label">{mes.periodo}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      <style jsx>{`
        .bi-dashboard {
          padding: 1rem;
          background: #101012;
          color: #FFFFFF;
        }

        .alertas-section {
          margin-bottom: 2rem;
        }

        .alertas-section h3 {
          margin-bottom: 1rem;
          color: #F59E0B;
        }

        .alerta {
          display: flex;
          gap: 1rem;
          padding: 1rem;
          border-radius: 12px;
          margin-bottom: 0.75rem;
          border-left: 4px solid;
        }

        .alerta-crítica {
          background: rgba(239, 68, 68, 0.1);
          border-color: #EF4444;
        }

        .alerta-alta {
          background: rgba(245, 158, 11, 0.1);
          border-color: #F59E0B;
        }

        .alerta-média {
          background: rgba(59, 130, 246, 0.1);
          border-color: #3B82F6;
        }

        .alerta-conteudo {
          flex: 1;
        }

        .alerta-conteudo strong {
          color: #FFFFFF;
        }

        .alerta-conteudo p {
          color: #8E8E93;
          font-size: 0.85rem;
          margin-top: 0.25rem;
        }

        .kpi-grid-bi {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1.5rem;
          margin-bottom: 2rem;
        }

        .kpi-item {
          background: #161618;
          border-radius: 16px;
          padding: 1.5rem;
          border: 1px solid #2C2C2E;
          transition: all 0.2s;
        }

        .kpi-item:hover {
          transform: translateY(-4px);
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        }

        .kpi-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
          color: #8E8E93;
          font-size: 0.85rem;
        }

        .kpi-value {
          font-size: 2rem;
          font-weight: 700;
          margin-bottom: 0.75rem;
          color: #FFFFFF;
        }

        .kpi-subinfo {
          display: flex;
          gap: 0.5rem;
          flex-wrap: wrap;
        }

        .badge-success,
        .badge-danger {
          font-size: 0.7rem;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
        }

        .badge-success {
          background: rgba(16, 185, 129, 0.2);
          color: #10B981;
        }

        .badge-danger {
          background: rgba(239, 68, 68, 0.2);
          color: #EF4444;
        }

        .progress-bar-bi {
          height: 6px;
          background: #2C2C2E;
          border-radius: 3px;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          border-radius: 3px;
          transition: width 0.3s ease;
        }

        .kpi-indicator {
          font-size: 0.8rem;
          color: #8E8E93;
          margin-top: 0.5rem;
        }

        .financeiro-section {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1rem;
          margin-bottom: 2rem;
        }

        .financeiro-card {
          background: linear-gradient(135deg, #161618, #1e1e20);
          border-radius: 12px;
          padding: 1.25rem;
          border: 1px solid #2C2C2E;
        }

        .financeiro-card h4 {
          color: #8E8E93;
          font-size: 0.8rem;
          text-transform: uppercase;
          margin-bottom: 0.75rem;
        }

        .financeiro-card .valor {
          font-size: 1.5rem;
          font-weight: 700;
          color: #D4AF37;
          margin-bottom: 0.5rem;
        }

        .financeiro-card .info {
          font-size: 0.75rem;
          color: #8E8E93;
        }

        .tendencias-section {
          background: #161618;
          border-radius: 16px;
          padding: 1.5rem;
          border: 1px solid #2C2C2E;
        }

        .tendencias-section h3 {
          margin-bottom: 1.5rem;
          color: #FFFFFF;
        }

        .tendencias-chart {
          display: flex;
          gap: 1rem;
          align-items: flex-end;
          height: 150px;
        }

        .tendencia-bar {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 0.5rem;
        }

        .bar-value {
          width: 100%;
          border-radius: 4px 4px 0 0;
          min-height: 10px;
          transition: all 0.3s;
        }

        .bar-value:hover {
          opacity: 0.8;
          transform: scaleY(1.05);
        }

        .bar-label {
          font-size: 0.7rem;
          color: #8E8E93;
          text-align: center;
          width: 100%;
        }
      `}</style>
    </div>
  );
}
