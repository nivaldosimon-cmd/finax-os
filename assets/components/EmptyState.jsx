export default function EmptyState({ title, message, icon, actionText, onAction }) {
  return (
    <div className="empty-state">
      <div className="empty-icon">{icon || "📭"}</div>
      <h3>{title || "Nada por aqui"}</h3>
      <p>{message || "Tudo em ordem. Nenhum dado encontrado."}</p>
      {actionText && (
        <button onClick={onAction} className="empty-action">
          {actionText}
        </button>
      )}
      
      <style jsx>{`
        .empty-state {
          text-align: center;
          padding: 3rem;
          background: #161618;
          border-radius: 24px;
          border: 1px solid #2C2C2E;
        }
        .empty-icon { font-size: 4rem; margin-bottom: 1rem; opacity: 0.5; }
        h3 { color: white; margin-bottom: 0.5rem; }
        p { color: #8E8E93; margin-bottom: 1.5rem; }
        .empty-action {
          background: transparent;
          border: 1px solid #007BFF;
          color: #007BFF;
          padding: 0.5rem 1.5rem;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s;
        }
        .empty-action:hover { background: rgba(0,123,255,0.1); transform: scale(1.02); }
      `}</style>
    </div>
  );
}
