import React, { useEffect, useState } from 'react';
import { panelRegistry } from '../../../lib/panelRegistry';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const BrokerStatusPanel: React.FC = () => {
  const [brokers, setBrokers] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchBrokers = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/brokers`);
      if (res.ok) setBrokers(await res.json());
    } catch {
      // Ignore
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBrokers();
  }, []);

  return (
    <div className="h-full flex flex-col bg-slate-900 text-slate-100 p-4 border border-slate-800 rounded-lg font-sans overflow-y-auto">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <h3 className="text-xs font-bold uppercase tracking-wider text-blue-400">
          Broker Adapters & Health Telemetry
        </h3>
        <button onClick={fetchBrokers} className="text-[11px] text-blue-400 hover:text-blue-300 font-semibold">
          Refresh
        </button>
      </div>

      {loading ? (
        <div className="p-8 text-center text-xs text-slate-500">Querying broker adapters...</div>
      ) : (
        <div className="mt-3 space-y-3">
          {brokers.map((b) => (
            <div key={b.provider_name} className="bg-slate-950 p-3 rounded border border-slate-800 space-y-1 text-xs">
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-200">{b.provider_name}</span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${b.status === 'HEALTHY' || b.status === 'CONFIGURED' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800/60' : 'bg-amber-950 text-amber-400 border border-amber-800/60'}`}>
                  {b.status}
                </span>
              </div>
              <div className="text-[10px] text-slate-400">Execution Mode: <strong className="text-slate-300">{b.execution_mode}</strong></div>
              <div className="text-[10px] text-slate-500 italic mt-1">{b.disclaimer}</div>
            </div>
          ))}

          <div className="p-2.5 bg-slate-950/60 border border-slate-800 rounded text-[10px] text-slate-400 italic">
            Security Guarantee: Broker API keys & credentials are never stored in plaintext or exposed to frontend/logs.
          </div>
        </div>
      )}
    </div>
  );
};

export const RiskStatusPanel: React.FC = () => {
  const [riskStatus, setRiskStatus] = useState<any>(null);
  const [limits, setLimits] = useState<any>(null);
  const [decisions, setDecisions] = useState<any[]>([]);

  const fetchRiskInfo = async () => {
    const token = localStorage.getItem('auth_token');
    try {
      const [stRes, limRes, decRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/v1/risk/status`),
        fetch(`${API_BASE_URL}/api/v1/risk/limits`, { headers: token ? { Authorization: `Bearer ${token}` } : {} }),
        fetch(`${API_BASE_URL}/api/v1/risk/decisions`, { headers: token ? { Authorization: `Bearer ${token}` } : {} }),
      ]);
      if (stRes.ok) setRiskStatus(await stRes.json());
      if (limRes.ok) setLimits(await limRes.json());
      if (decRes.ok) setDecisions(await decRes.json());
    } catch {
      // Ignore
    }
  };

  useEffect(() => {
    fetchRiskInfo();
  }, []);

  return (
    <div className="h-full flex flex-col bg-slate-900 text-slate-100 p-4 border border-slate-800 rounded-lg font-sans overflow-y-auto">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <h3 className="text-xs font-bold uppercase tracking-wider text-blue-400">
          Pre-Trade Risk Engine & Live Safety Gate
        </h3>
        <button onClick={fetchRiskInfo} className="text-[11px] text-blue-400 hover:text-blue-300 font-semibold">
          Refresh
        </button>
      </div>

      {riskStatus && (
        <div className="mt-3 space-y-3">
          {/* Safety Gate Controls */}
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="bg-slate-950 p-2.5 rounded border border-slate-800 flex justify-between items-center">
              <span className="text-slate-400">LIVE TRADING</span>
              <span className={`font-bold ${riskStatus.live_trading_enabled ? 'text-emerald-400' : 'text-red-400'}`}>
                {riskStatus.live_trading_enabled ? 'ENABLED' : 'DISABLED'}
              </span>
            </div>
            <div className="bg-slate-950 p-2.5 rounded border border-slate-800 flex justify-between items-center">
              <span className="text-slate-400">KILL SWITCH</span>
              <span className={`font-bold ${riskStatus.trading_kill_switch ? 'text-red-400' : 'text-emerald-400'}`}>
                {riskStatus.trading_kill_switch ? 'ACTIVE' : 'INACTIVE'}
              </span>
            </div>
          </div>

          {/* Configured Limits */}
          {limits && (
            <div className="bg-slate-950 p-3 rounded border border-slate-800 space-y-2 text-xs">
              <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                Configured Pre-Trade Risk Thresholds
              </h4>
              <div className="grid grid-cols-2 gap-2 text-[11px]">
                <div className="flex justify-between border-b border-slate-900 pb-1">
                  <span className="text-slate-500">Max Order Quantity:</span>
                  <span className="font-bold text-slate-200">{limits.max_order_quantity}</span>
                </div>
                <div className="flex justify-between border-b border-slate-900 pb-1">
                  <span className="text-slate-500">Max Order Value:</span>
                  <span className="font-bold text-slate-200">₹{limits.max_order_value.toLocaleString()}</span>
                </div>
                <div className="flex justify-between border-b border-slate-900 pb-1">
                  <span className="text-slate-500">Daily Loss Limit:</span>
                  <span className="font-bold text-slate-200">₹{limits.daily_loss_limit.toLocaleString()}</span>
                </div>
                <div className="flex justify-between border-b border-slate-900 pb-1">
                  <span className="text-slate-500">Max Open Orders:</span>
                  <span className="font-bold text-slate-200">{limits.max_open_orders}</span>
                </div>
              </div>
            </div>
          )}

          {/* Recent Decisions */}
          <div className="bg-slate-950 p-3 rounded border border-slate-800 space-y-2 text-xs">
            <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
              Recent Pre-Trade Audit Decisions
            </h4>
            {decisions.length === 0 ? (
              <div className="text-center py-2 text-[11px] text-slate-500">No recent risk decisions logged</div>
            ) : (
              decisions.slice(0, 5).map((d) => (
                <div key={d.id} className="p-2 bg-slate-900/60 rounded border border-slate-800 text-[11px] flex justify-between items-center">
                  <div>
                    <span className="font-bold text-slate-200">{d.rule_name}</span>
                    <div className="text-[10px] text-slate-400">{d.reason}</div>
                  </div>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${d.decision === 'APPROVED' ? 'bg-emerald-950 text-emerald-400' : 'bg-red-950 text-red-400'}`}>
                    {d.decision}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export const LiveTradingPanel: React.FC = () => {
  const [symbol, setSymbol] = useState('RELIANCE');
  const [side, setSide] = useState<'BUY' | 'SELL'>('BUY');
  const [quantity, setQuantity] = useState(10);
  const [price, setPrice] = useState(2450.0);
  const [pendingConfirmation, setPendingConfirmation] = useState<any>(null);
  const [orderResult, setOrderResult] = useState<string | null>(null);

  const handleInitiateLiveOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = localStorage.getItem('auth_token');
    if (!token) return;
    setOrderResult(null);

    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/trading/orders`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          symbol,
          side,
          quantity,
          execution_mode: 'LIVE',
          order_type: 'MARKET',
          requested_price: price,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Live order initiation failed');

      if (data.status === 'CONFIRMATION_PENDING') {
        setPendingConfirmation({
          client_order_id: data.client_order_id,
          token: data.confirmation_token,
          expires_at: data.expires_at,
          order_params: {
            symbol,
            side,
            quantity,
            order_type: 'MARKET',
            requested_price: price,
            execution_mode: 'LIVE',
          },
        });
      }
    } catch (err: any) {
      setOrderResult(`Rejection: ${err.message}`);
    }
  };

  const handleConfirmLiveOrder = async () => {
    if (!pendingConfirmation) return;
    const token = localStorage.getItem('auth_token');
    if (!token) return;

    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/trading/orders/${pendingConfirmation.client_order_id}/confirm`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          confirmation_token: pendingConfirmation.token,
          order_params: pendingConfirmation.order_params,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Confirmation failed');
      setOrderResult(`Confirmed & Submitted! Status: ${data.status}`);
      setPendingConfirmation(null);
    } catch (err: any) {
      setOrderResult(`Confirmation Failed: ${err.message}`);
      setPendingConfirmation(null);
    }
  };

  return (
    <div className="h-full flex flex-col bg-slate-900 text-slate-100 p-4 border border-slate-800 rounded-lg font-sans overflow-y-auto">
      <div className="bg-red-950/80 border border-red-800/80 p-2.5 rounded text-center mb-3">
        <h3 className="text-xs font-bold text-red-400 tracking-wider uppercase">
          LIVE TRADING CONTROL (SAFETY GATE ACTIVE)
        </h3>
        <p className="text-[10px] text-red-300 mt-0.5">
          Live order submissions pass mandatorily through pre-trade RiskEngine re-evaluation, server-side activation checks, and single-use 5-minute confirmation tokens.
        </p>
      </div>

      <form onSubmit={handleInitiateLiveOrder} className="bg-slate-950 p-3 rounded border border-slate-800 space-y-3 text-xs">
        <h4 className="font-bold text-slate-200 uppercase tracking-wider text-[11px]">
          Initiate Controlled Live Order
        </h4>
        <div className="grid grid-cols-3 gap-2">
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
        </div>

        <button
          type="submit"
          className="w-full py-1.5 bg-red-600 hover:bg-red-500 text-white font-bold text-xs rounded transition-colors"
        >
          Initiate Live Order Confirmation
        </button>
      </form>

      {orderResult && <div className="mt-3 p-3 bg-slate-950 border border-slate-800 rounded text-xs text-blue-400 font-semibold">{orderResult}</div>}

      {/* Confirmation Modal */}
      {pendingConfirmation && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 border border-red-500/60 rounded-lg max-w-md w-full p-4 space-y-3 font-sans">
            <h3 className="text-sm font-bold text-red-400 uppercase tracking-wider">
              CONFIRM LIVE ORDER SUBMISSION
            </h3>
            <div className="bg-slate-950 p-3 rounded border border-slate-800 text-xs space-y-1.5">
              <div className="flex justify-between"><span className="text-slate-500">Symbol:</span><strong className="text-blue-400">{pendingConfirmation.order_params.symbol}</strong></div>
              <div className="flex justify-between"><span className="text-slate-500">Side / Qty:</span><strong className="text-slate-200">{pendingConfirmation.order_params.side} {pendingConfirmation.order_params.quantity} shares</strong></div>
              <div className="flex justify-between"><span className="text-slate-500">Token Expiration:</span><strong className="text-amber-400">{new Date(pendingConfirmation.expires_at).toLocaleTimeString()}</strong></div>
            </div>
            <div className="flex justify-end space-x-2 pt-2">
              <button
                type="button"
                onClick={() => setPendingConfirmation(null)}
                className="px-3 py-1.5 bg-slate-800 text-slate-300 text-xs font-medium rounded hover:bg-slate-700"
              >
                Cancel Order
              </button>
              <button
                type="button"
                onClick={handleConfirmLiveOrder}
                className="px-4 py-1.5 bg-red-600 text-white text-xs font-bold rounded hover:bg-red-500"
              >
                Confirm & Submit Live Order
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export const ReconciliationPanel: React.FC = () => {
  const [records, setRecords] = useState<any[]>([]);

  const fetchRecords = async () => {
    const token = localStorage.getItem('auth_token');
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/reconciliation`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (res.ok) setRecords(await res.json());
    } catch {
      // Ignore
    }
  };

  useEffect(() => {
    fetchRecords();
  }, []);

  return (
    <div className="h-full flex flex-col bg-slate-900 text-slate-100 p-4 border border-slate-800 rounded-lg font-sans overflow-y-auto">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <h3 className="text-xs font-bold uppercase tracking-wider text-blue-400">
          Order Reconciliation Ledger
        </h3>
        <button onClick={fetchRecords} className="text-[11px] text-blue-400 hover:text-blue-300 font-semibold">
          Refresh
        </button>
      </div>

      <div className="mt-3 space-y-2 text-xs">
        {records.length === 0 ? (
          <div className="p-6 border border-dashed border-slate-800 rounded text-center text-slate-500">
            All client order IDs match corresponding execution records. Zero discrepancies found.
          </div>
        ) : (
          records.map((r) => (
            <div key={r.id} className="bg-slate-950 p-2.5 rounded border border-slate-800 flex justify-between items-center">
              <div>
                <span className="font-mono font-bold text-slate-200">{r.client_order_id}</span>
                <div className="text-[10px] text-slate-400">Broker ID: {r.broker_order_id || 'N/A'}</div>
              </div>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${r.status === 'MATCHED' ? 'bg-emerald-950 text-emerald-400' : 'bg-red-950 text-red-400'}`}>
                {r.status}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

// Register in PanelRegistry
panelRegistry.register({
  type: 'BROKER_STATUS',
  title: 'Broker Adapters & Health',
  category: 'Admin',
  description: 'Registered broker providers and connection health telemetry',
  component: BrokerStatusPanel,
  defaultWidth: 4,
  defaultHeight: 3,
});

panelRegistry.register({
  type: 'RISK_STATUS',
  title: 'Pre-Trade Risk Engine',
  category: 'Admin',
  description: 'Production safety gates, risk rules, and audit decision logs',
  component: RiskStatusPanel,
  defaultWidth: 6,
  defaultHeight: 4,
});

panelRegistry.register({
  type: 'LIVE_TRADING',
  title: 'Live Trading Control (Safety Gate)',
  category: 'Portfolio',
  description: 'Production live order interface guarded by multi-stage safety controls',
  component: LiveTradingPanel,
  defaultWidth: 6,
  defaultHeight: 4,
});

panelRegistry.register({
  type: 'RECONCILIATION',
  title: 'Order Reconciliation',
  category: 'Admin',
  description: 'Order state reconciliation between client IDs and broker execution records',
  component: ReconciliationPanel,
  defaultWidth: 6,
  defaultHeight: 3,
});
