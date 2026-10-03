import React, { useEffect, useState } from 'react';
import { api } from '../../../lib/api';
import { PanelProps } from '../../../types/panel';
import { Globe, BarChart2, PieChart, Activity, AlertTriangle, RefreshCw } from 'lucide-react';

export const MarketIntelligenceCommandCenterPanel: React.FC<PanelProps> = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchOverview = async () => {
    setLoading(true);
    try {
      const res = await api.getMarketIntelligenceOverview();
      setData(res);
    } catch (err) {
      console.error('Failed to load market overview:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOverview();
  }, []);

  if (loading) return <div className="text-slate-500 animate-pulse p-4 text-center font-mono text-xs">Loading Market Intelligence Command Center...</div>;

  const breadth = data?.market_breadth || {};

  return (
    <div className="space-y-3 font-mono text-xs text-slate-200">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-slate-400">
        <div className="flex items-center space-x-1.5">
          <Globe className="h-3.5 w-3.5 text-indigo-400" />
          <span className="font-bold text-slate-100">Market Intelligence Command Center</span>
        </div>
        <button onClick={fetchOverview} className="p-1 hover:bg-slate-800 text-slate-400 rounded">
          <RefreshCw className="h-3 w-3" />
        </button>
      </div>

      {/* Indices Bar */}
      <div className="grid grid-cols-2 gap-2">
        {(data?.indices || []).map((idx: any) => (
          <div key={idx.symbol} className="bg-slate-950 p-2 rounded border border-slate-800 flex justify-between items-center">
            <div>
              <span className="font-bold text-slate-200 block text-[11px]">{idx.name}</span>
              <span className="text-slate-400 text-[10px]">₹{idx.last_price.toLocaleString()}</span>
            </div>
            <span className={`font-bold ${idx.change_percent >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
              +{idx.change_percent}%
            </span>
          </div>
        ))}
      </div>

      {/* Market Breadth */}
      <div className="p-2.5 bg-slate-950 border border-slate-800 rounded space-y-1.5">
        <span className="text-[10px] text-slate-400 font-bold block">MARKET BREADTH (NSE/BSE)</span>
        <div className="grid grid-cols-3 gap-2 text-center text-[10px]">
          <div>
            <span className="text-slate-500 block">ADVANCES</span>
            <span className="font-bold text-emerald-400">{breadth.advances ?? 0}</span>
          </div>
          <div>
            <span className="text-slate-500 block">DECLINES</span>
            <span className="font-bold text-red-400">{breadth.declines ?? 0}</span>
          </div>
          <div>
            <span className="text-slate-500 block">A/D RATIO</span>
            <span className="font-bold text-indigo-400">{breadth.advance_decline_ratio ?? 1.0}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export const MarketBreadthPanel: React.FC<PanelProps> = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchBreadth = async () => {
      try {
        const res = await api.getMarketBreadth();
        setData(res.market_breadth || {});
      } catch (err) {
        console.error('Failed to load market breadth:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchBreadth();
  }, []);

  if (loading) return <div className="text-slate-500 animate-pulse p-4 text-center font-mono text-xs">Loading Market Breadth...</div>;

  return (
    <div className="space-y-3 font-mono text-xs text-slate-200">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-slate-400">
        <div className="flex items-center space-x-1.5">
          <BarChart2 className="h-3.5 w-3.5 text-cyan-400" />
          <span className="font-bold text-slate-200">Market Breadth Meter</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px]">
        <div className="p-2 bg-slate-950 border border-slate-800 rounded">
          <span className="text-slate-500 block">ADVANCING VOLUME</span>
          <span className="font-bold text-emerald-400 text-xs">{data?.advancing_volume?.toLocaleString() ?? 0}</span>
        </div>
        <div className="p-2 bg-slate-950 border border-slate-800 rounded">
          <span className="text-slate-500 block">DECLINING VOLUME</span>
          <span className="font-bold text-red-400 text-xs">{data?.declining_volume?.toLocaleString() ?? 0}</span>
        </div>
      </div>
    </div>
  );
};

export const SectorIntelligencePanel: React.FC<PanelProps> = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSectors = async () => {
      try {
        const res = await api.getSectorIntelligence();
        setData(res.sector_performance || []);
      } catch (err) {
        console.error('Failed to load sector intelligence:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchSectors();
  }, []);

  if (loading) return <div className="text-slate-500 animate-pulse p-4 text-center font-mono text-xs">Loading Sector Analytics...</div>;

  return (
    <div className="space-y-3 font-mono text-xs text-slate-200">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-slate-400">
        <div className="flex items-center space-x-1.5">
          <PieChart className="h-3.5 w-3.5 text-indigo-400" />
          <span className="font-bold text-slate-200">Sector Performance Matrix</span>
        </div>
      </div>

      <div className="space-y-1">
        {(data || []).map((sec: any) => (
          <div key={sec.sector} className="flex justify-between items-center p-1.5 bg-slate-950 border border-slate-800 rounded text-[10px]">
            <span className="font-bold text-slate-200">{sec.sector}</span>
            <span className={`font-bold ${sec.return_1d_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
              {sec.return_1d_pct >= 0 ? '+' : ''}{sec.return_1d_pct}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export const MarketRegimePanel: React.FC<PanelProps> = () => {
  const [regime, setRegime] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRegime = async () => {
      try {
        const res = await api.getMarketRegime();
        setRegime(res);
      } catch (err) {
        console.error('Failed to load market regime:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchRegime();
  }, []);

  if (loading) return <div className="text-slate-500 animate-pulse p-4 text-center font-mono text-xs">Loading Market Regime...</div>;

  return (
    <div className="space-y-3 font-mono text-xs text-slate-200">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-slate-400">
        <div className="flex items-center space-x-1.5">
          <Activity className="h-3.5 w-3.5 text-amber-400" />
          <span className="font-bold text-slate-200">Market Regime Classification</span>
        </div>
      </div>

      <div className="p-3 bg-slate-950 border border-slate-800 rounded text-center space-y-1">
        <span className="text-[10px] text-slate-500 block">CURRENT REGIME</span>
        <span className="text-sm font-bold text-indigo-400 block">{regime?.regime_classification || 'TRENDING_UP'}</span>
        <span className="text-[9px] text-slate-500 italic block">{regime?.disclaimer}</span>
      </div>
    </div>
  );
};

export const MarketAnomaliesPanel: React.FC<PanelProps> = () => {
  const [anomalies, setAnomalies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnomalies = async () => {
      try {
        const res = await api.getMarketAnomalies();
        setAnomalies(res);
      } catch (err) {
        console.error('Failed to load anomalies:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnomalies();
  }, []);

  if (loading) return <div className="text-slate-500 animate-pulse p-4 text-center font-mono text-xs">Loading Market Anomalies...</div>;

  return (
    <div className="space-y-3 font-mono text-xs text-slate-200">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-slate-400">
        <div className="flex items-center space-x-1.5">
          <AlertTriangle className="h-3.5 w-3.5 text-amber-400" />
          <span className="font-bold text-slate-200">Market Anomaly Radar</span>
        </div>
      </div>

      <div className="space-y-1.5">
        {anomalies.map((a) => (
          <div key={a.id} className="p-2 bg-slate-950 border border-slate-800 rounded space-y-0.5 text-[10px]">
            <div className="flex justify-between items-center font-bold">
              <span className="text-amber-400">{a.symbol} ({a.sector})</span>
              <span className="text-slate-400">{a.anomaly_type}</span>
            </div>
            <p className="text-slate-300 text-[9px]">{a.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
