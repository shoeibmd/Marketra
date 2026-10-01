import React, { useEffect, useState } from 'react';
import { panelRegistry } from '../../../lib/panelRegistry';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const PaperTradingPanel: React.FC = () => {
  const [account, setAccount] = useState<any>(null);
  const [orders, setOrders] = useState<any[]>([]);
  const [trades, setTrades] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Order Ticket State
  const [symbol, setSymbol] = useState('RELIANCE');
  const [side, setSide] = useState<'BUY' | 'SELL'>('BUY');
  const [quantity, setQuantity] = useState(10);
  const [orderType, setOrderType] = useState<'MARKET' | 'LIMIT'>('MARKET');
  const [requestedPrice, setRequestedPrice] = useState(2450.0);
  const [orderStatus, setOrderStatus] = useState<string | null>(null);

  const fetchPaperAccount = async () => {
    const token = localStorage.getItem('auth_token');
    if (!token) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/paper/accounts/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setAccount(data);
      }
    } catch {
      setError('Failed to fetch paper trading account');
    } finally {
      setLoading(false);
    }
  };

  const fetchOrdersAndTrades = async () => {
    const token = localStorage.getItem('auth_token');
    if (!token) return;
    try {
      const [ordRes, trdRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/v1/paper/accounts/me/orders`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API_BASE_URL}/api/v1/paper/accounts/me/trades`, { headers: { Authorization: `Bearer ${token}` } }),
      ]);
      if (ordRes.ok) setOrders(await ordRes.json());
      if (trdRes.ok) setTrades(await trdRes.json());
    } catch {
      // Ignore
    }
  };

  useEffect(() => {
    fetchPaperAccount();
    fetchOrdersAndTrades();
  }, []);

  const handleSubmitOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = localStorage.getItem('auth_token');
    if (!token) return;
    setOrderStatus(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/paper/accounts/me/orders`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          symbol,
          side,
          quantity,
          order_type: orderType,
          requested_price: orderType === 'LIMIT' ? requestedPrice : undefined,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Order execution failed');
      setOrderStatus(`Order Executed! Status: ${data.status}`);
      fetchPaperAccount();
      fetchOrdersAndTrades();
    } catch (err: any) {
      setOrderStatus(`Rejected: ${err.message}`);
    }
  };

  return (
    <div className="h-full flex flex-col bg-slate-900 text-slate-100 p-4 border border-slate-800 rounded-lg font-sans overflow-y-auto">
      {/* Simulation Banner */}
      <div className="bg-amber-950/60 border border-amber-800/60 p-2 rounded text-center text-[10px] font-bold text-amber-400 tracking-wider uppercase mb-3">
        PAPER TRADING — SIMULATION ONLY — NO REAL MONEY OR BROKER EXECUTION
      </div>

      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <h3 className="text-xs font-bold uppercase tracking-wider text-blue-400">
          Virtual Portfolio & Order Ticket
        </h3>
        <button
          onClick={() => {
            fetchPaperAccount();
            fetchOrdersAndTrades();
          }}
          className="text-[11px] text-blue-400 hover:text-blue-300 font-semibold"
        >
          Refresh
        </button>
      </div>

      {loading ? (
        <div className="p-8 text-center text-xs text-slate-500">Loading paper account...</div>
      ) : !account ? (
        <div className="p-8 text-center text-xs text-slate-500">No active paper account found</div>
      ) : (
        <div className="mt-3 space-y-4">
          {/* Account Metrics Grid */}
          <div className="grid grid-cols-4 gap-2 text-xs">
            <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase">Available Cash</span>
              <div className="text-sm font-bold text-slate-100 mt-0.5">₹{account.available_cash.toLocaleString()}</div>
            </div>
            <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase">Total Equity</span>
              <div className="text-sm font-bold text-slate-100 mt-0.5">₹{account.total_equity.toLocaleString()}</div>
            </div>
            <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase">Unrealized P&L</span>
              <div className={`text-sm font-bold mt-0.5 ${account.unrealized_pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                ₹{account.unrealized_pnl.toLocaleString()}
              </div>
            </div>
            <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase">Return %</span>
              <div className={`text-sm font-bold mt-0.5 ${account.return_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                {account.return_pct}%
              </div>
            </div>
          </div>

          {/* Order Ticket */}
          <form onSubmit={handleSubmitOrder} className="bg-slate-950 p-3 rounded border border-slate-800 space-y-3">
            <h4 className="text-[11px] font-bold text-slate-300 uppercase tracking-wider">
              Simulated Order Ticket
            </h4>
            <div className="grid grid-cols-4 gap-2 text-xs">
              <div>
                <label className="text-[10px] text-slate-400 block mb-1">Symbol</label>
                <input
                  type="text"
                  value={symbol}
                  onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                  className="w-full bg-slate-900 border border-slate-800 text-slate-200 px-2 py-1 rounded focus:outline-none uppercase font-bold"
                />
              </div>
              <div>
                <label className="text-[10px] text-slate-400 block mb-1">Side</label>
                <select
                  value={side}
                  onChange={(e) => setSide(e.target.value as any)}
                  className="w-full bg-slate-900 border border-slate-800 text-slate-200 px-2 py-1 rounded focus:outline-none font-bold"
                >
                  <option value="BUY">BUY</option>
                  <option value="SELL">SELL</option>
                </select>
              </div>
              <div>
                <label className="text-[10px] text-slate-400 block mb-1">Quantity</label>
                <input
                  type="number"
                  value={quantity}
                  onChange={(e) => setQuantity(Number(e.target.value))}
                  className="w-full bg-slate-900 border border-slate-800 text-slate-200 px-2 py-1 rounded focus:outline-none font-bold"
                  min={1}
                />
              </div>
              <div>
                <label className="text-[10px] text-slate-400 block mb-1">Order Type</label>
                <select
                  value={orderType}
                  onChange={(e) => setOrderType(e.target.value as any)}
                  className="w-full bg-slate-900 border border-slate-800 text-slate-200 px-2 py-1 rounded focus:outline-none font-bold"
                >
                  <option value="MARKET">MARKET</option>
                  <option value="LIMIT">LIMIT</option>
                </select>
              </div>
            </div>

            <div className="flex items-center justify-between pt-1">
              <span className="text-[10px] text-slate-400 italic">Simulated Fee: ₹20.00 • Slippage: 0.05%</span>
              <button
                type="submit"
                className={`px-4 py-1.5 text-xs font-bold rounded transition-colors ${
                  side === 'BUY' ? 'bg-emerald-600 hover:bg-emerald-500 text-white' : 'bg-red-600 hover:bg-red-500 text-white'
                }`}
              >
                Submit {side} Order
              </button>
            </div>
            {orderStatus && <div className="text-xs text-blue-400 font-semibold mt-1">{orderStatus}</div>}
          </form>

          {/* Current Positions */}
          <div className="bg-slate-950 p-3 rounded border border-slate-800">
            <h4 className="text-[11px] font-bold text-slate-300 uppercase tracking-wider mb-2">
              Current Open Positions ({account.positions.length})
            </h4>
            {account.positions.length === 0 ? (
              <div className="text-center py-4 text-xs text-slate-500">No open positions in paper account</div>
            ) : (
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-500 text-[10px] uppercase">
                    <th className="py-1">Instrument</th>
                    <th className="py-1">Qty</th>
                    <th className="py-1">Avg Price</th>
                    <th className="py-1">Mkt Value</th>
                    <th className="py-1 text-right">Unrealized P&L</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {account.positions.map((p: any) => (
                    <tr key={p.instrument_id} className="hover:bg-slate-900/40">
                      <td className="py-2 font-bold text-blue-400">{p.instrument_id.slice(0, 8)}</td>
                      <td className="py-2 text-slate-200">{p.quantity}</td>
                      <td className="py-2 text-slate-300">₹{p.average_entry_price}</td>
                      <td className="py-2 text-slate-300">₹{p.market_value}</td>
                      <td className={`py-2 text-right font-bold ${p.unrealized_pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                        ₹{p.unrealized_pnl}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export const StrategySimulatorPanel: React.FC = () => {
  const [strategyName, setStrategyName] = useState('SMA_CROSSOVER');
  const [symbol, setSymbol] = useState('RELIANCE');
  const [shortWindow, setShortWindow] = useState(5);
  const [longWindow, setLongWindow] = useState(20);
  const [initialCapital, setInitialCapital] = useState(1000000);
  const [backtestResult, setBacktestResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRunBacktest = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = localStorage.getItem('auth_token');
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/paper/backtests`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          strategy_name: strategyName,
          symbol,
          initial_capital: initialCapital,
          parameters: {
            short_window: shortWindow,
            long_window: longWindow,
          },
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Backtest failed');
      setBacktestResult(data);
    } catch (err: any) {
      setError(err.message || 'Error executing strategy backtest');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-full flex flex-col bg-slate-900 text-slate-100 p-4 border border-slate-800 rounded-lg font-sans overflow-y-auto">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <h3 className="text-xs font-bold uppercase tracking-wider text-blue-400">
          Strategy Simulator & Backtesting Engine
        </h3>
        <span className="text-[10px] text-slate-500 font-mono">Look-Ahead Protected</span>
      </div>

      <form onSubmit={handleRunBacktest} className="mt-3 bg-slate-950 p-3 rounded border border-slate-800 space-y-3">
        <div className="grid grid-cols-4 gap-2 text-xs">
          <div>
            <label className="text-[10px] text-slate-400 block mb-1">Strategy</label>
            <select
              value={strategyName}
              onChange={(e) => setStrategyName(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 text-slate-200 px-2 py-1 rounded focus:outline-none font-bold"
            >
              <option value="SMA_CROSSOVER">SMA_CROSSOVER</option>
              <option value="EVENT_REACTION_RESEARCH">EVENT_REACTION_RESEARCH</option>
            </select>
          </div>
          <div>
            <label className="text-[10px] text-slate-400 block mb-1">Symbol</label>
            <input
              type="text"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              className="w-full bg-slate-900 border border-slate-800 text-slate-200 px-2 py-1 rounded focus:outline-none uppercase font-bold"
            />
          </div>
          <div>
            <label className="text-[10px] text-slate-400 block mb-1">Short SMA</label>
            <input
              type="number"
              value={shortWindow}
              onChange={(e) => setShortWindow(Number(e.target.value))}
              className="w-full bg-slate-900 border border-slate-800 text-slate-200 px-2 py-1 rounded focus:outline-none font-bold"
            />
          </div>
          <div>
            <label className="text-[10px] text-slate-400 block mb-1">Long SMA</label>
            <input
              type="number"
              value={longWindow}
              onChange={(e) => setLongWindow(Number(e.target.value))}
              className="w-full bg-slate-900 border border-slate-800 text-slate-200 px-2 py-1 rounded focus:outline-none font-bold"
            />
          </div>
        </div>

        <div className="flex items-center justify-between pt-1">
          <span className="text-[10px] text-slate-500 italic">No arbitrary executable code allowed • Server-validated strategies</span>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded transition-colors disabled:opacity-50"
          >
            {loading ? 'Simulating...' : 'Run Backtest'}
          </button>
        </div>
      </form>

      {error && <div className="mt-3 p-3 bg-red-950/40 border border-red-800/50 rounded text-xs text-red-400">{error}</div>}

      {backtestResult && (
        <div className="mt-4 space-y-3">
          <div className="bg-slate-950 p-3 rounded border border-slate-800">
            <h4 className="text-[11px] font-bold text-slate-300 uppercase tracking-wider mb-2">
              Backtest Performance Metrics
            </h4>
            <div className="grid grid-cols-4 gap-2 text-center text-xs">
              <div className="bg-slate-900 p-2 rounded">
                <span className="text-[10px] text-slate-500">Final Equity</span>
                <div className="font-bold text-slate-100 mt-0.5">₹{backtestResult.final_equity.toLocaleString()}</div>
              </div>
              <div className="bg-slate-900 p-2 rounded">
                <span className="text-[10px] text-slate-500">Total Return</span>
                <div className={`font-bold mt-0.5 ${backtestResult.total_return_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                  {backtestResult.total_return_pct}%
                </div>
              </div>
              <div className="bg-slate-900 p-2 rounded">
                <span className="text-[10px] text-slate-500">Max Drawdown</span>
                <div className="font-bold text-red-400 mt-0.5">{backtestResult.max_drawdown_pct}%</div>
              </div>
              <div className="bg-slate-900 p-2 rounded">
                <span className="text-[10px] text-slate-500">Win Rate</span>
                <div className="font-bold text-blue-400 mt-0.5">{backtestResult.win_rate_pct}% ({backtestResult.trade_count} trades)</div>
              </div>
            </div>
          </div>

          <div className="p-2.5 bg-slate-950/60 border border-slate-800 rounded text-[10px] text-slate-400 italic">
            {backtestResult.disclaimer}
          </div>
        </div>
      )}
    </div>
  );
};

// Register in PanelRegistry
panelRegistry.register({
  type: 'PAPER_TRADING',
  title: 'Paper Trading Terminal',
  category: 'Portfolio',
  description: 'Simulated paper trading, orders, positions, and virtual portfolio tracking',
  component: PaperTradingPanel,
  defaultWidth: 6,
  defaultHeight: 5,
});

panelRegistry.register({
  type: 'STRATEGY_SIMULATOR',
  title: 'Strategy Backtest Simulator',
  category: 'Portfolio',
  description: 'Deterministic backtest engine with look-ahead bias protection',
  component: StrategySimulatorPanel,
  defaultWidth: 6,
  defaultHeight: 5,
});
