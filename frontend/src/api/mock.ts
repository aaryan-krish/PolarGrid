import type { Status, Forecast, Schedule, Autonomy, Alert, Comparison, Load } from '../types';

export const mockStatus: Status = {
  timestamp: new Date().toISOString(),
  mode: "AI",
  load_kw: 62.5,
  solar_kw: 15.0,
  wind_kw: 25.0,
  generator_kw: 0,
  generator_on: false,
  battery_soc_pct: 85.0,
  battery_kw: 22.5,
  battery_temp_c: 5.5,
  fuel_litres: 8500,
  ambient_temp_c: -15.0,
  wind_speed_ms: 12.5,
  blizzard_mode: false,
};

export const mockForecast: Forecast = {
  generated_at: new Date().toISOString(),
  step_minutes: 60,
  points: Array.from({ length: 48 }).map((_, i) => {
    const time = new Date();
    time.setHours(time.getHours() + i);
    return {
      time: time.toISOString(),
      load_kw: 50 + Math.random() * 20,
      solar_kw: (i % 24 > 6 && i % 24 < 18) ? 20 + Math.random() * 10 : 0,
      wind_kw: 10 + Math.random() * 30,
    };
  }),
};

export const mockSchedule: Schedule = {
  horizon_hours: 48,
  est_fuel_litres: 120,
  points: Array.from({ length: 48 }).map((_, i) => {
    const time = new Date();
    time.setHours(time.getHours() + i);
    return {
      time: time.toISOString(),
      generator_kw: Math.random() > 0.8 ? 50 : 0,
      battery_kw: (Math.random() - 0.5) * 40,
      deferred_load_kw: Math.random() > 0.5 ? 10 : 0,
      soc_pct: 50 + Math.random() * 40,
    };
  }),
};

export const mockAutonomy: Autonomy = {
  fuel_litres: 8500,
  avg_daily_burn_l: 150,
  days_remaining: 56.6,
  days_to_resupply: 30,
  status: "OK",
  recommendation: "Fuel levels are sufficient until next resupply.",
};

export const mockAlerts: Alert[] = [
  { id: "1", time: new Date().toISOString(), severity: "info", type: "system", message: "AI Optimizer updated schedule" },
  { id: "2", time: new Date(Date.now() - 3600000).toISOString(), severity: "warning", type: "weather", message: "High wind speeds detected" },
];

export const mockComparison: Comparison = {
  period_days: 30,
  fuel_saved_pct: 25.5,
  baseline: { fuel_litres: 4500, generator_hours: 720, renewable_pct: 45 },
  ai: { fuel_litres: 3350, generator_hours: 410, renewable_pct: 68 },
  series: Array.from({ length: 30 }).map((_, i) => ({
    day: i + 1,
    baseline_fuel_l: 150 + Math.random() * 20,
    ai_fuel_l: 100 + Math.random() * 30,
  })),
};

export const mockLoads: Load[] = [
  { id: "l1", name: "Life Support", priority: "critical", kw: 25, enabled: true },
  { id: "l2", name: "Communications", priority: "critical", kw: 10, enabled: true },
  { id: "l3", name: "Science Lab A", priority: "deferrable", kw: 15, enabled: true },
  { id: "l4", name: "Water Heater", priority: "deferrable", kw: 20, enabled: false },
];
