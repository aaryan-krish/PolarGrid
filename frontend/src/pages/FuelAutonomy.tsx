import type { Autonomy } from '../types';
import { AlertCircle, CheckCircle2, ShieldAlert } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

export default function FuelAutonomy({ api }: { api: any }) {
  const autonomy: Autonomy | null = api.autonomy;

  if (!autonomy) return <div>Loading...</div>;

  const data = [
    { name: 'Remaining', value: autonomy.days_remaining },
    { name: 'Buffer', value: Math.max(0, (autonomy.days_to_resupply * 1.5) - autonomy.days_remaining) }
  ];

  let color = '#22c55e'; // OK
  let Icon = CheckCircle2;
  if (autonomy.status === 'WARNING') {
    color = '#eab308';
    Icon = AlertCircle;
  } else if (autonomy.status === 'CRITICAL') {
    color = '#ef4444';
    Icon = ShieldAlert;
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold">Fuel Autonomy Analysis</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-900 rounded-xl border border-slate-800 p-8 flex flex-col items-center justify-center">
          <div className="w-64 h-64 relative">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="50%"
                  innerRadius={80}
                  outerRadius={100}
                  startAngle={180}
                  endAngle={0}
                  dataKey="value"
                  stroke="none"
                >
                  <Cell fill={color} />
                  <Cell fill="#1e293b" />
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center mt-[-20px]">
              <div className="text-4xl font-bold" style={{ color }}>{autonomy.days_remaining.toFixed(1)}</div>
              <div className="text-sm text-slate-400">Days Remaining</div>
            </div>
          </div>
          
          <div className="text-center mt-4 space-y-1">
            <div className="text-slate-400">Target Resupply</div>
            <div className="text-2xl font-medium">{autonomy.days_to_resupply} Days</div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-slate-900 rounded-xl border border-slate-800 p-6">
            <div className="flex items-start gap-4">
              <Icon className="w-8 h-8 mt-1" style={{ color }} />
              <div>
                <h3 className="text-lg font-bold" style={{ color }}>Status: {autonomy.status}</h3>
                <p className="text-slate-300 mt-2 leading-relaxed">{autonomy.recommendation}</p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-900 rounded-xl border border-slate-800 p-6">
              <div className="text-slate-400 text-sm mb-2">Total Fuel</div>
              <div className="text-2xl font-bold">{Math.round(autonomy.fuel_litres).toLocaleString()} L</div>
            </div>
            <div className="bg-slate-900 rounded-xl border border-slate-800 p-6">
              <div className="text-slate-400 text-sm mb-2">Avg Daily Burn</div>
              <div className="text-2xl font-bold">{Math.round(autonomy.avg_daily_burn_l).toLocaleString()} L</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
