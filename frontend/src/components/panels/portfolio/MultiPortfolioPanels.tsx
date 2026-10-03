import React, { useEffect, useState } from 'react';
import { api } from '../../../lib/api';
import { PanelProps } from '../../../types/panel';
import { Briefcase, Layers, Copy, PieChart, Plus, RefreshCw } from 'lucide-react';

export const MultiPortfolioOverviewPanel: React.FC<PanelProps> = () => {
  const [portfolios, setPortfolios] = useState<any[]>([]);
  const [consolidated, setConsolidated] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [newAccountName, setNewAccountName] = useState('');
  const [creating, setCreating] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const ports = await api.getUserPortfolios();
      setPortfolios(ports);
      const cons = await api.getConsolidatedPortfolio();
      setConsolidated(cons);
    } catch (err) {
      console.error('Failed to load multi-portfolio data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreatePortfolio = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newAccountName.trim()) return;
    setCreating(true);
    try {
      await api.createPortfolioAccount(newAccountName.trim(), 1000000.0, 'PAPER');
      setNewAccountName('');
      await fetchData();
    } catch (err) {
      console.error('Failed to create portfolio:', err);
    } finally {
      setCreating(false);
    }
  };

  if (loading) return <div className="text-slate-500 animate-pulse p-4 text-center font-mono text-xs">Loading Multi-Portfolio Dashboard...</div>;

  const summary = consolidated?.consolidated_summary || {};

  return (
    <div className="space-y-3 font-mono text-xs text-slate-200">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-slate-400">
        <div className="flex items-center space-x-1.5">
          <Briefcase className="h-3.5 w-3.5 text-emerald-400" />
          <span className="font-bold text-slate-100 font-bold">Consolidated Multi-Portfolio Overview</span>
        </div>
        <button onClick={fetchData} className="p-1 hover:bg-slate-800 text-slate-400 rounded">
          <RefreshCw className="h-3 w-3" />
        </button>
      </div>

      {/* KPI Summary */}
      <div className="grid grid-cols-3 gap-2">
        <div className="bg-slate-950 p-2 rounded border border-slate-800">
          <span className="text-[10px] text-slate-500 block">TOTAL COMBINED EQUITY</span>
          <span className="text-sm font-bold text-slate-100">₹{summary.total_equity?.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
        </div>
        <div className="bg-slate-950 p-2 rounded border border-slate-800">
          <span className="text-[10px] text-slate-500 block">COMBINED CASH</span>
          <span className="text-sm font-bold text-slate-200">₹{summary.cash_balance?.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
        </div>
        <div className="bg-slate-950 p-2 rounded border border-slate-800">
          <span className="text-[10px] text-slate-500 block">COMBINED REALIZED P&L</span>
          <span className={`text-sm font-bold ${summary.realized_pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            ₹{summary.realized_pnl?.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </span>
        </div>
      </div>

      {/* Account List & Creator */}
      <div className="space-y-2">
        <span className="text-[10px] text-slate-400 font-bold block">ACTIVE USER PORTFOLIOS ({portfolios.length})</span>
        <div className="space-y-1">
          {portfolios.map((p) => (
            <div key={p.id} className="flex justify-between items-center p-2 bg-slate-950 border border-slate-800 rounded text-[10px]">
              <div>
                <span className="font-bold text-slate-200 block">{p.name}</span>
                <span className="text-slate-500">Type: {p.portfolio_type}</span>
              </div>
              <span className="text-slate-300 font-bold">₹{p.available_cash?.toLocaleString()} cash</span>
            </div>
          ))}
        </div>

        <form onSubmit={handleCreatePortfolio} className="flex space-x-2 pt-1">
          <input
            type="text"
            placeholder="New Portfolio Name..."
            value={newAccountName}
            onChange={(e) => setNewAccountName(e.target.value)}
            className="flex-1 bg-slate-950 border border-slate-800 rounded px-2 py-1 text-slate-200 text-xs"
          />
          <button
            type="submit"
            disabled={creating}
            className="bg-emerald-950 hover:bg-emerald-900 border border-emerald-800 text-emerald-400 px-3 py-1 rounded font-bold flex items-center space-x-1"
          >
            <Plus className="h-3 w-3" />
            <span>Create</span>
          </button>
        </form>
      </div>
    </div>
  );
};

export const PortfolioComparisonPanel: React.FC<PanelProps> = () => {
  const [comparisons, setComparisons] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchComparison = async () => {
      try {
        const res = await api.comparePortfolios();
        setComparisons(res);
      } catch (err) {
        console.error('Failed to load comparisons:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchComparison();
  }, []);

  if (loading) return <div className="text-slate-500 animate-pulse p-4 text-center font-mono text-xs">Loading Side-by-Side Comparison...</div>;

  return (
    <div className="space-y-3 font-mono text-xs text-slate-200">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-slate-400">
        <div className="flex items-center space-x-1.5">
          <Layers className="h-3.5 w-3.5 text-indigo-400" />
          <span className="font-bold text-slate-200">Side-by-Side Portfolio Comparison</span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-center text-[10px] border-collapse">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400">
              <th className="p-1 text-left">PORTFOLIO</th>
              <th className="p-1">EQUITY</th>
              <th className="p-1">RETURN</th>
              <th className="p-1">MAX DRAWDOWN</th>
              <th className="p-1">VaR 95%</th>
            </tr>
          </thead>
          <tbody>
            {comparisons.map((c) => (
              <tr key={c.account_id} className="border-b border-slate-800/40">
                <td className="p-1 font-bold text-left text-slate-200">{c.name}</td>
                <td className="p-1 text-slate-300">₹{c.total_equity?.toLocaleString()}</td>
                <td className={`p-1 font-bold ${c.total_return_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                  {c.total_return_pct}%
                </td>
                <td className="p-1 text-red-400">{c.max_drawdown_pct}%</td>
                <td className="p-1 text-amber-400">{c.historical_var_95_pct}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export const DuplicateExposurePanel: React.FC<PanelProps> = () => {
  const [duplicates, setDuplicates] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDuplicates = async () => {
      try {
        const res = await api.getDuplicateExposures();
        setDuplicates(res);
      } catch (err) {
        console.error('Failed to load duplicate exposures:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDuplicates();
  }, []);

  if (loading) return <div className="text-slate-500 animate-pulse p-4 text-center font-mono text-xs">Loading Duplicate Exposures...</div>;

  return (
    <div className="space-y-3 font-mono text-xs text-slate-200">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-slate-400">
        <div className="flex items-center space-x-1.5">
          <Copy className="h-3.5 w-3.5 text-amber-400" />
          <span className="font-bold text-slate-200">Duplicate Cross-Portfolio Exposures</span>
        </div>
      </div>

      {duplicates.length === 0 ? (
        <div className="p-4 text-center text-slate-500 bg-slate-950 border border-slate-800 rounded">
          No holdings currently overlap across multiple portfolios.
        </div>
      ) : (
        <div className="space-y-1.5">
          {duplicates.map((d) => (
            <div key={d.symbol} className="p-2 bg-slate-950 border border-slate-800 rounded space-y-1">
              <div className="flex justify-between items-center text-[11px] font-bold">
                <span className="text-slate-100">{d.symbol}</span>
                <span className="text-amber-400">Held in {d.portfolio_count} portfolios (Total: ₹{d.combined_market_value?.toLocaleString()})</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export const PortfolioAttributionPanel: React.FC<PanelProps> = () => {
  const [attr, setAttribution] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAttr = async () => {
      try {
        const res = await api.getPortfolioAttribution();
        setAttribution(res);
      } catch (err) {
        console.error('Failed to load attribution:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAttr();
  }, []);

  if (loading) return <div className="text-slate-500 animate-pulse p-4 text-center font-mono text-xs">Loading Performance Attribution...</div>;

  const list = attr?.attribution_by_portfolio || [];

  return (
    <div className="space-y-3 font-mono text-xs text-slate-200">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-slate-400">
        <div className="flex items-center space-x-1.5">
          <PieChart className="h-3.5 w-3.5 text-cyan-400" />
          <span className="font-bold text-slate-200">Portfolio Performance Attribution</span>
        </div>
      </div>

      <div className="space-y-1">
        {list.map((item: any) => (
          <div key={item.account_id} className="p-2 bg-slate-950 border border-slate-800 rounded flex justify-between items-center text-[10px]">
            <span className="font-bold text-slate-200">{item.account_name}</span>
            <span className={`font-bold ${item.total_pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
              ₹{item.total_pnl?.toLocaleString()}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
