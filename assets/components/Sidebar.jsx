import { useState } from 'react';
import { Home, Users, BookOpen, CreditCard, Calendar, Settings, LogOut, Menu, X } from 'lucide-react';

const menuItems = [
  { icon: Home, label: 'Dashboard', key: 'dashboard' },
  { icon: Users, label: 'Alunos', key: 'alunos' },
  { icon: Users, label: 'Professores', key: 'professores' },
  { icon: BookOpen, label: 'Notas', key: 'notas' },
  { icon: CreditCard, label: 'Financeiro', key: 'financeiro' },
  { icon: CreditCard, label: 'FinaX Pay', key: 'finax_pay' },
  { icon: Calendar, label: 'Salários', key: 'folha' },
  { icon: Settings, label: 'Configurações', key: 'config' },
];

export default function Sidebar({ activePage, setActivePage, isCollapsed, setIsCollapsed }) {
  return (
    <div className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <div className="logo">
          <span className="logo-icon">🏫</span>
          {!isCollapsed && <span className="logo-text">FINAX OS</span>}
        </div>
        <button className="toggle-btn" onClick={() => setIsCollapsed(!isCollapsed)}>
          {isCollapsed ? <Menu size={20} /> : <X size={20} />}
        </button>
      </div>
      
      <nav className="sidebar-nav">
        {menuItems.map((item) => (
          <button
            key={item.key}
            className={`nav-item ${activePage === item.key ? 'active' : ''}`}
            onClick={() => setActivePage(item.key)}
          >
            <item.icon size={20} />
            {!isCollapsed && <span>{item.label}</span>}
          </button>
        ))}
      </nav>
      
      <div className="sidebar-footer">
        <button className="nav-item logout">
          <LogOut size={20} />
          {!isCollapsed && <span>Sair</span>}
        </button>
      </div>
      
      <style jsx>{`
        .sidebar {
          position: fixed;
          left: 0;
          top: 0;
          height: 100vh;
          background: #161618;
          border-right: 1px solid #2C2C2E;
          transition: width 0.3s ease;
          z-index: 100;
          display: flex;
          flex-direction: column;
        }
        .sidebar:not(.collapsed) { width: 260px; }
        .sidebar.collapsed { width: 72px; }
        
        .sidebar-header {
          padding: 1.5rem 1rem;
          display: flex;
          justify-content: space-between;
          align-items: center;
          border-bottom: 1px solid #2C2C2E;
        }
        .logo { display: flex; align-items: center; gap: 0.75rem; }
        .logo-icon { font-size: 1.5rem; }
        .logo-text { font-weight: 600; font-size: 1.25rem; background: linear-gradient(135deg, #007BFF, #D4AF37); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .toggle-btn { background: transparent; border: none; color: #8E8E93; cursor: pointer; padding: 0.25rem; }
        
        .sidebar-nav { flex: 1; padding: 1rem 0; }
        .nav-item {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          width: 100%;
          padding: 0.75rem 1rem;
          background: transparent;
          border: none;
          color: #8E8E93;
          cursor: pointer;
          transition: all 0.2s;
          text-align: left;
        }
        .nav-item:hover { background: #1e1e20; color: #FFFFFF; }
        .nav-item.active { background: #1e1e20; color: #007BFF; border-left: 3px solid #007BFF; }
        .sidebar.collapsed .nav-item { justify-content: center; padding: 0.75rem; }
        
        .sidebar-footer { padding: 1rem; border-top: 1px solid #2C2C2E; }
        .logout { color: #EF4444; }
        .logout:hover { background: rgba(239,68,68,0.1); }
      `}</style>
    </div>
  );
}
