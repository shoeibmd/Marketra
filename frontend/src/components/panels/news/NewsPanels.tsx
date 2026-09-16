import React, { useEffect, useState } from 'react';
import { api } from '../../../lib/api';
import { NewsArticle } from '../../../types/market';
import { PanelProps } from '../../../types/panel';
import { Newspaper, ExternalLink, Search } from 'lucide-react';

export const MarketNewsPanel: React.FC<PanelProps> = () => {
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    api.getNews(undefined, 5).then((res) => {
      if (isMounted) {
        setArticles(res);
        setLoading(false);
      }
    });
    return () => {
      isMounted = false;
    };
  }, []);

  if (loading) return <div className="text-slate-500 animate-pulse p-4 text-center">Loading News Feed...</div>;

  return (
    <div className="space-y-3 font-mono text-xs">
      <div className="flex items-center space-x-1.5 border-b border-slate-800 pb-1.5 text-slate-400">
        <Newspaper className="h-3.5 w-3.5 text-emerald-400" />
        <span className="font-bold text-slate-200">Global Financial News</span>
      </div>
      <div className="space-y-2">
        {articles.map((art) => (
          <a
            key={art.id}
            href={art.url}
            target="_blank"
            rel="noreferrer"
            className="block p-2 bg-slate-950 border border-slate-800 rounded hover:border-slate-700 transition-colors"
          >
            <div className="flex items-center justify-between text-[10px] text-slate-500 mb-1">
              <span>{art.source_name}</span>
              <span>{new Date(art.published_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
            </div>
            <h4 className="font-bold text-slate-200 hover:text-emerald-400 leading-snug">{art.title}</h4>
            {art.summary && <p className="text-[11px] text-slate-400 mt-1 line-clamp-2">{art.summary}</p>}
          </a>
        ))}
      </div>
    </div>
  );
};

export const CompanyNewsPanel: React.FC<PanelProps> = ({ symbol = 'AAPL' }) => {
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    api.getNews(symbol, 5).then((res) => {
      if (isMounted) {
        setArticles(res);
        setLoading(false);
      }
    });
    return () => {
      isMounted = false;
    };
  }, [symbol]);

  if (loading) return <div className="text-slate-500 animate-pulse p-4 text-center">Loading Company News...</div>;

  return (
    <div className="space-y-3 font-mono text-xs">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-slate-400">
        <span className="font-bold text-slate-200">{symbol} Coverage</span>
        <span className="text-[10px] bg-slate-800 px-1.5 py-0.5 rounded text-emerald-400">{symbol}</span>
      </div>
      <div className="space-y-2">
        {articles.map((art) => (
          <a
            key={art.id}
            href={art.url}
            target="_blank"
            rel="noreferrer"
            className="block p-2 bg-slate-950 border border-slate-800 rounded hover:border-slate-700"
          >
            <h4 className="font-bold text-slate-200 flex items-center justify-between">
              <span className="truncate">{art.title}</span>
              <ExternalLink className="h-3 w-3 text-slate-500 flex-shrink-0 ml-1" />
            </h4>
          </a>
        ))}
      </div>
    </div>
  );
};

export const NewsSearchPanel: React.FC<PanelProps> = () => {
  const [query, setQuery] = useState('');

  return (
    <div className="space-y-3 font-mono text-xs">
      <div className="relative">
        <Search className="absolute left-2.5 top-2 h-3.5 w-3.5 text-slate-500" />
        <input
          type="text"
          placeholder="Filter news by topic..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full bg-slate-950 border border-slate-800 rounded pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-emerald-500"
        />
      </div>
      <p className="text-[11px] text-slate-500 text-center py-4">
        {query ? `Filtering for keyword "${query}"...` : 'Enter a query above to search article archives.'}
      </p>
    </div>
  );
};
