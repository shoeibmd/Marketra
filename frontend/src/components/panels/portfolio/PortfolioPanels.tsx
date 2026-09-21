import React, { useEffect, useState } from 'react';
import { api } from '../../../lib/api';
import { PortfolioSummary, Position } from '../../../types/market';
import { PanelProps } from '../../../types/panel';
import { Wallet, Briefcase, History, PlusCircle } from 'lucide-react';

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
