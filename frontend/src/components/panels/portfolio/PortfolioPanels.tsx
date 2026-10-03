import React, { useEffect, useState } from 'react';
import { api } from '../../../lib/api';
import { PortfolioSummary, Position } from '../../../types/market';
import { PanelProps } from '../../../types/panel';
import { Wallet, Briefcase, History, PlusCircle, ShieldAlert, BarChart3, PieChart, TrendingUp } from 'lucide-react';

export interface PortfolioAnalyticsData {
  account_id: string;
  currency: string;
  data_status: string;
  summary: {
    total_equity: number;
    cash_balance: number;
    positions_value: number;
    total_pnl: number;
    total_return_pct: number;
    realized_pnl: number;
    unrealized_pnl: number;
  };
  risk_analytics: {
    max_drawdown_pct: number;
    sharpe_ratio: number | null;
    sortino_ratio: number | null;
    annualized_volatility_pct: number | null;
    max_position_concentration_pct: number;
    sector_exposure_pct: Record<string, number>;
  };
  performance_metrics: {
    total_trades: number;
    win_rate_pct: number;
    profit_factor: number;
    winning_trades: number;
    losing_trades: number;
  };
  benchmark_comparison: {
    benchmark_symbol: string;
    portfolio_return_pct: number;
    benchmark_return_pct: number;
    alpha_pct: number;
    beta: number | null;
  };
  positions: Array<{
    instrument_id: string;
    symbol: string;
    quantity: number;
    avg_price: number;
    current_price: number;
    market_value: number;
    unrealized_pnl: number;
  }>;
  disclaimer: string;
}

export const PortfolioAnalyticsPanel: React.FC<PanelProps> = () => {
  const [data, setData] = useState<PortfolioAnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const res = await api.getPortfolioAnalytics();
        setData(res);
      } catch (err) {
        console.error('Failed to load portfolio analytics:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (loading) return <div className="text-slate-500 animate-pulse p-4 text-center font-mono text-xs">Loading Portfolio Intelligence & Risk Analytics...</div>;

  if (!data) return <div className="text-slate-500 p-4 text-center font-mono text-xs">Portfolio Analytics Unavailable</div>;

  const { summary, risk_analytics, performance_metrics, benchmark_comparison } = data;

  return (
    <div className="space-y-3 font-mono text-xs text-slate-200">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-slate-400">
        <div className="flex items-center space-x-1.5">
          <BarChart3 className="h-3.5 w-3.5 text-indigo-400" />
          <span className="font-bold text-slate-200">Portfolio Intelligence & Risk Analytics</span>
        </div>
        <span className="text-[10px] bg-slate-900 text-indigo-400 px-1.5 py-0.5 rounded border border-indigo-950 font-semibold">
          {data.data_status}
        </span>
      </div>

      {/* Summary KPI Grid */}
      <div className="grid grid-cols-4 gap-2">
        <div className="bg-slate-950 p-2 rounded border border-slate-800">
          <span className="text-[10px] text-slate-500 block">TOTAL EQUITY</span>
          <span className="text-sm font-bold text-slate-100">₹{summary.total_equity.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
        </div>
        <div className="bg-slate-950 p-2 rounded border border-slate-800">
          <span className="text-[10px] text-slate-500 block">TOTAL RETURN</span>
          <span className={`text-sm font-bold ${summary.total_return_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            {summary.total_return_pct >= 0 ? '+' : ''}{summary.total_return_pct}%
          </span>
        </div>
        <div className="bg-slate-950 p-2 rounded border border-slate-800">
          <span className="text-[10px] text-slate-500 block">REALIZED P&L</span>
          <span className={`text-sm font-bold ${summary.realized_pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            ₹{summary.realized_pnl.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </span>
        </div>
        <div className="bg-slate-950 p-2 rounded border border-slate-800">
          <span className="text-[10px] text-slate-500 block">UNREALIZED P&L</span>
          <span className={`text-sm font-bold ${summary.unrealized_pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            ₹{summary.unrealized_pnl.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </span>
        </div>
      </div>

      {/* Risk Metrics Section */}
      <div className="bg-slate-950 p-2.5 rounded border border-slate-800 space-y-2">
        <div className="flex items-center space-x-1.5 text-slate-400 text-[11px] font-bold border-b border-slate-800/80 pb-1">
          <ShieldAlert className="h-3 w-3 text-amber-400" />
          <span>Risk & Drawdown Analysis</span>
        </div>
        <div className="grid grid-cols-4 gap-2 text-center text-[10px]">
          <div>
            <span className="text-slate-500 block">MAX DRAWDOWN</span>
            <span className="font-bold text-red-400">{risk_analytics.max_drawdown_pct}%</span>
          </div>
          <div>
            <span className="text-slate-500 block">SHARPE RATIO</span>
            <span className="font-bold text-slate-200">{risk_analytics.sharpe_ratio ?? 'N/A'}</span>
          </div>
          <div>
            <span className="text-slate-500 block">SORTINO RATIO</span>
            <span className="font-bold text-slate-200">{risk_analytics.sortino_ratio ?? 'N/A'}</span>
          </div>
          <div>
            <span className="text-slate-500 block">ANN. VOLATILITY</span>
            <span className="font-bold text-slate-200">{risk_analytics.annualized_volatility_pct ? `${risk_analytics.annualized_volatility_pct}%` : 'N/A'}</span>
          </div>
        </div>
      </div>

      {/* Performance & Benchmark Section */}
      <div className="grid grid-cols-2 gap-2">
        <div className="bg-slate-950 p-2.5 rounded border border-slate-800 space-y-1.5">
          <div className="flex items-center space-x-1.5 text-slate-400 text-[11px] font-bold border-b border-slate-800/80 pb-1">
            <PieChart className="h-3 w-3 text-cyan-400" />
            <span>Execution Performance</span>
          </div>
          <div className="flex justify-between items-center text-[10px]">
            <span className="text-slate-500">WIN RATE:</span>
            <span className="font-bold text-emerald-400">{performance_metrics.win_rate_pct}%</span>
          </div>
          <div className="flex justify-between items-center text-[10px]">
            <span className="text-slate-500">PROFIT FACTOR:</span>
            <span className="font-bold text-slate-200">{performance_metrics.profit_factor}</span>
          </div>
          <div className="flex justify-between items-center text-[10px]">
            <span className="text-slate-500">TOTAL TRADES:</span>
            <span className="font-bold text-slate-200">{performance_metrics.total_trades}</span>
          </div>
        </div>

        <div className="bg-slate-950 p-2.5 rounded border border-slate-800 space-y-1.5">
          <div className="flex items-center space-x-1.5 text-slate-400 text-[11px] font-bold border-b border-slate-800/80 pb-1">
            <TrendingUp className="h-3 w-3 text-emerald-400" />
            <span>Benchmark vs {benchmark_comparison.benchmark_symbol}</span>
          </div>
          <div className="flex justify-between items-center text-[10px]">
            <span className="text-slate-500">BENCHMARK RETURN:</span>
            <span className="font-bold text-slate-200">{benchmark_comparison.benchmark_return_pct}%</span>
          </div>
          <div className="flex justify-between items-center text-[10px]">
            <span className="text-slate-500">PORTFOLIO ALPHA:</span>
            <span className={`font-bold ${benchmark_comparison.alpha_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
              {benchmark_comparison.alpha_pct >= 0 ? '+' : ''}{benchmark_comparison.alpha_pct}%
            </span>
          </div>
          <div className="flex justify-between items-center text-[10px]">
            <span className="text-slate-500">PORTFOLIO BETA:</span>
            <span className="font-bold text-slate-200">{benchmark_comparison.beta ?? 'N/A'}</span>
          </div>
        </div>
      </div>

      <p className="text-[9px] text-slate-600 italic mt-2">{data.disclaimer}</p>
    </div>
  );
};

export const PortfolioSummaryPanel: React.FC<PanelProps> = () => {
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getPortfolioSummary().then((res) => {
      setSummary(res);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="text-slate-500 animate-pulse p-4 text-center">Loading Portfolio Summary...</div>;

  return (
    <div className="space-y-3 font-mono text-xs">
      <div className="flex items-center space-x-1.5 border-b border-slate-800 pb-1.5 text-slate-400">
        <Wallet className="h-3.5 w-3.5 text-emerald-400" />
        <span className="font-bold text-slate-200">{summary?.portfolio_name || 'Indian Market Portfolio'}</span>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
          <span className="text-[10px] text-slate-500 block">TOTAL VALUE (INR)</span>
          <span className="text-sm font-bold text-slate-100">₹{summary?.total_market_value.toFixed(2)}</span>
        </div>
        <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
          <span className="text-[10px] text-slate-500 block">CASH BALANCE</span>
          <span className="text-sm font-bold text-slate-100">₹{summary?.cash_balance.toFixed(2)}</span>
        </div>
      </div>

      <div className="bg-slate-950 p-2.5 rounded border border-slate-800 flex justify-between items-center">
        <span className="text-slate-500">UNREALIZED P&L:</span>
        <span className={`font-bold ${summary && summary.total_pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
          ₹{summary?.total_pnl.toFixed(2)} ({summary?.total_pnl_percent}%)
        </span>
      </div>
    </div>
  );
};

export const HoldingsPanel: React.FC<PanelProps> = () => {
  const [positions, setPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getPortfolio().then((res) => {
      setPositions(res.positions);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="text-slate-500 animate-pulse p-4 text-center">Loading Holdings...</div>;

  return (
    <div className="space-y-2 font-mono text-xs">
      <div className="flex items-center space-x-1.5 border-b border-slate-800 pb-1.5 text-slate-400">
        <Briefcase className="h-3.5 w-3.5 text-blue-400" />
        <span className="font-bold text-slate-200">NSE/BSE Asset Holdings</span>
      </div>

      <div className="grid grid-cols-4 text-[10px] text-slate-500 border-b border-slate-800 pb-1">
        <span>ASSET</span>
        <span>QTY</span>
        <span>MKT VAL</span>
        <span className="text-right">P&L</span>
      </div>

      {positions.map((p) => (
        <div key={p.symbol} className="grid grid-cols-4 py-1 border-b border-slate-800/40 items-center">
          <span className="font-bold text-slate-200">{p.symbol}</span>
          <span className="text-slate-400">{p.quantity}</span>
          <span className="text-slate-100">₹{p.market_value.toFixed(2)}</span>
          <span className={`text-right font-bold ${p.unrealized_pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            ₹{p.unrealized_pnl.toFixed(2)}
          </span>
        </div>
      ))}
    </div>
  );
};

export const TransactionHistoryPanel: React.FC<PanelProps> = () => {
  return (
    <div className="space-y-2 font-mono text-xs">
      <div className="flex items-center space-x-1.5 border-b border-slate-800 pb-1.5 text-slate-400">
        <History className="h-3.5 w-3.5 text-amber-400" />
        <span className="font-bold text-slate-200">Recent Transactions</span>
      </div>

      <div className="space-y-1.5">
        <div className="p-2 bg-slate-950 border border-slate-800 rounded flex justify-between items-center">
          <div>
            <span className="font-bold text-emerald-400 mr-2">BUY</span>
            <span className="text-slate-200">RELIANCE x 10</span>
          </div>
          <span className="text-slate-400">₹2,850.00 / share</span>
        </div>
        <div className="p-2 bg-slate-950 border border-slate-800 rounded flex justify-between items-center">
          <div>
            <span className="font-bold text-emerald-400 mr-2">BUY</span>
            <span className="text-slate-200">TCS x 5</span>
          </div>
          <span className="text-slate-400">₹3,920.00 / share</span>
        </div>
      </div>
    </div>
  );
};

export const AddTransactionPanel: React.FC<PanelProps> = () => {
  const [symbol, setSymbol] = useState('RELIANCE');
  const [qty, setQty] = useState(1);
  const [price, setPrice] = useState(2850.0);

  return (
    <div className="space-y-3 font-mono text-xs">
      <div className="flex items-center space-x-1.5 border-b border-slate-800 pb-1.5 text-slate-400">
        <PlusCircle className="h-3.5 w-3.5 text-emerald-400" />
        <span className="font-bold text-slate-200">Record New Trade</span>
      </div>

      <form onSubmit={(e) => e.preventDefault()} className="space-y-2">
        <div>
          <label className="text-[10px] text-slate-500 block mb-0.5">SYMBOL</label>
          <input
            type="text"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1 text-slate-200 focus:outline-none focus:border-emerald-500"
          />
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="text-[10px] text-slate-500 block mb-0.5">QUANTITY</label>
            <input
              type="number"
              value={qty}
              onChange={(e) => setQty(Number(e.target.value))}
              className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1 text-slate-200 focus:outline-none focus:border-emerald-500"
            />
          </div>
          <div>
            <label className="text-[10px] text-slate-500 block mb-0.5">EXEC PRICE (₹)</label>
            <input
              type="number"
              value={price}
              onChange={(e) => setPrice(Number(e.target.value))}
              className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1 text-slate-200 focus:outline-none focus:border-emerald-500"
            />
          </div>
        </div>
        <button
          type="submit"
          className="w-full bg-emerald-950 hover:bg-emerald-900 border border-emerald-800 text-emerald-400 py-1.5 rounded font-bold transition-colors mt-2"
        >
          Execute Order Record
        </button>
      </form>
    </div>
  );
};
