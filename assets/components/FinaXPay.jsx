import { useState } from 'react';
import { Download, Upload, QrCode, Copy, Check } from 'lucide-react';

export default function FinaXPay({ aluno, valor, onPay, onUpload }) {
  const [copied, setCopied] = useState(false);
  const [uploading, setUploading] = useState(false);
  
  const payLink = `https://finax-os.streamlit.app/pay?aluno=${aluno.id}&valor=${valor}`;
  
  const copyToClipboard = () => {
    navigator.clipboard.writeText(payLink);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-AO', { style: 'currency', currency: 'AOA' }).format(value);
  };
  
  return (
    <div className="finax-pay-container">
      <div className="invoice-card">
        <div className="invoice-header">
          <h3>📄 Fatura Digital</h3>
          <span className="invoice-status">Pendente</span>
        </div>
        
        <div className="invoice-details">
          <div className="detail-row">
            <span>Aluno:</span>
            <strong>{aluno.nome}</strong>
          </div>
          <div className="detail-row">
            <span>Valor:</span>
            <strong className="valor">{formatCurrency(valor)}</strong>
          </div>
          <div className="detail-row">
            <span>Referência:</span>
            <span>FINAX-{aluno.id.slice(0,8)}</span>
          </div>
          <div className="detail-row">
            <span>IBAN:</span>
            <span className="iban">AO06.0066.0000.1234.5678.9012.3</span>
          </div>
        </div>
        
        <div className="qr-section">
          <div className="qr-code">
            <QrCode size={120} />
            <p>Escaneie para pagar</p>
          </div>
          <div className="pay-link-section">
            <div className="pay-link">
              <code>{payLink}</code>
              <button onClick={copyToClipboard} className="copy-btn">
                {copied ? <Check size={16} /> : <Copy size={16} />}
              </button>
            </div>
            <button className="btn-outline" onClick={onPay}>
              <Download size={16} /> Gerar QR Code
            </button>
          </div>
        </div>
        
        <div className="upload-section">
          <div className="upload-area">
            <Upload size={24} />
            <p>Envie o comprovativo de pagamento</p>
            <input 
              type="file" 
              accept=".pdf,.jpg,.png"
              onChange={onUpload}
              disabled={uploading}
            />
          </div>
          <button className="btn-ghost" onClick={() => alert('Comprovativo enviado!')}>
            Confirmar Pagamento
          </button>
        </div>
      </div>
      
      <style jsx>{`
        .finax-pay-container { max-width: 600px; margin: 0 auto; }
        .invoice-card {
          background: #161618;
          border-radius: 24px;
          padding: 1.5rem;
          border: 1px solid #2C2C2E;
        }
        .invoice-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1.5rem;
          padding-bottom: 1rem;
          border-bottom: 1px solid #2C2C2E;
        }
        .invoice-header h3 { color: white; font-size: 1.25rem; }
        .invoice-status {
          background: rgba(245,158,11,0.2);
          color: #F59E0B;
          padding: 0.25rem 0.75rem;
          border-radius: 20px;
          font-size: 0.75rem;
        }
        .detail-row {
          display: flex;
          justify-content: space-between;
          padding: 0.5rem 0;
          color: #8E8E93;
        }
        .detail-row strong { color: white; }
        .valor { color: #D4AF37; font-size: 1.2rem; }
        .iban { font-family: monospace; font-size: 0.8rem; }
        .qr-section {
          display: flex;
          gap: 1.5rem;
          margin: 1.5rem 0;
          padding: 1rem;
          background: white;
          border-radius: 16px;
          align-items: center;
          justify-content: center;
        }
        .qr-code { text-align: center; }
        .qr-code p { color: #8E8E93; font-size: 0.7rem; margin-top: 0.5rem; }
        .pay-link-section { flex: 1; }
        .pay-link {
          background: #f5f5f5;
          padding: 0.5rem;
          border-radius: 8px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }
        .pay-link code { font-size: 0.7rem; word-break: break-all; color: #333; }
        .copy-btn {
          background: transparent;
          border: none;
          cursor: pointer;
          padding: 0.25rem;
        }
        .btn-outline, .btn-ghost {
          width: 100%;
          padding: 0.75rem;
          border-radius: 12px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
        }
        .btn-outline {
          background: transparent;
          border: 1px solid #007BFF;
          color: #007BFF;
        }
        .btn-outline:hover { background: rgba(0,123,255,0.1); transform: scale(1.02); }
        .btn-ghost {
          background: #007BFF;
          border: none;
          color: white;
          margin-top: 1rem;
        }
        .upload-section { margin-top: 1rem; }
        .upload-area {
          border: 2px dashed #2C2C2E;
          border-radius: 12px;
          padding: 1rem;
          text-align: center;
          position: relative;
          cursor: pointer;
        }
        .upload-area input {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          opacity: 0;
          cursor: pointer;
        }
        .upload-area p { color: #8E8E93; margin-top: 0.5rem; }
      `}</style>
    </div>
  );
}
