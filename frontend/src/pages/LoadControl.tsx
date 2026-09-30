import type { Load } from '../types';
import { Shield, Settings, Zap } from 'lucide-react';

export default function LoadControl({ api }: { api: any }) {
  const loads: Load[] = api.loads || [];
  const currentMode = api.status?.mode || 'AI';

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <div>
        <h2 className="text-2xl font-bold mb-6">System Mode</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { id: 'AI', name: 'AI Optimizer', icon: Zap, desc: 'Dynamic load shedding & fuel optimization' },
            { id: 'BASELINE', name: 'Baseline', icon: Settings, desc: 'Standard operating procedure (heuristic)' },
            { id: 'SAFE', name: 'Safe Mode', icon: Shield, desc: 'Critical loads only, max conservation' }
          ].map(mode => {
            const Icon = mode.icon;
            const active = currentMode === mode.id;
            return (
              <button
                key={mode.id}
                onClick={() => api.setMode(mode.id)}
                className={`p-6 rounded-xl border text-left transition-all ${
                  active 
                    ? 'bg-slate-800 border-accent-orange ring-1 ring-accent-orange' 
                    : 'bg-slate-900 border-slate-800 hover:border-slate-600'
                }`}
              >
                <div className="flex items-center gap-3 mb-2">
                  <Icon className={`w-6 h-6 ${active ? 'text-accent-orange' : 'text-slate-400'}`} />
                  <h3 className={`font-bold ${active ? 'text-white' : 'text-slate-300'}`}>{mode.name}</h3>
                </div>
                <p className="text-sm text-slate-500">{mode.desc}</p>
              </button>
            );
          })}
        </div>
      </div>

      <div>
        <h2 className="text-2xl font-bold mb-6">Load Management</h2>
        <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden">
          {loads.map((load, i) => (
            <div key={load.id} className={`p-6 flex items-center justify-between ${i !== loads.length - 1 ? 'border-b border-slate-800' : ''}`}>
              <div>
                <div className="flex items-center gap-3 mb-1">
                  <h3 className="font-bold text-lg">{load.name}</h3>
                  {load.priority === 'critical' && (
                    <span className="bg-red-500/20 text-red-400 text-xs px-2 py-0.5 rounded font-bold uppercase tracking-wider">
                      Critical
                    </span>
                  )}
                </div>
                <p className="text-slate-400">{load.kw} kW</p>
              </div>
              
              <button
                onClick={() => {
                  if (load.priority !== 'critical') {
                    api.toggleLoad(load.id, !load.enabled);
                  }
                }}
                disabled={load.priority === 'critical'}
                className={`relative inline-flex h-8 w-14 items-center rounded-full transition-colors ${
                  load.enabled ? 'bg-green-500' : 'bg-slate-600'
                } ${load.priority === 'critical' ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
              >
                <span
                  className={`inline-block h-6 w-6 transform rounded-full bg-white transition-transform ${
                    load.enabled ? 'translate-x-7' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
