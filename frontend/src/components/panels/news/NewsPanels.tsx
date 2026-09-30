import React, { useEffect, useState } from 'react';
import { api } from '../../../lib/api';
import { NewsArticle } from '../../../types/market';
import { PanelProps } from '../../../types/panel';
import { Newspaper, ExternalLink, Search, X, Sparkles, Building2 } from 'lucide-react';

const CATEGORIES = [
  'ALL',
  'HIGH IMPORTANCE',
  'CORPORATE',
  'RESULTS',
  'ACQUISITION',
  'INVESTMENT',
  'DIVIDEND',
  'REGULATORY',
  'MARKET',
];

export const LiveMarketNewsPanel: React.FC<PanelProps> = () => {
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedArticle, setSelectedArticle] = useState<NewsArticle | null>(null);

  const fetchNews = async () => {
    setLoading(true);
    try {
      if (searchQuery.trim() || (activeCategory !== 'ALL' && activeCategory !== 'HIGH IMPORTANCE')) {
        const categoryFilter = activeCategory === 'HIGH IMPORTANCE' ? undefined : activeCategory;
        const res = await api.searchNews(searchQuery, categoryFilter, 1, 15);
        setArticles(res.items);
      } else {
        const res = await api.getLiveNews(1, 15);
        let items = res.items;
        if (activeCategory === 'HIGH IMPORTANCE') {
          items = items.filter((a) => a.ai_importance === 'HIGH' || a.ai_importance === 'CRITICAL');
        }
        setArticles(items);
      }
    } catch (err) {
      console.error('Failed to load news:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNews();
  }, [activeCategory, searchQuery]);

  const getTimeAgo = (dateStr: string) => {
    const diffMs = new Date().getTime() - new Date(dateStr).getTime();
    const mins = Math.floor(diffMs / 60000);
    if (mins < 60) return `${Math.max(1, mins)} mins ago`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours} hrs ago`;
    return `${Math.floor(hours / 24)} days ago`;
  };

  return (
    <div className="space-y-3 font-mono text-xs h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center space-x-2">
          <Newspaper className="h-4 w-4 text-emerald-400" />
          <span className="font-bold text-slate-100 text-sm">LIVE MARKET NEWS</span>
        </div>
        <span className="text-[10px] bg-slate-800 text-emerald-400 px-2 py-0.5 rounded font-bold">
          NSE / BSE
        </span>
      </div>

      {/* Search Input */}
      <div className="relative">
        <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-slate-500" />
        <input
          type="text"
          placeholder="Search by Company, Symbol, or Keyword (e.g. RELIANCE, TCS)..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full bg-slate-950 border border-slate-800 rounded pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-emerald-500"
        />
      </div>

      {/* Category Filter Chips */}
      <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 scrollbar-none">
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={`px-2.5 py-1 rounded text-[10px] font-bold whitespace-nowrap transition-colors ${
              activeCategory === cat
                ? 'bg-emerald-600 text-white'
                : 'bg-slate-900 border border-slate-800 text-slate-400 hover:border-slate-700'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Cards List */}
      {loading ? (
        <div className="text-slate-500 animate-pulse p-8 text-center flex-1">
          Loading Live Indian Market News...
        </div>
      ) : articles.length === 0 ? (
        <div className="text-slate-500 p-8 text-center flex-1">
          No announcements found matching current filter.
        </div>
      ) : (
        <div className="space-y-2.5 flex-1 overflow-y-auto pr-1">
          {articles.map((art) => {
            const isHigh = art.ai_importance === 'HIGH' || art.ai_importance === 'CRITICAL';
            const companyName = art.company || art.symbol || 'INDIAN LISTED ENTITY';
            const catLabel = (art.category || 'general').replace('_', ' ').toUpperCase();

            return (
              <div
                key={art.id}
                className="p-3 bg-slate-950 border border-slate-800 hover:border-slate-700 rounded-lg transition-all space-y-2"
              >
                {/* Top Badges Bar */}
                <div className="flex items-center justify-between text-[10px]">
                  <div className="flex items-center space-x-2">
                    <span
                      className={`px-1.5 py-0.5 rounded font-bold ${
                        isHigh
                          ? 'bg-rose-950/80 border border-rose-800 text-rose-400'
                          : 'bg-slate-800 text-slate-300'
                      }`}
                    >
                      {art.ai_importance || 'MEDIUM'}
                    </span>
                    <span className="font-bold text-emerald-400 flex items-center space-x-1">
                      <Building2 className="h-3 w-3" />
                      <span>{companyName}</span>
                    </span>
                    <span className="bg-slate-900 text-slate-400 border border-slate-800 px-1.5 py-0.5 rounded">
                      {catLabel}
                    </span>
                  </div>
                  <span className="text-slate-500">{getTimeAgo(art.published_at)}</span>
                </div>

                {/* Title / Headline */}
                <h4 className="font-bold text-slate-100 text-xs leading-snug">{art.title}</h4>

                {/* Short AI Explanation / Why it matters */}
                {art.ai_analysis && (
                  <div className="p-2 bg-slate-900/60 border border-slate-800/80 rounded text-[11px] text-slate-300 space-y-1">
                    <div className="flex items-center space-x-1 text-emerald-400 font-bold text-[10px]">
                      <Sparkles className="h-3 w-3" />
                      <span>Why it matters:</span>
                    </div>
                    <p className="line-clamp-2">{art.ai_analysis.importance_reason || art.ai_analysis.what_happened}</p>
                  </div>
                )}

                {/* Bottom Meta & Action */}
                <div className="flex items-center justify-between pt-1 border-t border-slate-900 text-[10px]">
                  <div className="flex items-center space-x-3 text-slate-500">
                    <span>Source: <strong className="text-slate-400">{art.source_name}</strong></span>
                    {art.ai_impact && (
                      <span>
                        Impact:{' '}
                        <strong
                          className={
                            art.ai_impact === 'POSITIVE'
                              ? 'text-emerald-400'
                              : art.ai_impact === 'NEGATIVE'
                              ? 'text-rose-400'
                              : 'text-slate-400'
                          }
                        >
                          {art.ai_impact}
                        </strong>
                      </span>
                    )}
                  </div>
                  <button
                    onClick={() => setSelectedArticle(art)}
                    className="bg-emerald-950 hover:bg-emerald-900 text-emerald-300 border border-emerald-800 px-2.5 py-1 rounded text-[10px] font-bold transition-colors"
                  >
                    READ DETAILS
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* News Detail View Modal */}
      {selectedArticle && (
        <NewsDetailModal article={selectedArticle} onClose={() => setSelectedArticle(null)} />
      )}
    </div>
  );
};

export const MarketNewsPanel: React.FC<PanelProps> = LiveMarketNewsPanel;

export const CompanyNewsPanel: React.FC<PanelProps> = ({ symbol = 'RELIANCE' }) => {
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

  if (loading) return <div className="text-slate-500 animate-pulse p-4 text-center">Loading {symbol} News...</div>;

  return (
    <div className="space-y-3 font-mono text-xs">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-slate-400">
        <span className="font-bold text-slate-200">{symbol} Live Feed</span>
        <span className="text-[10px] bg-slate-800 px-1.5 py-0.5 rounded text-emerald-400 font-bold">{symbol}</span>
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

interface DetailModalProps {
  article: NewsArticle;
  onClose: () => void;
}

const NewsDetailModal: React.FC<DetailModalProps> = ({ article, onClose }) => {
  const ai = article.ai_analysis;
  const relatedCompanies = ai?.related_companies?.length ? ai.related_companies : article.associated_symbols || [];
  const categoryFormatted = (article.category || 'general').replace('_', ' ').toUpperCase();

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-xl w-full max-w-2xl max-h-[85vh] flex flex-col shadow-2xl font-mono text-xs">
        {/* Modal Header */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/40">
          <div>
            <div className="flex flex-wrap items-center gap-1.5 text-[10px] text-slate-400 mb-1">
              <span className="bg-emerald-950 text-emerald-400 border border-emerald-800 px-1.5 py-0.5 rounded font-bold">
                {article.company || article.symbol || 'INDIAN LISTED ENTITY'}
              </span>
              <span className="bg-rose-950/80 border border-rose-800 text-rose-400 px-1.5 py-0.5 rounded font-bold">
                IMPORTANCE: {article.ai_importance || 'MEDIUM'}
              </span>
              <span className="bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded font-bold">
                CATEGORY: {categoryFormatted}
              </span>
              <span>Source: {article.source_name}</span>
              <span>•</span>
              <span>{new Date(article.published_at).toLocaleString()}</span>
            </div>
            <h3 className="font-bold text-slate-100 text-sm">{article.title}</h3>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-slate-800 rounded text-slate-400 hover:text-slate-100">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-4 overflow-y-auto space-y-4 flex-1">
          {/* AI Intelligence Card */}
          {ai && (
            <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg space-y-3">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <div className="flex items-center space-x-1.5 text-emerald-400 font-bold">
                  <Sparkles className="h-4 w-4" />
                  <span>AI Structured Intelligence</span>
                </div>
                <div className="flex items-center space-x-2 text-[10px]">
                  <span className="bg-slate-800 text-slate-300 px-2 py-0.5 rounded">
                    Impact: <strong className="text-emerald-400">{ai.potential_impact}</strong>
                  </span>
                  <span className="bg-slate-800 text-slate-300 px-2 py-0.5 rounded">
                    Confidence: <strong>{Math.round(ai.ai_confidence * 100)}%</strong>
                  </span>
                </div>
              </div>

              <div className="space-y-2 text-slate-300">
                <div>
                  <strong className="text-slate-400 block text-[10px]">WHAT HAPPENED:</strong>
                  <p>{ai.what_happened}</p>
                </div>
                <div>
                  <strong className="text-slate-400 block text-[10px]">WHY IT MATTERS:</strong>
                  <p>{ai.importance_reason}</p>
                </div>
              </div>

              {/* Related Companies & Sector */}
              <div className="grid grid-cols-2 gap-2 p-2 bg-slate-900/60 rounded border border-slate-800 text-[11px]">
                <div>
                  <strong className="text-slate-400 block text-[10px]">RELATED COMPANIES:</strong>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {relatedCompanies.length > 0 ? (
                      relatedCompanies.map((c, idx) => (
                        <span key={idx} className="bg-slate-800 text-emerald-300 border border-slate-700 px-1.5 py-0.5 rounded text-[10px]">
                          {c}
                        </span>
                      ))
                    ) : (
                      <span className="text-slate-500">None specified</span>
                    )}
                  </div>
                </div>
                <div>
                  <strong className="text-slate-400 block text-[10px]">RELATED SECTOR:</strong>
                  <span className="text-slate-300 mt-1 block">{ai.related_sector || 'General Equity'}</span>
                </div>
              </div>

              {/* Source Facts */}
              {ai.source_facts && ai.source_facts.length > 0 && (
                <div>
                  <strong className="text-slate-400 block text-[10px] mb-1">VERIFIED SOURCE FACTS:</strong>
                  <ul className="list-disc list-inside space-y-0.5 text-slate-300 text-[11px]">
                    {ai.source_facts.map((fact, idx) => (
                      <li key={idx}>{fact}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* User Checklist */}
              {ai.user_monitoring_checklist && ai.user_monitoring_checklist.length > 0 && (
                <div className="p-2 bg-slate-900 rounded border border-slate-800">
                  <strong className="text-emerald-400 block text-[10px] mb-1">MONITOR NEXT CHECKLIST:</strong>
                  <ul className="list-disc list-inside space-y-0.5 text-slate-300 text-[11px]">
                    {ai.user_monitoring_checklist.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Related Announcements */}
              {ai.related_announcements && ai.related_announcements.length > 0 && (
                <div>
                  <strong className="text-slate-400 block text-[10px] mb-1">RELATED ANNOUNCEMENTS:</strong>
                  <ul className="list-disc list-inside space-y-0.5 text-slate-300 text-[11px]">
                    {ai.related_announcements.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Article Summary / Content */}
          <div>
            <strong className="text-slate-400 block text-[10px] mb-1">ANNOUNCEMENT SUMMARY:</strong>
            <p className="text-slate-300 leading-relaxed bg-slate-950 p-3 rounded border border-slate-800">
              {article.content || article.summary || 'Public corporate filing disclosure.'}
            </p>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-3 border-t border-slate-800 bg-slate-950/40 flex items-center justify-between">
          <a
            href={article.url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center space-x-1.5 text-emerald-400 hover:underline font-bold text-xs"
          >
            <span>View Original Source ({article.source_name})</span>
            <ExternalLink className="h-3.5 w-3.5" />
          </a>
          <button
            onClick={onClose}
            className="bg-slate-800 hover:bg-slate-700 text-slate-200 px-4 py-1.5 rounded font-bold text-xs transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
