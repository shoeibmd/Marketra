import React, { useEffect, useState } from 'react';
import { api } from '../../../lib/api';
import { PanelProps } from '../../../types/panel';
import { FileText, Clock, Settings, RefreshCw, CheckCircle, AlertTriangle } from 'lucide-react';

export const PortfolioBriefingPanel: React.FC<PanelProps> = () => {
  const [briefing, setBriefing] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  const fetchLatestBriefing = async () => {
    setLoading(true);
    try {
      const list = await api.getBriefings();
      if (list.length > 0) {
        const detail = await api.getBriefingDetail(list[0].id);
        setBriefing(detail);
      }
    } catch (err) {
      console.error('Failed to load briefing:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLatestBriefing();
  }, []);

  const handleGenerate = async (type = 'DAILY') => {
    setGenerating(true);
    try {
      await api.generateBriefingOnDemand(type);
      await fetchLatestBriefing();
    } catch (err) {
      console.error('Failed to generate briefing:', err);
    } finally {
      setGenerating(false);
    }
  };

  if (loading) return <div className="text-slate-500 animate-pulse p-4 text-center font-mono text-xs">Loading Latest Portfolio Briefing...</div>;

  return (
    <div className="space-y-3 font-mono text-xs text-slate-200">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-slate-400">
        <div className="flex items-center space-x-1.5">
          <FileText className="h-3.5 w-3.5 text-indigo-400" />
          <span className="font-bold text-slate-100">{briefing?.summary_title || 'Portfolio Research Briefing'}</span>
        </div>
        <div className="flex items-center space-x-1.5">
          <button
            onClick={() => handleGenerate('DAILY')}
            disabled={generating}
            className="bg-indigo-950 hover:bg-indigo-900 border border-indigo-800 text-indigo-300 px-2 py-0.5 rounded text-[10px] font-bold flex items-center space-x-1 transition-colors"
          >
            <RefreshCw className={`h-2.5 w-2.5 ${generating ? 'animate-spin' : ''}`} />
            <span>Generate Briefing</span>
          </button>
        </div>
      </div>

      {!briefing ? (
        <div className="p-4 text-center text-slate-500 bg-slate-950 border border-slate-800 rounded">
          No briefings generated yet. Click 'Generate Briefing' to create your first portfolio briefing.
        </div>
      ) : (
        <div className="space-y-2">
          {/* Executive Summary */}
          <div className="p-2.5 bg-slate-950 border border-slate-800 rounded space-y-1">
            <span className="text-[10px] text-indigo-400 font-bold block">PORTFOLIO SUMMARY</span>
            <div className="grid grid-cols-2 gap-2 text-[10px]">
              <div>TOTAL EQUITY: ₹{briefing.content?.portfolio_summary?.total_equity?.toLocaleString()}</div>
              <div>TOTAL RETURN: {briefing.content?.portfolio_summary?.total_return_pct}%</div>
            </div>
          </div>

          {/* What Changed */}
          {briefing.content?.what_changed?.length > 0 && (
            <div className="p-2.5 bg-slate-950 border border-slate-800 rounded space-y-1">
              <span className="text-[10px] text-amber-400 font-bold block">WHAT CHANGED</span>
              {briefing.content.what_changed.map((c: any, idx: number) => (
                <div key={idx} className="text-[10px] text-slate-300 flex items-start space-x-1">
                  <AlertTriangle className="h-3 w-3 text-amber-400 shrink-0 mt-0.5" />
                  <span>{c.description}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export const PortfolioChangeTimelinePanel: React.FC<PanelProps> = () => {
  const [changes, setChanges] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchChanges = async () => {
      try {
        const res = await api.getPortfolioChanges();
        setChanges(res);
      } catch (err) {
        console.error('Failed to load portfolio changes:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchChanges();
  }, []);

  if (loading) return <div className="text-slate-500 animate-pulse p-4 text-center font-mono text-xs">Loading Real-time Change Timeline...</div>;

  return (
    <div className="space-y-3 font-mono text-xs text-slate-200">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-slate-400">
        <div className="flex items-center space-x-1.5">
          <Clock className="h-3.5 w-3.5 text-cyan-400" />
          <span className="font-bold text-slate-200">Real-time Portfolio Change Timeline</span>
        </div>
      </div>

      {changes.length === 0 ? (
        <div className="p-4 text-center text-slate-500 bg-slate-950 border border-slate-800 rounded">
          No significant portfolio changes detected recently.
        </div>
      ) : (
        <div className="space-y-1.5">
          {changes.map((c) => (
            <div key={c.id} className="p-2 bg-slate-950 border border-slate-800 rounded flex justify-between items-center text-[10px]">
              <div>
                <span className="font-bold text-slate-200 block">{c.description}</span>
                <span className="text-slate-500">{new Date(c.detected_at).toLocaleString()}</span>
              </div>
              <span className="text-[9px] bg-slate-900 text-amber-400 px-1.5 py-0.5 rounded border border-slate-800">
                {c.significance}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export const PortfolioBriefingSettingsPanel: React.FC<PanelProps> = () => {
  const [prefs, setPrefs] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPrefs = async () => {
      try {
        const res = await api.getBriefingPreferences();
        setPrefs(res);
      } catch (err) {
        console.error('Failed to load briefing preferences:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchPrefs();
  }, []);

  const handleToggle = async (key: string) => {
    const updated = { ...prefs, [key]: !prefs[key] };
    setPrefs(updated);
    try {
      await api.updateBriefingPreferences(updated);
    } catch (err) {
      console.error('Failed to update preference:', err);
    }
  };

  if (loading) return <div className="text-slate-500 animate-pulse p-4 text-center">Loading Briefing Settings...</div>;

  return (
    <div className="space-y-3 font-mono text-xs text-slate-200">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-slate-400">
        <div className="flex items-center space-x-1.5">
          <Settings className="h-3.5 w-3.5 text-indigo-400" />
          <span className="font-bold text-slate-200">Briefing Schedule & Preferences</span>
        </div>
      </div>

      <div className="space-y-2 text-[10px]">
        <label className="flex items-center justify-between p-2 bg-slate-950 border border-slate-800 rounded cursor-pointer">
          <span>DAILY BRIEFING</span>
          <input
            type="checkbox"
            checked={prefs?.daily_briefing_enabled ?? true}
            onChange={() => handleToggle('daily_briefing_enabled')}
          />
        </label>
        <label className="flex items-center justify-between p-2 bg-slate-950 border border-slate-800 rounded cursor-pointer">
          <span>WEEKLY BRIEFING</span>
          <input
            type="checkbox"
            checked={prefs?.weekly_briefing_enabled ?? true}
            onChange={() => handleToggle('weekly_briefing_enabled')}
          />
        </label>
        <label className="flex items-center justify-between p-2 bg-slate-950 border border-slate-800 rounded cursor-pointer">
          <span>PRE-MARKET BRIEFING</span>
          <input
            type="checkbox"
            checked={prefs?.pre_market_briefing_enabled ?? true}
            onChange={() => handleToggle('pre_market_briefing_enabled')}
          />
        </label>
      </div>
    </div>
  );
};
