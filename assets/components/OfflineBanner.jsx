import { WifiOff } from 'lucide-react';

export default function OfflineBanner() {
  return (
    <div className="offline-banner">
      <WifiOff size={16} />
      <span>Modo Offline: Sincronizando dados locais...</span>
      <div className="sync-spinner"></div>
      
      <style jsx>{`
        .offline-banner {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          background: #F59E0B;
          color: #101012;
          padding: 0.5rem;
          text-align: center;
          font-size: 0.8rem;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
          z-index: 1000;
        }
        .sync-spinner {
          width: 12px;
          height: 12px;
          border: 2px solid #101012;
          border-top-color: transparent;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
