# Componentes React - FINAX OS

Estrutura de componentes prontos para integração com React/Next.js

## 📁 Estrutura

```
assets/
├── components/
│   ├── Sidebar.jsx          # Menu lateral minimalista
│   ├── KPICards.jsx         # Cards de KPIs do dashboard
│   ├── FinaXPay.jsx         # Sistema de pagamentos digital
│   ├── ConfirmModal.jsx     # Modal de confirmação
│   ├── EmptyState.jsx       # Estado vazio
│   ├── OfflineBanner.jsx    # Banner de modo offline
│   ├── SecurityBadge.jsx    # Badge de segurança
│   └── index.js             # Exportações centralizadas
├── theme_config.json        # Configuração de tema global
└── COMPONENTS_README.md     # Este arquivo
```

## 🎨 Tema Global

O arquivo `theme_config.json` contém toda a configuração visual:

- **Cores**: Dark mode profissional (#101012 background)
- **Tipografia**: Inter/Geist Sans
- **Espaçamento**: Valores padronizados (xs, sm, md, lg, xl)
- **Border Radius**: 4 níveis (sm, md, lg, xl)
- **Sombras**: 3 intensidades (sm, md, lg)
- **Animações**: Transições suaves 0.2s ease

## 📦 Instalação

### Dependências necessárias:

```bash
npm install lucide-react react
```

### Importação de componentes:

```javascript
import { Sidebar, KPICards, FinaXPay, BIDashboard } from './assets/components';
```

Ou importação individual:

```javascript
import Sidebar from './assets/components/Sidebar';
import BIDashboard from './assets/components/BIDashboard';
```

## 🔧 Componentes

### Sidebar

Menu lateral com navegação colapsável.

**Props:**
- `activePage` (string): Página ativa
- `setActivePage` (function): Callback para mudar página
- `isCollapsed` (boolean): Estado colapsado
- `setIsCollapsed` (function): Callback para colapsar

**Exemplo:**

```jsx
import { Sidebar } from './assets/components';

export default function App() {
  const [activePage, setActivePage] = useState('dashboard');
  const [isCollapsed, setIsCollapsed] = useState(false);
  
  return (
    <Sidebar 
      activePage={activePage}
      setActivePage={setActivePage}
      isCollapsed={isCollapsed}
      setIsCollapsed={setIsCollapsed}
    />
  );
}
```

### KPICards

Cards de indicadores-chave de desempenho.

**Props:**
- `data` (object): 
  - `saldo`: Saldo em caixa
  - `inadimplencia`: Percentual de inadimplência
  - `proximoPagamento`: Dados do próximo pagamento

**Exemplo:**

```jsx
import { KPICards } from './assets/components';

<KPICards 
  data={{
    saldo: 150000,
    inadimplencia: 15,
    proximoPagamento: { dias: 12, data: '25/03/2026' }
  }}
/>
```

### FinaXPay

Sistema de pagamento digital com geração de QR codes.

**Props:**
- `aluno` (object): Dados do aluno { id, nome }
- `valor` (number): Valor a pagar
- `onPay` (function): Callback para gerar QR code
- `onUpload` (function): Callback para upload de comprovativo

**Exemplo:**

```jsx
import { FinaXPay } from './assets/components';

<FinaXPay 
  aluno={{ id: '123', nome: 'João Silva' }}
  valor={50000}
  onPay={() => console.log('Gerando QR')}
  onUpload={(e) => console.log(e.target.files[0])}
/>
```

### ConfirmModal

Modal de confirmação de ações.

**Props:**
- `isOpen` (boolean): Visibilidade do modal
- `onClose` (function): Callback para fechar
- `onConfirm` (function): Callback para confirmar
- `title` (string): Título do modal
- `message` (string): Mensagem
- `confirmText` (string): Texto do botão (padrão: "Confirmar")

**Exemplo:**

```jsx
import { ConfirmModal } from './assets/components';

const [showModal, setShowModal] = useState(false);

<ConfirmModal
  isOpen={showModal}
  title="Confirmar ação"
  message="Deseja realmente continuar?"
  confirmText="Sim, continuar"
  onClose={() => setShowModal(false)}
  onConfirm={() => { /* ação */ setShowModal(false); }}
/>
```

### EmptyState

Estado vazio para listas/tabelas vazias.

**Props:**
- `title` (string): Título
- `message` (string): Mensagem
- `icon` (string): Emoji/ícone
- `actionText` (string): Texto do botão (opcional)
- `onAction` (function): Callback do botão

**Exemplo:**

```jsx
<EmptyState
  title="Nenhum aluno encontrado"
  message="Comece adicionando seu primeiro aluno"
  icon="📚"
  actionText="Adicionar Aluno"
  onAction={() => console.log('Adicionar')}
/>
```

### OfflineBanner

Banner de modo offline com sincronização.

**Exemplo:**

```jsx
<OfflineBanner />
```

### SecurityBadge

Badge fixo de segurança no canto inferior direito.

**Exemplo:**

```jsx
<SecurityBadge />
```

### BIDashboard

Dashboard completo de Business Intelligence com KPIs, alertas e tendências.

**Props:**
- `kpis` (object): Dados de KPIs calculados
- `alertas` (array): Lista de alertas automáticos
- `tendencias` (array): Dados de tendências (últimos meses)

**Exemplo:**

```jsx
import { BIDashboard } from './assets/components';

const kpis = {
  alunos: { total: 150, devedores: 22, adimplentes: 128 },
  financeiro: { total_receitas: 2500000, saldo_atual: 700000, margem_lucro: 28.5 },
  propinas: { pendentes: 550000, pagas: 2500000 },
  salarios: { pendentes: 120000 },
  indicadores: { taxa_inadimplencia: 14.7, projecao_caixa: 1130000, saude_financeira: 85 }
};

const alertas = [
  { tipo: 'INADIMPLENCIA', severidade: 'ALTA', mensagem: 'Taxa acima de 20%' }
];

const tendencias = [
  // Dados dos últimos 6 meses
];

<BIDashboard kpis={kpis} alertas={alertas} tendencias={tendencias} />
```

**Funcionalidades:**
- Exibição de alertas por severidade
- Grid de KPIs principais
- Cards de receitas/despesas/pendências
- Gráfico de tendências (últimos 6 meses)
- Score de saúde financeira
- Formatação automática de moeda (AOA)

## 🎯 Tema e Estilo

Todos os componentes já incluem estilos CSS-in-JS e seguem a paleta de cores global:

- **Primary**: #007BFF (Azul)
- **Gold**: #D4AF37 (Destaque)
- **Success**: #10B981 (Verde)
- **Danger**: #EF4444 (Vermelho)
- **Warning**: #F59E0B (Amarelo)
- **Background**: #101012 (Preto profundo)
- **Surface**: #161618 (Cinza escuro)

## 🔌 Integração com Backend

Os componentes são agnósticos quanto ao backend, mas esperam receber dados estruturados:

### Exemplo com fetch:

```javascript
const [data, setData] = useState(null);

useEffect(() => {
  fetch('/api/dashboard')
    .then(r => r.json())
    .then(setData);
}, []);

if (!data) return <div>Carregando...</div>;

return (
  <KPICards 
    data={{
      saldo: data.saldo,
      inadimplencia: data.taxa_inadimplencia,
      proximoPagamento: data.proximo_pagamento
    }}
  />
);
```

## 📝 Customização

Para customizar cores/tema:

1. Edite `assets/theme_config.json`
2. Importe o tema em seu app
3. Use as variáveis CSS:

```css
:root {
  --primary: #007BFF;
  --gold: #D4AF37;
  /* ... */
}
```

## 📱 Responsividade

Os componentes são responsivos e funciona em:
- Desktop (1920px+)
- Tablet (768px - 1024px)
- Mobile (320px - 767px)

Breakpoints principais:
- `640px`: Mobile
- `768px`: Tablet
- `1024px`: Desktop
- `1280px`: Desktop XL

## 🚀 Performance

- Componentes otimizados com React.memo
- Mínimas re-renders
- CSS-in-JS para reduzir bundle
- Sem dependências externas pesadas (apenas lucide-react)

## 🔒 Segurança

- XSS protegido com React
- Sanitização de inputs
- CORS ready
- Encriptação E2E suportada

## 📧 Suporte

Para dúvidas ou sugestões, consulte a documentação do projeto.

---

**Versão**: 1.0.0  
**Última atualização**: 2026-03-31
