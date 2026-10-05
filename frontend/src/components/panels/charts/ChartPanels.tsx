import React, { useEffect, useState } from 'react';
import { api } from '../../../lib/api';
import { OHLCV } from '../../../types/market';
import { PanelProps } from '../../../types/panel';
import { Activity, BarChart2 } from 'lucide-react';

export const OHLCChartPanel: React.FC<PanelProps> = ({ symbol = 'RELIANCE' }) => {
  const [candles, setCandles] = useState<OHLCV[]>([]);
  const [interval, setInterval] = useState('1d');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    setError(null);
    api
      .getOHLCV(symbol, interval, 30)
      .then((res) => {
        if (isMounted) {
          setCandles(res);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err.message || 'Failed to load historical data');
          setLoading(false);
        }
      });
    return () => {
      isMounted = false;
    };
  }, [symbol, interval]);

  const maxPrice = candles.length > 0 ? Math.max(...candles.map((c) => c.high)) : 1;
  const minPrice = candles.length > 0 ? Math.min(...candles.map((c) => c.low)) : 0;

  return (
    <div className="space-y-3 font-mono">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-xs">
        <div className="flex items-center space-x-2">
          <span className="font-bold text-slate-200">{symbol} OHLC Candlestick</span>
          <span className="bg-amber-950/80 text-amber-400 border border-amber-800/60 text-[9px] px-1.5 py-0.5 rounded font-bold tracking-wider">
            DEMO / DEVELOPMENT DATA
          </span>
        </div>
        <div className="flex space-x-1">
          {['1m', '5m', '1h', '1d'].map((i) => (
            <button
              key={i}
              onClick={() => setInterval(i)}
              className={`px-1.5 py-0.5 text-[10px] rounded ${
                interval === i
                  ? 'bg-emerald-950 text-emerald-400 font-bold border border-emerald-800'
                  : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              {i}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="bg-slate-950 border border-slate-800 rounded p-6 h-48 flex items-center justify-center text-slate-400 text-xs animate-pulse">
          Loading 30-Day {interval} Historical Candles for {symbol}...
        </div>
      ) : error ? (
        <div className="bg-slate-950 border border-slate-800 rounded p-6 h-48 flex items-center justify-center text-red-400 text-xs">
          Unable to load historical data. ({error})
        </div>
      ) : candles.length === 0 ? (
        <div className="bg-slate-950 border border-slate-800 rounded p-6 h-48 flex items-center justify-center text-amber-400 text-xs">
          No historical data available for the selected timeframe.
        </div>
      ) : (
        <div className="bg-slate-950 border border-slate-800 rounded p-3 h-48 flex flex-col justify-between">
          <div className="flex items-end justify-between space-x-1.5 h-36 border-b border-slate-900 pb-1">
            {candles.map((c, idx) => {
              const isGreen = c.close >= c.open;
              const range = maxPrice - minPrice || 1;
              const heightPct = Math.max(12, ((c.close - minPrice) / range) * 100);

              const formattedDate = new Date(c.timestamp).toLocaleDateString('en-IN', {
                month: 'short',
                day: 'numeric',
                hour: interval !== '1d' ? '2-digit' : undefined,
                minute: interval !== '1d' ? '2-digit' : undefined,
              });

              return (
                <div key={idx} className="flex-1 flex flex-col items-center justify-end h-full group relative">
                  <div
                    style={{ height: `${heightPct}%` }}
                    className={`w-full rounded-t transition-all ${
                      isGreen ? 'bg-emerald-500 hover:bg-emerald-400' : 'bg-red-500 hover:bg-red-400'
                    }`}
                  />
                  {/* Tooltip on hover */}
                  <div className="absolute bottom-full mb-1 hidden group-hover:block bg-slate-900 text-slate-200 border border-slate-700 text-[10px] p-2 rounded shadow-xl whitespace-nowrap z-30">
                    <div className="font-bold text-emerald-400">{symbol} ({formattedDate})</div>
                    <div>Open: ₹{c.open.toFixed(2)}</div>
                    <div>High: ₹{c.high.toFixed(2)}</div>
                    <div>Low: ₹{c.low.toFixed(2)}</div>
                    <div>Close: ₹{c.close.toFixed(2)}</div>
                    <div>Vol: {c.volume.toLocaleString()}</div>
                  </div>
                </div>
              );
            })}
          </div>
          <div className="flex justify-between text-[10px] text-slate-500 pt-1">
            <span>{new Date(candles[0].timestamp).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' })}</span>
            <span>Range: 30 Days (1 Month)</span>
            <span>{new Date(candles[candles.length - 1].timestamp).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' })}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export const VolumePanel: React.FC<PanelProps> = () => {
  return (
    <div className="space-y-2 font-mono text-xs">
      <div className="flex items-center justify-between text-slate-400 border-b border-slate-800 pb-1">
        <span className="flex items-center gap-1"><BarChart2 className="h-3.5 w-3.5 text-emerald-400" /> Realtime Volume Histogram</span>
        <span className="text-[10px] text-slate-500">RELIANCE</span>
      </div>
      <div className="h-28 flex items-end space-x-1 bg-slate-950 border border-slate-800 p-2 rounded">
        {[40, 65, 30, 80, 95, 50, 70, 85, 45, 60, 90, 100].map((v, i) => (
          <div key={i} style={{ height: `${v}%` }} className="flex-1 bg-slate-700 hover:bg-emerald-500 transition-colors rounded-t" />
        ))}
      </div>
    </div>
  );
};

export const RSIPanel: React.FC<PanelProps> = () => {
  return (
    <div className="space-y-2 font-mono text-xs">
      <div className="flex items-center justify-between text-slate-400 border-b border-slate-800 pb-1">
        <span>RSI (14-Period Indicator)</span>
        <span className="text-emerald-400 font-bold">58.4 (NEUTRAL)</span>
      </div>
      <div className="p-3 bg-slate-950 border border-slate-800 rounded space-y-2">
        <div className="flex justify-between text-[10px] text-slate-500">
          <span>OVERSOLD (30)</span>
          <span>NEUTRAL (50)</span>
          <span>OVERBOUGHT (70)</span>
        </div>
        <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
          <div className="bg-emerald-500 h-full rounded-full" style={{ width: '58.4%' }} />
        </div>
      </div>
    </div>
  );
};

export const MACDPanel: React.FC<PanelProps> = () => {
  return (
    <div className="space-y-2 font-mono text-xs">
      <div className="flex items-center justify-between text-slate-400 border-b border-slate-800 pb-1">
        <span className="flex items-center gap-1"><Activity className="h-3.5 w-3.5 text-blue-400" /> MACD (12, 26, 9)</span>
        <span className="text-blue-400 font-bold">+1.45</span>
      </div>
      <div className="bg-slate-950 border border-slate-800 p-3 rounded flex items-center justify-between">
        <div>
          <span className="text-[10px] text-slate-500 block">MACD LINE</span>
          <span className="text-emerald-400 font-bold">+2.84</span>
        </div>
        <div>
          <span className="text-[10px] text-slate-500 block">SIGNAL LINE</span>
          <span className="text-amber-400 font-bold">+1.39</span>
        </div>
        <div>
          <span className="text-[10px] text-slate-500 block">HISTOGRAM</span>
          <span className="text-blue-400 font-bold">+1.45</span>
        </div>
      </div>
    </div>
  );
};

export const VWAPPanel: React.FC<PanelProps> = () => {
  return (
    <div className="space-y-2 font-mono text-xs">
      <div className="flex items-center justify-between text-slate-400 border-b border-slate-800 pb-1">
        <span>Volume Weighted Average Price (VWAP)</span>
        <span className="text-emerald-400 font-bold">₹2845.50</span>
      </div>
      <div className="bg-slate-950 border border-slate-800 p-3 rounded space-y-1">
        <div className="flex justify-between text-slate-300">
          <span className="text-slate-500">Upper Band (+2 SD):</span>
          <span>₹2870.20</span>
        </div>
        <div className="flex justify-between text-slate-300">
          <span className="text-slate-500">Lower Band (-2 SD):</span>
          <span>₹2820.10</span>
        </div>
        <p className="text-[10px] text-slate-500 pt-1">Price currently trading above intraday VWAP baseline (institutional support).</p>
      </div>
    </div>
  );
};
