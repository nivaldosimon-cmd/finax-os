import { TrendingUp, TrendingDown, AlertCircle, DollarSign } from 'lucide-react';

export default function KPICards({ data }) {
  const { saldo, inadimplencia, proximoPagamento } = data;
  
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-AO', { style: 'currency', currency: 'AOA' }).format(value);
  };
  
  return (
    <div className="kpi-grid">
      {/* Card Saldo em Caixa */}
      <div className="kpi-card highlight">
        <div className="kpi-header">
          <span className="kpi-icon">💰</span>
          <TrendingUp size={20} className="trend-icon" />
        </div>
        <div className="kpi-value">{formatCurrency(saldo)}</div>
        <div className="kpi-label">Saldo em Caixa</div>
        <div className="kpi-trend">
          <span className="trend-up">+12%</span> este mês
        </div>
        <div className="sparkline">
          <svg width="100%" height="32" viewBox="0 0 100 32">
            <polyline points="0,24 20,18 40,22 60,12 80,16 100,8" fill="none" stroke="#007BFF" strokeWidth="2"/>
          </svg>
        </div>
      </div>
      
      {/* Card Inadimplência */}
      <div className="kpi-card">
        <div className="kpi-header">
          <span className="kpi-icon">⚠️</span>
          <AlertCircle size={20} className="trend-icon" />
        </div>
        <div className="kpi-value">{inadimplencia}%</div>
        <div className="kpi-label">Inadimplência</div>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${inadimplencia}%` }}></div>
        </div>
        <div className="kpi-trend">
          <span className="trend-down">-3%</span> que no mês passado
        </div>
      </div>
      
      {/* Card RH/Salários */}
      <div className="kpi-card">
        <div className="kpi-header">
          <span className="kpi-icon">👥</span>
          <DollarSign size={20} className="trend-icon" />
        </div>
        <div className="kpi-value">{proximoPagamento?.dias || 12} dias</div>
        <div className="kpi-label">Próximo Pagamento</div>
        <div className="kpi-date">
          {proximoPagamento?.data || "25/03/2026"}
        </div>
        <div className="kpi-warning">
          ⚠️ Faltam {proximoPagamento?.dias || 12} dias
        </div>
      </div>
      
      <style jsx>{`
        .kpi-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 1.5rem;
          margin-bottom: 2rem;
        }
        .kpi-card {
          background: #161618;
          border-radius: 16px;
          padding: 1.5rem;
          border: 1px solid #2C2C2E;
          transition: all 0.2s;
        }
        .kpi-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 8px 24px rgba(0,0,0,0.4);
        }
        .kpi-card.highlight {
          background: linear-gradient(135deg, #161618, #1e1e20);
          border: 1px solid rgba(0,123,255,0.3);
        }
        .kpi-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }
        .kpi-icon { font-size: 1.5rem; }
        .trend-icon { color: #10B981; }
        .trend-down { color: #EF4444; }
        .kpi-value {
          font-size: 2rem;
          font-weight: 700;
          color: white;
          margin-bottom: 0.25rem;
        }
        .kpi-label {
          color: #8E8E93;
          font-size: 0.8rem;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        .kpi-trend {
          font-size: 0.75rem;
          color: #8E8E93;
          margin-top: 0.75rem;
        }
        .trend-up { color: #10B981; }
        .progress-bar {
          background: #2C2C2E;
          border-radius: 4px;
          height: 4px;
          margin: 0.75rem 0;
          overflow: hidden;
        }
        .progress-fill {
          background: #EF4444;
          height: 100%;
          border-radius: 4px;
          transition: width 0.3s;
        }
        .sparkline { margin-top: 0.75rem; }
        .kpi-date { color: white; font-size: 0.9rem; margin-top: 0.25rem; }
        .kpi-warning { color: #F59E0B; font-size: 0.7rem; margin-top: 0.5rem; }
      `}</style>
    </div>
  );
}
