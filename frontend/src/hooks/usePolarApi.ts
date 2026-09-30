import { useState, useEffect, useCallback, useRef } from 'react';
import type { Status, Forecast, Schedule, Autonomy, Alert, Comparison, Load } from '../types';
import * as mockData from '../api/mock';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';
const WS_URL = API_URL.replace(/^http/, 'ws') + '/ws/live';

interface ApiState {
  status: Status | null;
  forecast: Forecast | null;
  schedule: Schedule | null;
  autonomy: Autonomy | null;
  alerts: Alert[] | null;
  comparison: Comparison | null;
  loads: Load[] | null;
  isConnected: boolean;
  isMock: boolean;
  error: string | null;
}

export function usePolarApi() {
  const [state, setState] = useState<ApiState>({
    status: USE_MOCK ? mockData.mockStatus : null,
    forecast: USE_MOCK ? mockData.mockForecast : null,
    schedule: USE_MOCK ? mockData.mockSchedule : null,
    autonomy: USE_MOCK ? mockData.mockAutonomy : null,
    alerts: USE_MOCK ? mockData.mockAlerts : null,
    comparison: USE_MOCK ? mockData.mockComparison : null,
    loads: USE_MOCK ? mockData.mockLoads : null,
    isConnected: false,
    isMock: USE_MOCK,
    error: null,
  });

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const fetchRestData = useCallback(async () => {
    if (USE_MOCK) return;
    try {
      const [forecastRes, scheduleRes, autonomyRes, alertsRes, comparisonRes, loadsRes] = await Promise.all([
        fetch(`${API_URL}/api/forecast?hours=48`),
        fetch(`${API_URL}/api/schedule`),
        fetch(`${API_URL}/api/autonomy`),
        fetch(`${API_URL}/api/alerts`),
        fetch(`${API_URL}/api/comparison`),
        fetch(`${API_URL}/api/loads`)
      ]);

      if (!forecastRes.ok) throw new Error("Failed to fetch");

      const [forecast, schedule, autonomy, alerts, comparison, loads] = await Promise.all([
        forecastRes.json(),
        scheduleRes.json(),
        autonomyRes.json(),
        alertsRes.json(),
        comparisonRes.json(),
        loadsRes.json()
      ]);

      setState(prev => ({
        ...prev,
        forecast,
        schedule,
        autonomy,
        alerts,
        comparison,
        loads,
        error: null,
        isMock: false
      }));
    } catch (err) {
      console.error("REST fetch failed, falling back to mock", err);
      setState(prev => ({
        ...prev,
        forecast: mockData.mockForecast,
        schedule: mockData.mockSchedule,
        autonomy: mockData.mockAutonomy,
        alerts: mockData.mockAlerts,
        comparison: mockData.mockComparison,
        loads: mockData.mockLoads,
        error: "Failed to fetch data, using mock data.",
        isMock: true
      }));
    }
  }, []);

  const connectWs = useCallback(() => {
    if (USE_MOCK) return;
    
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      setState(prev => ({ ...prev, isConnected: true }));
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setState(prev => ({ ...prev, status: data }));
      } catch (e) {
        console.error("Invalid WS message", e);
      }
    };

    ws.onclose = () => {
      setState(prev => ({ ...prev, isConnected: false }));
      // Auto reconnect
      reconnectTimeoutRef.current = setTimeout(connectWs, 3000);
    };

    ws.onerror = () => {
      ws.close();
    };
  }, []);

  useEffect(() => {
    fetchRestData();
    const pollInterval = setInterval(fetchRestData, 60000); // refresh non-live data every minute

    connectWs();

    return () => {
      clearInterval(pollInterval);
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [fetchRestData, connectWs]);

  const toggleLoad = async (id: string, enabled: boolean) => {
    if (state.isMock) {
      setState(prev => ({
        ...prev,
        loads: prev.loads?.map(l => l.id === id ? { ...l, enabled } : l) || null
      }));
      return;
    }
    
    try {
      const res = await fetch(`${API_URL}/api/loads/${id}/toggle`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled })
      });
      if (res.ok) {
        const updatedLoad = await res.json();
        setState(prev => ({
          ...prev,
          loads: prev.loads?.map(l => l.id === id ? updatedLoad : l) || null
        }));
      }
    } catch (e) {
      console.error("Failed to toggle load", e);
    }
  };

  const setMode = async (mode: "AI" | "BASELINE" | "SAFE") => {
    if (state.isMock) {
      setState(prev => ({
        ...prev,
        status: prev.status ? { ...prev.status, mode } : null
      }));
      return;
    }

    try {
      const res = await fetch(`${API_URL}/api/mode`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode })
      });
      if (res.ok) {
        const data = await res.json();
        setState(prev => ({
          ...prev,
          status: prev.status ? { ...prev.status, mode: data.mode } : null
        }));
      }
    } catch (e) {
      console.error("Failed to set mode", e);
    }
  };

  return { ...state, toggleLoad, setMode };
}
