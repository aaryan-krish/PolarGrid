import type { Status } from '../types';
import { Battery, Thermometer, Wind, Droplet, AlertTriangle, Zap, Activity } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  icon: React.ElementType;
  alert?: boolean;
}

function MetricCard({ title, value, unit, icon: Icon, alert }: MetricCardProps) {
  return (
    <div className={`p-6 rounded-xl border ${alert ? 'bg-red-900/20 border-red-500/50 text-red-200' : 'bg-slate-900 border-slate-800'}`}>
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-slate-400 font-medium text-sm">{title}</h3>
        <Icon className={`w-5 h-5 ${alert ? 'text-red-400' : 'text-icy-blue'}`} />
      </div>
      <div className="flex items-baseline gap-1">
        <span className="text-3xl font-bold">{value}</span>
        {unit && <span className="text-sm font-medium text-slate-400">{unit}</span>}
      </div>
    </div>
  );
}

export default function Overview({ api }: { api: any }) {
  const status: Status | null = api.status;

  if (!status) return <div className="animate-pulse flex gap-4"><div className="h-32 bg-slate-800 rounded-xl w-1/4"></div></div>;

  return (
    <div className="space-y-6">
      {status.blizzard_mode && (
        <div className="bg-red-500/20 border border-red-500 text-red-200 px-6 py-4 rounded-xl flex items-center gap-4 animate-pulse">
          <AlertTriangle className="w-6 h-6" />
          <div>
            <h3 className="font-bold text-lg">Blizzard Mode Active</h3>
            <p className="text-sm opacity-80">Extreme weather conditions detected. Operating in high-conservation mode.</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard title="System Mode" value={status.mode} icon={Zap} alert={status.mode === 'SAFE'} />
        <MetricCard title="Battery Level" value={status.battery_soc_pct.toFixed(1)} unit="%" icon={Battery} alert={status.battery_soc_pct < 20} />
        <MetricCard title="Fuel Level" value={Math.round(status.fuel_litres).toLocaleString()} unit="L" icon={Droplet} />
        <MetricCard title="Wind Speed" value={status.wind_speed_ms.toFixed(1)} unit="m/s" icon={Wind} alert={status.wind_speed_ms > 20} />
        <MetricCard title="Ambient Temp" value={status.ambient_temp_c.toFixed(1)} unit="°C" icon={Thermometer} />
        <MetricCard title="Battery Temp" value={status.battery_temp_c.toFixed(1)} unit="°C" icon={Thermometer} alert={status.battery_temp_c < -10} />
      </div>

      <div className="bg-slate-900 rounded-xl border border-slate-800 p-8 mt-8">
        <h3 className="text-xl font-bold mb-8 flex items-center gap-2"><Activity className="text-accent-orange" /> Energy Flow Diagram</h3>
        
        <div className="relative h-64 max-w-4xl mx-auto">
          {/* Layout for diagram */}
          <div className="absolute top-0 left-0 w-32 text-center">
            <div className="w-16 h-16 mx-auto bg-slate-800 rounded-full flex items-center justify-center border-2 border-yellow-500">
              <span className="text-yellow-500 font-bold">SOLAR</span>
            </div>
            <div className="mt-2 font-mono text-lg">{status.solar_kw.toFixed(1)} kW</div>
          </div>

          <div className="absolute top-0 right-0 w-32 text-center">
            <div className="w-16 h-16 mx-auto bg-slate-800 rounded-full flex items-center justify-center border-2 border-teal-400">
              <span className="text-teal-400 font-bold">WIND</span>
            </div>
            <div className="mt-2 font-mono text-lg">{status.wind_kw.toFixed(1)} kW</div>
          </div>

          <div className="absolute bottom-0 left-0 w-32 text-center">
            <div className="w-16 h-16 mx-auto bg-slate-800 rounded-full flex items-center justify-center border-2 border-orange-500">
              <span className="text-orange-500 font-bold">GEN</span>
            </div>
            <div className="mt-2 font-mono text-lg">{status.generator_kw.toFixed(1)} kW</div>
            <div className="text-xs text-slate-400">{status.generator_on ? 'RUNNING' : 'STANDBY'}</div>
          </div>

          <div className="absolute bottom-0 right-0 w-32 text-center">
            <div className="w-16 h-16 mx-auto bg-slate-800 rounded-full flex items-center justify-center border-2 border-green-500">
              <span className="text-green-500 font-bold">BATT</span>
            </div>
            <div className="mt-2 font-mono text-lg">{status.battery_kw > 0 ? '+' : ''}{status.battery_kw.toFixed(1)} kW</div>
          </div>

          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-40 text-center z-10">
            <div className="w-24 h-24 mx-auto bg-slate-800 rounded-full flex flex-col items-center justify-center border-4 border-icy-blue shadow-[0_0_30px_rgba(160,196,255,0.2)]">
              <span className="text-icy-blue font-bold text-sm">LOAD</span>
              <span className="font-mono font-bold text-xl">{status.load_kw.toFixed(1)}</span>
              <span className="text-xs text-slate-400">kW</span>
            </div>
          </div>
          
          {/* SVG connecting lines (animated dashed lines) */}
          <svg className="absolute inset-0 w-full h-full -z-0 pointer-events-none" style={{ filter: 'drop-shadow(0 0 5px rgba(255,255,255,0.2))' }}>
            <path d="M 64 64 L 400 128" stroke="#eab308" strokeWidth="2" fill="none" strokeDasharray="5,5" className={status.solar_kw > 0 ? 'animate-[dash_1s_linear_infinite]' : 'opacity-20'} />
            <path d="M 832 64 L 496 128" stroke="#2dd4bf" strokeWidth="2" fill="none" strokeDasharray="5,5" className={status.wind_kw > 0 ? 'animate-[dash_1s_linear_infinite_reverse]' : 'opacity-20'} />
            <path d="M 64 192 L 400 128" stroke="#f97316" strokeWidth="2" fill="none" strokeDasharray="5,5" className={status.generator_kw > 0 ? 'animate-[dash_1s_linear_infinite]' : 'opacity-20'} />
            <path d="M 832 192 L 496 128" stroke="#22c55e" strokeWidth="2" fill="none" strokeDasharray="5,5" className={status.battery_kw !== 0 ? (status.battery_kw > 0 ? 'animate-[dash_1s_linear_infinite_reverse]' : 'animate-[dash_1s_linear_infinite]') : 'opacity-20'} />
          </svg>
        </div>
      </div>
      <style>{`
        @keyframes dash { to { stroke-dashoffset: -20; } }
      `}</style>
    </div>
  );
}
