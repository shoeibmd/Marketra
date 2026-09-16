import React, { useState } from 'react';
import { PanelProps } from '../../../types/panel';
import { Bot, FileText, Send, Sparkles } from 'lucide-react';

interface AIResponseUI {
  answer: string;
  confidence: number;
  citations: Array<{ source_type: string; source_id: string; snippet: string; relevance_score: number }>;
  source_facts: string[];
  calculated_metrics: string[];
  interpretation: string[];
}

export const AIResearchAssistantPanel: React.FC<PanelProps> = () => {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState<AIResponseUI | null>(null);
  const [loading, setLoading] = useState(false);

  const handleQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/v1/ai/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });
      const data = await res.json();
      setResponse(data);
      setLoading(false);
    } catch (err) {
      console.error('AI Query failed:', err);
      setLoading(false);
    }
  };

  return (
    <div className="space-y-3 font-mono text-xs">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-slate-300">
        <span className="font-bold flex items-center gap-1.5">
          <Bot className="h-4 w-4 text-emerald-400" /> AI Financial Research Assistant
        </span>
        <span className="text-[10px] bg-emerald-950 border border-emerald-800 text-emerald-400 px-1.5 py-0.5 rounded">
          RAG CITATIONS ACTIVE
        </span>
      </div>

      <form onSubmit={handleQuery} className="flex gap-2">
        <input
          type="text"
          placeholder="Ask AI assistant (e.g., Analyze revenue growth)..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-1 bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-emerald-500"
        />
        <button
          type="submit"
          disabled={loading}
          className="bg-emerald-950 hover:bg-emerald-900 border border-emerald-800 text-emerald-400 px-3 py-1.5 rounded font-bold transition-colors flex items-center gap-1"
        >
          <Send className="h-3.5 w-3.5" /> Query
        </button>
      </form>

      {loading && <div className="text-slate-500 animate-pulse text-center py-6">Running RAG retrieval and LLM reasoning...</div>}

      {response && (
        <div className="space-y-3 pt-2">
          <div className="p-3 bg-slate-950 border border-slate-800 rounded text-slate-200">
            <p className="leading-relaxed font-sans">{response.answer}</p>
            <div className="mt-2 text-[10px] text-slate-500 flex justify-between border-t border-slate-900 pt-1">
              <span>Model Confidence: {(response.confidence * 100).toFixed(0)}%</span>
              <span>Model: mock-financial-rag-v1</span>
            </div>
          </div>

          {/* Fact vs Interpretation Breakdown */}
          <div className="grid grid-cols-3 gap-2 text-[11px]">
            <div className="bg-slate-950 p-2 rounded border border-slate-800/80">
              <span className="text-[10px] text-emerald-400 font-bold block mb-1">SOURCE FACTS</span>
              <ul className="space-y-1 text-slate-400">
                {response.source_facts.map((f, i) => (
                  <li key={i}>• {f}</li>
                ))}
              </ul>
            </div>
            <div className="bg-slate-950 p-2 rounded border border-slate-800/80">
              <span className="text-[10px] text-blue-400 font-bold block mb-1">CALCULATED METRICS</span>
              <ul className="space-y-1 text-slate-400">
                {response.calculated_metrics.map((m, i) => (
                  <li key={i}>• {m}</li>
                ))}
              </ul>
            </div>
            <div className="bg-slate-950 p-2 rounded border border-slate-800/80">
              <span className="text-[10px] text-amber-400 font-bold block mb-1">INTERPRETATION</span>
              <ul className="space-y-1 text-slate-400">
                {response.interpretation.map((p, i) => (
                  <li key={i}>• {p}</li>
                ))}
              </ul>
            </div>
          </div>

          {/* Citations */}
          {response.citations.length > 0 && (
            <div className="p-2.5 bg-slate-950/60 border border-slate-800 rounded">
              <span className="text-[10px] text-slate-500 font-bold block mb-1">TRACED CITATIONS</span>
              {response.citations.map((c, i) => (
                <div key={i} className="text-[10px] text-slate-400 italic">
                  [{c.source_type}] "{c.snippet}" (Relevance: {(c.relevance_score * 100).toFixed(0)}%)
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export const AICompanySummaryPanel: React.FC<PanelProps> = ({ symbol = 'AAPL' }) => {
  return (
    <div className="space-y-2 font-mono text-xs">
      <div className="flex items-center space-x-1.5 border-b border-slate-800 pb-1.5 text-slate-300">
        <Sparkles className="h-3.5 w-3.5 text-emerald-400" />
        <span className="font-bold">{symbol} Executive AI Summary</span>
      </div>
      <div className="p-3 bg-slate-950 border border-slate-800 rounded text-slate-300 space-y-2">
        <p>Apple Inc. demonstrates robust quarterly fundamentals supported by strong operating cash flows ($110.54B) and $383.28B total revenue.</p>
        <div className="text-[10px] text-slate-500 border-t border-slate-900 pt-1">Traceable Source: 2024 10-K & Income Statements</div>
      </div>
    </div>
  );
};

export const AINewsSummaryPanel: React.FC<PanelProps> = ({ symbol = 'AAPL' }) => {
  return (
    <div className="space-y-2 font-mono text-xs">
      <div className="flex items-center space-x-1.5 border-b border-slate-800 pb-1.5 text-slate-300">
        <FileText className="h-3.5 w-3.5 text-blue-400" />
        <span className="font-bold">{symbol} AI News Synthesis</span>
      </div>
      <div className="p-3 bg-slate-950 border border-slate-800 rounded text-slate-300 space-y-1.5">
        <span className="text-[10px] text-blue-400 font-bold block">KEY THEMES</span>
        <p className="text-slate-400">• Institutional investors highlighting expansion in services division margins.</p>
        <p className="text-slate-400">• Global supply chain optimization improving product gross margins.</p>
      </div>
    </div>
  );
};

export const AIFilingAnalysisPanel: React.FC<PanelProps> = () => {
  return (
    <div className="space-y-2 font-mono text-xs">
      <div className="flex items-center space-x-1.5 border-b border-slate-800 pb-1.5 text-slate-300">
        <FileText className="h-3.5 w-3.5 text-amber-400" />
        <span className="font-bold">SEC 10-Q/10-K AI Filing Extractor</span>
      </div>
      <div className="p-3 bg-slate-950 border border-slate-800 rounded text-slate-400">
        Upload or select an indexed filing above to automatically extract risk factors, management discussions, and capital commitments with paragraph citations.
      </div>
    </div>
  );
};
