import React, { useEffect, useState } from 'react';
import { api } from '../../../lib/api';
import { OHLCV } from '../../../types/market';
import { PanelProps } from '../../../types/panel';
import { Activity, BarChart2 } from 'lucide-react';

export const OHLCChartPanel: React.FC<PanelProps> = ({ symbol = 'AAPL' }) => {
  const [candles, setCandles] = useState<OHLCV[]>([]);
  const [interval, setInterval] = useState('1d');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let isMounted = true;
    api.getOHLCV(symbol, interval, 15).then((res) => {
      if (isMounted) {
        setCandles(res);
        setLoading(false);
      }
    });
    return () => {
      isMounted = false;
    };
  }, [symbol, interval]);

  if (loading) return <div className="text-slate-500 animate-pulse p-4 text-center">Loading Candlestick Feed...</div>;

  const maxPrice = Math.max(...candles.map((c) => c.high), 1);
  const minPrice = Math.min(...candles.map((c) => c.low), 0);

  return (
    <div className="space-y-3 font-mono">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-xs">
        <span className="font-bold text-slate-200">{symbol} OHLC Candlestick</span>
        <div className="flex space-x-1">
          {['1m', '5m', '1h', '1d'].map((i) => (
            <button
              key={i}
              onClick={() => {
                setLoading(true);
                setInterval(i);
              }}
              className={`px-1.5 py-0.5 text-[10px] rounded ${
                interval === i ? 'bg-emerald-950 text-emerald-400 font-bold border border-emerald-800' : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              {i}
            </button>
          ))}
        </div>
      </div>

      <div className="flex items-end justify-between space-x-1.5 bg-slate-950 border border-slate-800 rounded p-3 h-40">
        {candles.map((c, idx) => {
          const isGreen = c.close >= c.open;
          const range = maxPrice - minPrice || 1;
          const heightPct = Math.max(10, ((c.close - minPrice) / range) * 100);

          return (
            <div key={idx} className="flex-1 flex flex-col items-center justify-end h-full">
              <div
                style={{ height: `${heightPct}%` }}
                className={`w-full rounded-t transition-all ${
                  isGreen ? 'bg-emerald-500 hover:bg-emerald-400' : 'bg-red-500 hover:bg-red-400'
                }`}
                title={`Close: $${c.close}`}
              />
            </div>
          );
        })}
      </div>
    </div>
  );
};

export const VolumePanel: React.FC<PanelProps> = () => {
  return (
    <div className="space-y-2 font-mono text-xs">
      <div className="flex items-center justify-between text-slate-400 border-b border-slate-800 pb-1">
        <span className="flex items-center gap-1"><BarChart2 className="h-3.5 w-3.5 text-emerald-400" /> Realtime Volume Histogram</span>
        <span className="text-[10px] text-slate-500">AAPL</span>
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
        <span className="text-emerald-400 font-bold">$184.65</span>
      </div>
      <div className="bg-slate-950 border border-slate-800 p-3 rounded space-y-1">
        <div className="flex justify-between text-slate-300">
          <span className="text-slate-500">Upper Band (+2 SD):</span>
          <span>$186.20</span>
        </div>
        <div className="flex justify-between text-slate-300">
          <span className="text-slate-500">Lower Band (-2 SD):</span>
          <span>$183.10</span>
        </div>
        <p className="text-[10px] text-slate-500 pt-1">Price currently trading above intraday VWAP baseline (institutional support).</p>
      </div>
    </div>
  );
};
