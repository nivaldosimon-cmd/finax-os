import { Shield, Lock } from 'lucide-react';

export default function SecurityBadge() {
  return (
    <div className="security-badge">
      <Shield size={14} />
      <span>Encriptação de Ponta-a-Ponta</span>
      <Lock size={12} />
      <span>Servidores Seguros</span>
      
      <style jsx>{`
        .security-badge {
          position: fixed;
          bottom: 1rem;
          right: 1rem;
          background: rgba(22,22,24,0.9);
          backdrop-filter: blur(8px);
          padding: 0.5rem 1rem;
          border-radius: 40px;
          font-size: 0.7rem;
          color: #8E8E93;
          display: flex;
          align-items: center;
          gap: 0.5rem;
          border: 1px solid #2C2C2E;
          z-index: 100;
        }
      `}</style>
    </div>
  );
}
