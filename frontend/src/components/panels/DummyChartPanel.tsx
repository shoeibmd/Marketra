import React, { useEffect, useState } from 'react';
import { api } from '../../lib/api';
import { PanelProps } from '../../types/panel';
import { OHLCV } from '../../types/market';

export const DummyChartPanel: React.FC<PanelProps> = ({ symbol = 'AAPL' }) => {
  const [candles, setCandles] = useState<OHLCV[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getOHLCV(symbol, '1d', 7)
      .then((data) => {
        setCandles(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load chart panel data:', err);
        setLoading(false);
      });
  }, [symbol]);

  if (loading) {
    return <div className="text-slate-500 animate-pulse p-4 text-center">Loading chart feed...</div>;
  }

  const maxPrice = Math.max(...candles.map((c) => c.high), 1);
  const minPrice = Math.min(...candles.map((c) => c.low), 0);

  return (
    <div className="flex flex-col h-full space-y-3 font-mono">
      <div className="flex items-center justify-between text-[11px] border-b border-slate-800 pb-1">
        <span className="text-slate-400">TradingView Lightweight Simulation</span>
        <span className="text-emerald-400 font-bold">{symbol} / USD</span>
      </div>

      {/* Synthetic Candle Bar Visualization */}
      <div className="flex-1 flex items-end justify-between space-x-2 bg-slate-950/60 border border-slate-800/80 rounded p-3 min-h-[140px]">
        {candles.map((c, i) => {
          const isGreen = c.close >= c.open;
          const range = maxPrice - minPrice || 1;
          const heightPct = Math.max(15, ((c.close - minPrice) / range) * 100);

          return (
            <div key={i} className="flex-1 flex flex-col items-center justify-end h-full">
              <div
                style={{ height: `${heightPct}%` }}
                className={`w-full rounded-t transition-all ${
                  isGreen ? 'bg-emerald-500/80 hover:bg-emerald-400' : 'bg-red-500/80 hover:bg-red-400'
                }`}
                title={`Date: ${new Date(c.timestamp).toLocaleDateString()}\nClose: $${c.close}`}
              />
              <span className="text-[9px] text-slate-500 mt-1 truncate">
                {new Date(c.timestamp).toLocaleDateString(undefined, { month: 'numeric', day: 'numeric' })}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
