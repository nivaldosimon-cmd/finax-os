import { CheckCircle, X } from 'lucide-react';

export default function ConfirmModal({ isOpen, onClose, onConfirm, title, message, confirmText = "Confirmar" }) {
  if (!isOpen) return null;
  
  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <button className="modal-close" onClick={onClose}>
          <X size={20} />
        </button>
        
        <div className="modal-icon">
          <CheckCircle size={48} color="#10B981" />
        </div>
        
        <h3>{title}</h3>
        <p>{message}</p>
        
        <div className="modal-actions">
          <button className="btn-secondary" onClick={onClose}>Cancelar</button>
          <button className="btn-primary" onClick={onConfirm}>{confirmText}</button>
        </div>
      </div>
      
      <style jsx>{`
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0,0,0,0.8);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          backdrop-filter: blur(4px);
        }
        .modal-content {
          background: #161618;
          border-radius: 24px;
          padding: 2rem;
          max-width: 400px;
          width: 90%;
          text-align: center;
          position: relative;
          border: 1px solid #2C2C2E;
          animation: slideUp 0.2s ease;
        }
        .modal-close {
          position: absolute;
          top: 1rem;
          right: 1rem;
          background: transparent;
          border: none;
          color: #8E8E93;
          cursor: pointer;
        }
        .modal-icon { margin-bottom: 1rem; }
        h3 { color: white; margin-bottom: 0.5rem; }
        p { color: #8E8E93; margin-bottom: 1.5rem; }
        .modal-actions {
          display: flex;
          gap: 1rem;
          justify-content: center;
        }
        .btn-secondary, .btn-primary {
          padding: 0.5rem 1.5rem;
          border-radius: 8px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }
        .btn-secondary {
          background: transparent;
          border: 1px solid #2C2C2E;
          color: #8E8E93;
        }
        .btn-primary {
          background: #007BFF;
          border: none;
          color: white;
        }
        .btn-secondary:hover, .btn-primary:hover { transform: scale(1.02); }
        @keyframes slideUp {
          from { transform: translateY(20px); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }
      `}</style>
    </div>
  );
}
