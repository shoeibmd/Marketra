import React, { useEffect, useState } from 'react';
import { api } from '../../../lib/api';
import { PanelProps } from '../../../types/panel';
import { Bell, Settings, History, CheckCircle, AlertTriangle, Shield, RefreshCw } from 'lucide-react';

export const PortfolioRiskAlertsPanel: React.FC<PanelProps> = () => {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setStatusFilter] = useState('ALL');

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const res = await api.getRiskAlerts(filter === 'ALL' ? undefined : filter);
      setAlerts(res);
    } catch (err) {
      console.error('Failed to load risk alerts:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [filter]);

  const handleMarkRead = async (id: string) => {
    try {
      await api.markRiskAlertRead(id);
      setAlerts((prev) => prev.map((a) => (a.id === id ? { ...a, is_read: true } : a)));
    } catch (err) {
      console.error('Failed to mark read:', err);
    }
  };

  return (
    <div className="space-y-3 font-mono text-xs text-slate-200">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-slate-400">
        <div className="flex items-center space-x-1.5">
          <Bell className="h-3.5 w-3.5 text-amber-400" />
          <span className="font-bold text-slate-200">Portfolio Risk Alerts Dashboard</span>
        </div>
        <div className="flex items-center space-x-2">
          <select
            value={filter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 text-slate-300 rounded px-1.5 py-0.5 text-[10px]"
          >
            <option value="ALL">All Alerts</option>
            <option value="TRIGGERED">Triggered</option>
            <option value="RECOVERED">Recovered</option>
          </select>
          <button
            onClick={fetchAlerts}
            className="p-1 hover:bg-slate-800 text-slate-400 rounded transition-colors"
          >
            <RefreshCw className="h-3 w-3" />
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-slate-500 animate-pulse p-4 text-center">Loading Risk Alerts...</div>
      ) : alerts.length === 0 ? (
        <div className="p-4 text-center text-slate-500 bg-slate-950 border border-slate-800 rounded">
          <CheckCircle className="h-5 w-3.5 mx-auto text-emerald-400 mb-1" />
          <span>No active risk alerts. Portfolio is operating within configured thresholds.</span>
        </div>
      ) : (
        <div className="space-y-2">
          {alerts.map((a) => (
            <div
              key={a.id}
              className={`p-2.5 rounded border text-xs space-y-1.5 transition-colors ${
                a.status === 'RECOVERED'
                  ? 'bg-slate-950/60 border-emerald-950 text-slate-300'
                  : a.severity === 'CRITICAL'
                  ? 'bg-red-950/30 border-red-900 text-red-200'
                  : 'bg-amber-950/30 border-amber-900 text-amber-200'
              }`}
            >
              <div className="flex items-center justify-between font-bold text-[11px]">
                <div className="flex items-center space-x-1.5">
                  <AlertTriangle className={`h-3.5 w-3.5 ${a.status === 'RECOVERED' ? 'text-emerald-400' : 'text-amber-400'}`} />
                  <span>{a.metric_name}</span>
                </div>
                <div className="flex items-center space-x-1.5">
                  <span className="text-[10px] bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800 font-normal">
                    {a.status}
                  </span>
                  {!a.is_read && (
                    <button
                      onClick={() => handleMarkRead(a.id)}
                      className="text-[9px] text-emerald-400 hover:underline"
                    >
                      Mark Read
                    </button>
                  )}
                </div>
              </div>

              <p className="text-[10px] text-slate-300">{a.explanation}</p>

              <div className="flex justify-between items-center text-[9px] text-slate-500 pt-1 border-t border-slate-800/60">
                <span>TRIGGERED: {new Date(a.triggered_at).toLocaleString()}</span>
                <span>
                  VALUE: {a.current_value} / THRESHOLD: {a.threshold_value}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export const PortfolioRiskAlertSettingsPanel: React.FC<PanelProps> = () => {
  const [prefs, setPrefs] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const fetchPrefs = async () => {
      try {
        const res = await api.getRiskAlertPreferences();
        setPrefs(res);
      } catch (err) {
        console.error('Failed to load risk preferences:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchPrefs();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await api.updateRiskAlertPreferences(prefs);
      setPrefs(res);
    } catch (err) {
      console.error('Failed to save preferences:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleReset = async () => {
    setLoading(true);
    try {
      const res = await api.resetRiskAlertPreferences();
      setPrefs(res);
    } catch (err) {
      console.error('Failed to reset preferences:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="text-slate-500 animate-pulse p-4 text-center">Loading Risk Settings...</div>;

  return (
    <div className="space-y-3 font-mono text-xs text-slate-200">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-slate-400">
        <div className="flex items-center space-x-1.5">
          <Settings className="h-3.5 w-3.5 text-indigo-400" />
          <span className="font-bold text-slate-200">Risk Threshold Settings</span>
        </div>
        <button
          onClick={handleReset}
          className="text-[10px] text-slate-400 hover:text-slate-200 transition-colors"
        >
          Reset Defaults
        </button>
      </div>

      <form onSubmit={handleSave} className="space-y-2">
        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="text-[10px] text-slate-500 block mb-0.5">MAX DRAWDOWN THRESHOLD (%)</label>
            <input
              type="number"
              step="0.5"
              value={prefs?.drawdown_threshold_pct ?? 5.0}
              onChange={(e) => setPrefs({ ...prefs, drawdown_threshold_pct: Number(e.target.value) })}
              className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1 text-slate-200 text-xs"
            />
          </div>
          <div>
            <label className="text-[10px] text-slate-500 block mb-0.5">COMPANY CONCENTRATION (%)</label>
            <input
              type="number"
              step="1"
              value={prefs?.company_concentration_threshold_pct ?? 25.0}
              onChange={(e) => setPrefs({ ...prefs, company_concentration_threshold_pct: Number(e.target.value) })}
              className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1 text-slate-200 text-xs"
            />
          </div>
          <div>
            <label className="text-[10px] text-slate-500 block mb-0.5">SECTOR CONCENTRATION (%)</label>
            <input
              type="number"
              step="1"
              value={prefs?.sector_concentration_threshold_pct ?? 40.0}
              onChange={(e) => setPrefs({ ...prefs, sector_concentration_threshold_pct: Number(e.target.value) })}
              className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1 text-slate-200 text-xs"
            />
          </div>
          <div>
            <label className="text-[10px] text-slate-500 block mb-0.5">VaR THRESHOLD (%)</label>
            <input
              type="number"
              step="0.5"
              value={prefs?.var_threshold_pct ?? 5.0}
              onChange={(e) => setPrefs({ ...prefs, var_threshold_pct: Number(e.target.value) })}
              className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1 text-slate-200 text-xs"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={saving}
          className="w-full bg-indigo-950 hover:bg-indigo-900 border border-indigo-800 text-indigo-300 font-bold py-1.5 rounded transition-colors mt-2"
        >
          {saving ? 'Saving...' : 'Save Risk Thresholds'}
        </button>
      </form>
    </div>
  );
};

export const PortfolioRiskHistoryPanel: React.FC<PanelProps> = () => {
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await api.getRiskHistory();
        setHistory(res.snapshots || []);
      } catch (err) {
        console.error('Failed to load risk history:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  if (loading) return <div className="text-slate-500 animate-pulse p-4 text-center">Loading Risk Timeline...</div>;

  return (
    <div className="space-y-3 font-mono text-xs text-slate-200">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-slate-400">
        <div className="flex items-center space-x-1.5">
          <History className="h-3.5 w-3.5 text-cyan-400" />
          <span className="font-bold text-slate-200">Visual Risk Timeline & History</span>
        </div>
      </div>

      {history.length === 0 ? (
        <div className="p-4 text-center text-slate-500 bg-slate-950 border border-slate-800 rounded">
          No historical risk snapshots recorded yet.
        </div>
      ) : (
        <div className="space-y-1.5">
          {history.map((s) => (
            <div key={s.id} className="p-2 bg-slate-950 border border-slate-800 rounded flex justify-between items-center text-[10px]">
              <div>
                <span className="text-slate-400 font-bold block">{new Date(s.timestamp).toLocaleString()}</span>
                <span className="text-slate-500">Value: ₹{s.portfolio_value.toLocaleString()}</span>
              </div>
              <div className="text-right">
                <span className="text-indigo-400 font-bold block">VaR 95%: {s.var_95_pct ?? 'N/A'}%</span>
                <span className="text-red-400">DD: {s.drawdown_pct}%</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
