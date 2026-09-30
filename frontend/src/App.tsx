import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Activity, Battery, BarChart2, Bell, Settings, Wind, Zap, Navigation } from 'lucide-react';
import Overview from './pages/Overview';
import Forecasts from './pages/Forecasts';
import Optimizer from './pages/Optimizer';
import FuelAutonomy from './pages/FuelAutonomy';
import Comparison from './pages/Comparison';
import Alerts from './pages/Alerts';
import LoadControl from './pages/LoadControl';
import { usePolarApi } from './hooks/usePolarApi';

function Sidebar() {
  const location = useLocation();
  const links = [
    { to: '/', icon: Activity, label: 'Overview' },
    { to: '/forecasts', icon: BarChart2, label: 'Forecasts' },
    { to: '/optimizer', icon: Zap, label: 'Optimizer' },
    { to: '/fuel', icon: Battery, label: 'Fuel Autonomy' },
    { to: '/comparison', icon: Wind, label: 'Comparison' },
    { to: '/alerts', icon: Bell, label: 'Alerts' },
    { to: '/loads', icon: Settings, label: 'Load Control' },
  ];

  return (
    <div className="w-64 bg-slate-900 h-screen flex flex-col border-r border-slate-800">
      <div className="p-6 flex items-center gap-3">
        <Navigation className="w-8 h-8 text-accent-orange" />
        <span className="text-xl font-bold text-icy-light">PolarGrid AI</span>
      </div>
      <nav className="flex-1 px-4 space-y-2">
        {links.map((link) => {
          const Icon = link.icon;
          const active = location.pathname === link.to;
          return (
            <Link
              key={link.to}
              to={link.to}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                active ? 'bg-slate-800 text-accent-orange' : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
              }`}
            >
              <Icon className="w-5 h-5" />
              {link.label}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-icy-dark text-slate-200 overflow-hidden">
      <Sidebar />
      <main className="flex-1 flex flex-col h-screen overflow-y-auto relative">
        <header className="h-16 border-b border-slate-800 flex items-center justify-between px-8 bg-slate-900/50 backdrop-blur sticky top-0 z-10">
          <h2 className="text-xl font-semibold">Dashboard</h2>
        </header>
        <div className="p-8 flex-1">
          {children}
        </div>
      </main>
    </div>
  );
}

export default function App() {
  const api = usePolarApi();

  if (api.error) {
    return <div className="flex items-center justify-center h-screen text-red-400 font-bold">{api.error}</div>;
  }

  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Overview api={api} />} />
          <Route path="/forecasts" element={<Forecasts api={api} />} />
          <Route path="/optimizer" element={<Optimizer api={api} />} />
          <Route path="/fuel" element={<FuelAutonomy api={api} />} />
          <Route path="/comparison" element={<Comparison api={api} />} />
          <Route path="/alerts" element={<Alerts api={api} />} />
          <Route path="/loads" element={<LoadControl api={api} />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
