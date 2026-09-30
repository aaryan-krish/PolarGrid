import type { Schedule } from '../types';
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, ComposedChart, Line, Bar } from 'recharts';

export default function Optimizer({ api }: { api: any }) {
  const schedule: Schedule | null = api.schedule;

  if (!schedule) return <div>Loading...</div>;

  const data = schedule.points.map(p => ({
    time: new Date(p.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    generator: Math.round(p.generator_kw),
    battery: Math.round(p.battery_kw),
    deferred: Math.round(p.deferred_load_kw),
    soc: Math.round(p.soc_pct),
  }));

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-2xl font-bold">AI Optimizer Schedule</h2>
          <p className="text-slate-400">Next {schedule.horizon_hours} hours</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl px-6 py-3 text-right">
          <div className="text-sm text-slate-400 font-medium">Estimated Fuel Required</div>
          <div className="text-2xl font-bold text-accent-orange">{schedule.est_fuel_litres.toFixed(1)} L</div>
        </div>
      </div>

      <div className="bg-slate-900 rounded-xl border border-slate-800 p-6 h-[500px]">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
            <XAxis dataKey="time" stroke="#94a3b8" />
            <YAxis yAxisId="left" stroke="#94a3b8" />
            <YAxis yAxisId="right" orientation="right" stroke="#94a3b8" />
            <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b' }} />
            <Legend />
            <Bar yAxisId="left" dataKey="generator" name="Generator (kW)" fill="#f97316" opacity={0.8} />
            <Bar yAxisId="left" dataKey="battery" name="Battery (kW)" fill="#22c55e" opacity={0.8} />
            <Bar yAxisId="left" dataKey="deferred" name="Deferred Load (kW)" fill="#a855f7" opacity={0.8} />
            <Line yAxisId="right" type="monotone" dataKey="soc" name="Battery SOC (%)" stroke="#3b82f6" strokeWidth={3} dot={false} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
