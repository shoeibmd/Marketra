import React, { useEffect, useState } from 'react';
import { panelRegistry } from '../../../lib/panelRegistry';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const EventMarketContextPanel: React.FC = () => {
  const [eventIdInput, setEventIdInput] = useState('');
  const [contextData, setContextData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchContext = async (id: string) => {
    if (!id.trim()) return;
    const token = localStorage.getItem('auth_token');
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/events/${id.trim()}/market-context`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!res.ok) throw new Error('Event market context not found');
      const data = await res.json();
      setContextData(data);
    } catch (err: any) {
      setError(err.message || 'Error fetching event market context');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-full flex flex-col bg-slate-900 text-slate-100 p-4 border border-slate-800 rounded-lg font-sans overflow-y-auto">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <h3 className="text-xs font-bold uppercase tracking-wider text-blue-400">
          Historical Event Market Context
        </h3>
        <span className="text-[10px] text-slate-500 font-mono">Factual / Non-Causal</span>
      </div>

      <div className="mt-3 flex items-center space-x-2">
        <input
          type="text"
          placeholder="Enter Event ID..."
          value={eventIdInput}
          onChange={(e) => setEventIdInput(e.target.value)}
          className="flex-1 bg-slate-950 border border-slate-800 text-xs text-slate-200 px-3 py-1.5 rounded-md focus:outline-none focus:border-blue-500 font-mono"
        />
        <button
          onClick={() => fetchContext(eventIdInput)}
          className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-md transition-colors"
        >
          Analyze Context
        </button>
      </div>

      {loading && <div className="p-6 text-center text-xs text-slate-500">Loading market context...</div>}
      {error && <div className="mt-3 p-3 bg-red-950/40 border border-red-800/50 rounded-md text-xs text-red-400">{error}</div>}

      {contextData && (
        <div className="mt-4 space-y-3">
          <div className="bg-slate-950 p-3 rounded-md border border-slate-800">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-slate-200">{contextData.event_title}</span>
              <span className="text-blue-400 font-mono text-[11px]">{contextData.event_type}</span>
            </div>
            <div className="mt-1 flex items-center justify-between text-[10px] text-slate-400">
              <span>Event Date: {new Date(contextData.event_date).toLocaleString()}</span>
              <span className="text-amber-400 font-semibold">
                Session: {contextData.market_context.session_classification}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="bg-slate-950/80 p-2.5 rounded border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase">Baseline Price</span>
              <div className="text-sm font-bold text-slate-100 mt-0.5">
                {contextData.market_context.baseline_price != null ? `₹${contextData.market_context.baseline_price}` : 'N/A'}
              </div>
            </div>
            <div className="bg-slate-950/80 p-2.5 rounded border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase">Volume Change</span>
              <div className="text-sm font-bold text-slate-100 mt-0.5">
                {contextData.market_context.volume_change_pct != null ? `${contextData.market_context.volume_change_pct}%` : 'N/A'}
              </div>
            </div>
          </div>

          <div className="bg-slate-950 p-3 rounded-md border border-slate-800">
            <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">
              Historical Return Windows
            </h4>
            <div className="grid grid-cols-5 gap-1 text-center text-xs">
              <div className="bg-slate-900 p-2 rounded">
                <span className="text-[10px] text-slate-500">1D</span>
                <div className={`font-bold mt-1 ${contextData.market_context.return_1d_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                  {contextData.market_context.return_1d_pct ?? 'N/A'}%
                </div>
              </div>
              <div className="bg-slate-900 p-2 rounded">
                <span className="text-[10px] text-slate-500">3D</span>
                <div className={`font-bold mt-1 ${contextData.market_context.return_3d_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                  {contextData.market_context.return_3d_pct ?? 'N/A'}%
                </div>
              </div>
              <div className="bg-slate-900 p-2 rounded">
                <span className="text-[10px] text-slate-500">5D</span>
                <div className={`font-bold mt-1 ${contextData.market_context.return_5d_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                  {contextData.market_context.return_5d_pct ?? 'N/A'}%
                </div>
              </div>
              <div className="bg-slate-900 p-2 rounded">
                <span className="text-[10px] text-slate-500">10D</span>
                <div className={`font-bold mt-1 ${contextData.market_context.return_10d_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                  {contextData.market_context.return_10d_pct ?? 'N/A'}%
                </div>
              </div>
              <div className="bg-slate-900 p-2 rounded">
                <span className="text-[10px] text-slate-500">20D</span>
                <div className={`font-bold mt-1 ${contextData.market_context.return_20d_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                  {contextData.market_context.return_20d_pct ?? 'N/A'}%
                </div>
              </div>
            </div>
          </div>

          <div className="p-2.5 bg-slate-950/60 border border-slate-800 rounded text-[10px] text-slate-400 italic">
            {contextData.market_context.disclaimer}
          </div>
        </div>
      )}
    </div>
  );
};

export const CompanyHistoricalAnalyticsPanel: React.FC = () => {
  const [symbol, setSymbol] = useState('RELIANCE');
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const fetchCompanyAnalytics = async (sym: string) => {
    const token = localStorage.getItem('auth_token');
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/company/${sym}/event-analytics`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (res.ok) {
        const data = await res.json();
        setAnalytics(data);
      }
    } catch {
      // Ignore
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCompanyAnalytics(symbol);
  }, [symbol]);

  return (
    <div className="h-full flex flex-col bg-slate-900 text-slate-100 p-4 border border-slate-800 rounded-lg font-sans overflow-y-auto">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <h3 className="text-xs font-bold uppercase tracking-wider text-blue-400">
          Company Historical Event Analytics
        </h3>
        <select
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
          className="bg-slate-950 border border-slate-800 text-xs text-blue-400 font-bold px-2 py-1 rounded focus:outline-none"
        >
          <option value="RELIANCE">RELIANCE</option>
          <option value="TCS">TCS</option>
          <option value="INFY">INFY</option>
          <option value="HDFCBANK">HDFCBANK</option>
        </select>
      </div>

      {loading ? (
        <div className="p-8 text-center text-xs text-slate-500">Loading analytics...</div>
      ) : !analytics ? (
        <div className="p-8 text-center text-xs text-slate-500">No analytics data found</div>
      ) : (
        <div className="mt-3 space-y-3">
          <div className="flex items-center justify-between bg-slate-950 p-3 rounded border border-slate-800 text-xs">
            <div>
              <span className="font-bold text-slate-200">{analytics.company_name} ({analytics.symbol})</span>
              <div className="text-[10px] text-slate-400 mt-0.5">Total Historical Events: {analytics.total_events}</div>
            </div>
          </div>

          {/* 1D Aggregate Stats */}
          <div className="bg-slate-950 p-3 rounded border border-slate-800">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                1-Day Observed Aggregate Statistics
              </span>
              <span className="text-[10px] text-slate-400 font-mono">
                Sample Size: n = {analytics.aggregate_statistics_1d.sample_size}
              </span>
            </div>
            {analytics.aggregate_statistics_1d.insufficient_sample ? (
              <div className="p-2 bg-amber-950/40 border border-amber-800/40 rounded text-[11px] text-amber-400">
                {analytics.aggregate_statistics_1d.message}
              </div>
            ) : (
              <div className="grid grid-cols-4 gap-2 text-center text-xs">
                <div className="bg-slate-900 p-2 rounded">
                  <span className="text-[10px] text-slate-500">Mean Return</span>
                  <div className="font-bold text-slate-200 mt-0.5">{analytics.aggregate_statistics_1d.mean_return_pct}%</div>
                </div>
                <div className="bg-slate-900 p-2 rounded">
                  <span className="text-[10px] text-slate-500">Median</span>
                  <div className="font-bold text-slate-200 mt-0.5">{analytics.aggregate_statistics_1d.median_return_pct}%</div>
                </div>
                <div className="bg-slate-900 p-2 rounded">
                  <span className="text-[10px] text-slate-500">Positive Obs</span>
                  <div className="font-bold text-emerald-400 mt-0.5">{analytics.aggregate_statistics_1d.positive_observations}</div>
                </div>
                <div className="bg-slate-900 p-2 rounded">
                  <span className="text-[10px] text-slate-500">Negative Obs</span>
                  <div className="font-bold text-red-400 mt-0.5">{analytics.aggregate_statistics_1d.negative_observations}</div>
                </div>
              </div>
            )}
          </div>

          <div className="p-2.5 bg-slate-950/60 border border-slate-800 rounded text-[10px] text-slate-400 italic">
            {analytics.disclaimer}
          </div>
        </div>
      )}
    </div>
  );
};

export const HistoricalEventAnalyticsPanel: React.FC = () => {
  const [sym1, setSym1] = useState('TCS');
  const [sym2, setSym2] = useState('INFY');
  const [compareData, setCompareData] = useState<any>(null);

  const fetchCompare = async () => {
    const token = localStorage.getItem('auth_token');
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/analytics/compare?symbol1=${sym1}&symbol2=${sym2}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (res.ok) {
        const data = await res.json();
        setCompareData(data);
      }
    } catch {
      // Ignore
    }
  };

  useEffect(() => {
    fetchCompare();
  }, [sym1, sym2]);

  return (
    <div className="h-full flex flex-col bg-slate-900 text-slate-100 p-4 border border-slate-800 rounded-lg font-sans overflow-y-auto">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <h3 className="text-xs font-bold uppercase tracking-wider text-blue-400">
          Historical Event Comparison (Factual)
        </h3>
        <div className="flex items-center space-x-2 text-xs font-bold">
          <input
            type="text"
            value={sym1}
            onChange={(e) => setSym1(e.target.value.toUpperCase())}
            className="w-16 bg-slate-950 border border-slate-800 text-center px-1.5 py-1 rounded text-blue-400 uppercase font-mono"
          />
          <span className="text-slate-500">vs</span>
          <input
            type="text"
            value={sym2}
            onChange={(e) => setSym2(e.target.value.toUpperCase())}
            className="w-16 bg-slate-950 border border-slate-800 text-center px-1.5 py-1 rounded text-emerald-400 uppercase font-mono"
          />
        </div>
      </div>

      {!compareData ? (
        <div className="p-8 text-center text-xs text-slate-500">Loading comparison...</div>
      ) : (
        <div className="mt-3 space-y-3">
          <div className="grid grid-cols-2 gap-3 text-xs">
            {compareData.comparison.map((comp: any) => (
              <div key={comp.symbol} className="bg-slate-950 p-3 rounded border border-slate-800 space-y-2">
                <div className="font-bold text-slate-200 border-b border-slate-800 pb-1 flex justify-between">
                  <span>{comp.symbol}</span>
                  <span className="text-[10px] text-slate-400">Events: {comp.total_events}</span>
                </div>
                <div className="text-[11px] text-slate-300">
                  <div className="flex justify-between py-0.5">
                    <span className="text-slate-500">1D Mean:</span>
                    <span className="font-semibold">{comp.aggregate_statistics_1d.mean_return_pct ?? 'N/A'}%</span>
                  </div>
                  <div className="flex justify-between py-0.5">
                    <span className="text-slate-500">5D Mean:</span>
                    <span className="font-semibold">{comp.aggregate_statistics_5d.mean_return_pct ?? 'N/A'}%</span>
                  </div>
                  <div className="flex justify-between py-0.5">
                    <span className="text-slate-500">Sample Size:</span>
                    <span className="font-semibold font-mono">n = {comp.aggregate_statistics_1d.sample_size}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="p-2.5 bg-slate-950/60 border border-slate-800 rounded text-[10px] text-slate-400 italic">
            {compareData.disclaimer}
          </div>
        </div>
      )}
    </div>
  );
};

// Register in PanelRegistry
panelRegistry.register({
  type: 'EVENT_MARKET_CONTEXT',
  title: 'Historical Event Market Context',
  category: 'News',
  description: 'Factual price and volume observations around financial event timestamps',
  component: EventMarketContextPanel,
  defaultWidth: 6,
  defaultHeight: 4,
});

panelRegistry.register({
  type: 'COMPANY_HISTORICAL_ANALYTICS',
  title: 'Company Historical Analytics',
  category: 'News',
  description: 'Historical return window observations and aggregate statistics by company',
  component: CompanyHistoricalAnalyticsPanel,
  defaultWidth: 6,
  defaultHeight: 4,
});

panelRegistry.register({
  type: 'HISTORICAL_EVENT_ANALYTICS',
  title: 'Historical Event Comparison',
  category: 'News',
  description: 'Factual side-by-side event return comparison between companies',
  component: HistoricalEventAnalyticsPanel,
  defaultWidth: 6,
  defaultHeight: 4,
});
