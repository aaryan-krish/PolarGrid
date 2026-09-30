export interface Status {
  timestamp: string;
  mode: "AI" | "BASELINE" | "SAFE";
  load_kw: number;
  solar_kw: number;
  wind_kw: number;
  generator_kw: number;
  generator_on: boolean;
  battery_soc_pct: number;
  battery_kw: number;
  battery_temp_c: number;
  fuel_litres: number;
  ambient_temp_c: number;
  wind_speed_ms: number;
  blizzard_mode: boolean;
}

export interface ForecastPoint {
  time: string;
  load_kw: number;
  solar_kw: number;
  wind_kw: number;
}

export interface Forecast {
  generated_at: string;
  step_minutes: number;
  points: ForecastPoint[];
}

export interface SchedulePoint {
  time: string;
  generator_kw: number;
  battery_kw: number;
  deferred_load_kw: number;
  soc_pct: number;
}

export interface Schedule {
  horizon_hours: number;
  est_fuel_litres: number;
  points: SchedulePoint[];
}

export interface Autonomy {
  fuel_litres: number;
  avg_daily_burn_l: number;
  days_remaining: number;
  days_to_resupply: number;
  status: "OK" | "WARNING" | "CRITICAL";
  recommendation: string;
}

export interface Alert {
  id: string;
  time: string;
  severity: "info" | "warning" | "critical";
  type: string;
  message: string;
}

export interface ComparisonSeriesPoint {
  day: number;
  baseline_fuel_l: number;
  ai_fuel_l: number;
}

export interface ComparisonMetrics {
  fuel_litres: number;
  generator_hours: number;
  renewable_pct: number;
}

export interface Comparison {
  period_days: number;
  fuel_saved_pct: number;
  baseline: ComparisonMetrics;
  ai: ComparisonMetrics;
  series: ComparisonSeriesPoint[];
}

export interface Load {
  id: string;
  name: string;
  priority: "critical" | "deferrable";
  kw: number;
  enabled: boolean;
}
