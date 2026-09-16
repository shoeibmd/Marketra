import React, { useEffect, useState } from 'react';
import { api, MarketOverviewResponse, WatchlistItemResponse } from '../../../lib/api';
import { PanelProps } from '../../../types/panel';
import { ArrowUpRight, ArrowDownRight, TrendingUp, Activity } from 'lucide-react';

export const MarketOverviewPanel: React.FC<PanelProps> = () => {
  const [data, setData] = useState<MarketOverviewResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getMarketOverview()
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || 'Failed to fetch market overview');
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="text-slate-500 animate-pulse p-4 text-center">Loading Market Overview...</div>;
  if (error) return <div className="text-red-400 p-4 text-center">Error: {error}</div>;
  if (!data) return <div className="text-slate-500 p-4 text-center">No market overview data available.</div>;

  return (
    <div className="space-y-4 font-mono">
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <span className="text-slate-400 text-xs flex items-center gap-1">
          <Activity className="h-3.5 w-3.5 text-emerald-400" /> Market Status:
        </span>
        <span className="text-emerald-400 text-xs font-bold bg-emerald-950 px-2 py-0.5 rounded border border-emerald-800">
          {data.market_status}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2">
        {data.indices.map((idx) => (
          <div key={idx.symbol} className="bg-slate-950 border border-slate-800 p-2 rounded">
            <div className="flex items-center justify-between text-[11px]">
              <span className="text-slate-300 font-bold">{idx.symbol}</span>
              <span className="text-emerald-400 flex items-center">
                <ArrowUpRight className="h-3 w-3" /> +{idx.change_percent}%
              </span>
            </div>
            <div className="text-sm font-bold text-slate-100 mt-1">${idx.last_price.toFixed(2)}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export const WatchlistPanel: React.FC<PanelProps> = () => {
  const [watchlist, setWatchlist] = useState<WatchlistItemResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getWatchlist()
      .then((res) => {
        setWatchlist(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || 'Failed to fetch watchlist');
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="text-slate-500 animate-pulse p-4 text-center">Loading Watchlist...</div>;
  if (error) return <div className="text-red-400 p-4 text-center">Error: {error}</div>;
  if (watchlist.length === 0) return <div className="text-slate-500 p-4 text-center">Watchlist is empty.</div>;

  return (
    <div className="space-y-2 font-mono">
      <div className="grid grid-cols-3 text-[10px] text-slate-500 border-b border-slate-800 pb-1">
        <span>SYMBOL</span>
        <span>LAST PRICE</span>
        <span className="text-right">BID / ASK</span>
      </div>
      {watchlist.map((item) => (
        <div key={item.symbol} className="grid grid-cols-3 text-xs items-center py-1 border-b border-slate-800/40">
          <div>
            <span className="font-bold text-slate-200 block">{item.symbol}</span>
            <span className="text-[10px] text-slate-500">{item.name}</span>
          </div>
          <span className="font-bold text-slate-100">${item.quote.last_price.toFixed(2)}</span>
          <span className="text-right text-[11px] text-slate-400">
            ${item.quote.bid_price.toFixed(2)} / ${item.quote.ask_price.toFixed(2)}
          </span>
        </div>
      ))}
    </div>
  );
};

export const GainersLosersPanel: React.FC<PanelProps> = () => {
  const [data, setData] = useState<MarketOverviewResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getMarketOverview().then((res) => {
      setData(res);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="text-slate-500 animate-pulse p-4 text-center">Loading Market Movers...</div>;

  return (
    <div className="space-y-3 font-mono text-xs">
      <div>
        <h4 className="text-[10px] text-emerald-400 font-bold mb-1 flex items-center gap-1">
          <TrendingUp className="h-3 w-3" /> TOP GAINERS
        </h4>
        {data?.gainers.map((g) => (
          <div key={g.symbol} className="flex justify-between items-center py-1 border-b border-slate-800/40">
            <span className="font-bold text-slate-200">{g.symbol}</span>
            <span className="text-emerald-400">${g.last_price.toFixed(2)} (+{g.change_percent}%)</span>
          </div>
        ))}
      </div>

      <div>
        <h4 className="text-[10px] text-red-400 font-bold mb-1 flex items-center gap-1">
          <ArrowDownRight className="h-3 w-3" /> TOP LOSERS
        </h4>
        {data?.losers.map((l) => (
          <div key={l.symbol} className="flex justify-between items-center py-1 border-b border-slate-800/40">
            <span className="font-bold text-slate-200">{l.symbol}</span>
            <span className="text-red-400">${l.last_price.toFixed(2)} (-0.42%)</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export const MostActivePanel: React.FC<PanelProps> = () => {
  return (
    <div className="space-y-2 font-mono text-xs">
      <div className="grid grid-cols-3 text-[10px] text-slate-500 border-b border-slate-800 pb-1">
        <span>SYMBOL</span>
        <span>PRICE</span>
        <span className="text-right">VOLUME</span>
      </div>
      {[
        { symbol: 'AAPL', price: 185.20, volume: '45.2M' },
        { symbol: 'TSLA', price: 220.50, volume: '38.9M' },
        { symbol: 'SPY', price: 510.10, volume: '62.1M' },
        { symbol: 'BTC-USD', price: 64200.00, volume: '12.4K' },
      ].map((item) => (
        <div key={item.symbol} className="grid grid-cols-3 py-1 border-b border-slate-800/40">
          <span className="font-bold text-slate-200">{item.symbol}</span>
          <span className="text-slate-100">${item.price.toFixed(2)}</span>
          <span className="text-right text-slate-400">{item.volume}</span>
        </div>
      ))}
    </div>
  );
};
