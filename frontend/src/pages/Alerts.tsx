import { useState } from 'react';
import type { Alert } from '../types';
import { Info, AlertTriangle, ShieldAlert, Clock } from 'lucide-react';

export default function Alerts({ api }: { api: any }) {
  const alerts: Alert[] = api.alerts || [];
  const [filter, setFilter] = useState<'all' | 'info' | 'warning' | 'critical'>('all');

  const filteredAlerts = alerts.filter(a => filter === 'all' || a.severity === filter);

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">System Alerts</h2>
        <div className="flex gap-2">
          {['all', 'critical', 'warning', 'info'].map(f => (
            <button
              key={f}
              onClick={() => setFilter(f as any)}
              className={`px-4 py-2 text-sm rounded-lg capitalize transition-colors ${
                filter === f ? 'bg-slate-700 text-white font-bold' : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        {filteredAlerts.length === 0 ? (
          <div className="text-center py-12 text-slate-500 bg-slate-900 rounded-xl border border-slate-800">
            No alerts found.
          </div>
        ) : (
          filteredAlerts.map(alert => {
            let Icon = Info;
            let colorClass = 'text-blue-400';
            let bgClass = 'bg-slate-900 border-slate-800';

            if (alert.severity === 'warning') {
              Icon = AlertTriangle;
              colorClass = 'text-yellow-400';
            } else if (alert.severity === 'critical') {
              Icon = ShieldAlert;
              colorClass = 'text-red-400';
              bgClass = 'bg-red-950/20 border-red-900/50';
            }

            return (
              <div key={alert.id} className={`p-6 rounded-xl border flex items-start gap-4 ${bgClass}`}>
                <Icon className={`w-6 h-6 mt-1 ${colorClass}`} />
                <div className="flex-1">
                  <div className="flex justify-between items-start mb-1">
                    <h3 className="font-bold capitalize">{alert.type.replace('_', ' ')}</h3>
                    <div className="flex items-center gap-1 text-sm text-slate-500">
                      <Clock className="w-4 h-4" />
                      {new Date(alert.time).toLocaleString()}
                    </div>
                  </div>
                  <p className="text-slate-300">{alert.message}</p>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
