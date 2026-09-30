import type { Comparison } from '../types';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { TrendingDown, Clock, Leaf } from 'lucide-react';

export default function ComparisonPage({ api }: { api: any }) {
  const comparison: Comparison | null = api.comparison;

  if (!comparison) return <div>Loading...</div>;

  return (
    <div className="space-y-8">
      <div className="text-center mb-10">
        <h2 className="text-4xl font-bold mb-4">Baseline vs AI Performance</h2>
        <p className="text-slate-400 text-lg">Over the last {comparison.period_days} days</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-xl border border-slate-700 p-8 text-center relative overflow-hidden">
          <div className="absolute top-0 right-0 p-4 opacity-10"><TrendingDown className="w-24 h-24" /></div>
          <h3 className="text-slate-400 font-medium mb-2">Fuel Saved</h3>
          <div className="text-5xl font-bold text-accent-orange mb-2">{comparison.fuel_saved_pct.toFixed(1)}%</div>
          <div className="text-sm text-slate-400">
            {Math.round(comparison.ai.fuel_litres).toLocaleString()} L vs {Math.round(comparison.baseline.fuel_litres).toLocaleString()} L
          </div>
        </div>

        <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-xl border border-slate-700 p-8 text-center relative overflow-hidden">
          <div className="absolute top-0 right-0 p-4 opacity-10"><Clock className="w-24 h-24" /></div>
          <h3 className="text-slate-400 font-medium mb-2">Generator Hours</h3>
          <div className="text-5xl font-bold text-icy-blue mb-2">{Math.round(comparison.ai.generator_hours)}h</div>
          <div className="text-sm text-slate-400">
            Down from {Math.round(comparison.baseline.generator_hours)}h
          </div>
        </div>

        <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-xl border border-slate-700 p-8 text-center relative overflow-hidden">
          <div className="absolute top-0 right-0 p-4 opacity-10"><Leaf className="w-24 h-24" /></div>
          <h3 className="text-slate-400 font-medium mb-2">Renewable Share</h3>
          <div className="text-5xl font-bold text-green-400 mb-2">{comparison.ai.renewable_pct.toFixed(1)}%</div>
          <div className="text-sm text-slate-400">
            Up from {comparison.baseline.renewable_pct.toFixed(1)}%
          </div>
        </div>
      </div>

      <div className="bg-slate-900 rounded-xl border border-slate-800 p-6 h-[400px]">
        <h3 className="text-xl font-bold mb-6">Cumulative Fuel Consumption</h3>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={comparison.series} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorBase" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#94a3b8" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#94a3b8" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorAI" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ff8c42" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#ff8c42" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
            <XAxis dataKey="day" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b' }} />
            <Legend />
            <Area type="monotone" dataKey="baseline_fuel_l" name="Baseline (L)" stroke="#94a3b8" fillOpacity={1} fill="url(#colorBase)" />
            <Area type="monotone" dataKey="ai_fuel_l" name="AI Managed (L)" stroke="#ff8c42" fillOpacity={1} fill="url(#colorAI)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
