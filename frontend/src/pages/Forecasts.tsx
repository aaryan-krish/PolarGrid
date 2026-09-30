import { useState } from 'react';
import type { Forecast } from '../types';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

export default function Forecasts({ api }: { api: any }) {
  const forecast: Forecast | null = api.forecast;
  const [horizon, setHorizon] = useState<number>(48);

  if (!forecast) return <div>Loading...</div>;

  const data = forecast.points.slice(0, horizon).map(p => ({
    time: new Date(p.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    load: Math.round(p.load_kw),
    solar: Math.round(p.solar_kw),
    wind: Math.round(p.wind_kw),
  }));

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Renewable & Load Forecast</h2>
        <div className="flex gap-2 bg-slate-900 rounded-lg p-1 border border-slate-800">
          {[24, 48, 168].map(h => (
            <button
              key={h}
              onClick={() => setHorizon(h)}
              className={`px-4 py-1 text-sm rounded-md transition-colors ${horizon === h ? 'bg-slate-700 text-white font-bold' : 'text-slate-400 hover:text-white'}`}
            >
              {h}h
            </button>
          ))}
        </div>
      </div>

      <div className="bg-slate-900 rounded-xl border border-slate-800 p-6 h-[500px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorLoad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorSolar" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#eab308" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#eab308" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorWind" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2dd4bf" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#2dd4bf" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
            <XAxis dataKey="time" stroke="#94a3b8" tick={{ fill: '#94a3b8' }} />
            <YAxis stroke="#94a3b8" tick={{ fill: '#94a3b8' }} />
            <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b' }} />
            <Legend />
            <Area type="monotone" dataKey="load" name="Load (kW)" stroke="#ef4444" fillOpacity={1} fill="url(#colorLoad)" />
            <Area type="monotone" dataKey="solar" name="Solar (kW)" stroke="#eab308" fillOpacity={1} fill="url(#colorSolar)" />
            <Area type="monotone" dataKey="wind" name="Wind (kW)" stroke="#2dd4bf" fillOpacity={1} fill="url(#colorWind)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
