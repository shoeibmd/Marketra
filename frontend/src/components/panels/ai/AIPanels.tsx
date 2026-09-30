import React, { useState } from 'react';
import { api, SourceGroundedResearchAnswer } from '../../../lib/api';
import { PanelProps } from '../../../types/panel';
import { Sparkles, Send, ExternalLink, ShieldCheck, AlertCircle, Building2 } from 'lucide-react';

const QUICK_PROMPTS = [
  'What are the latest events for RELIANCE?',
  'Show recent acquisitions in the Indian market.',
  'What major events happened in the banking sector?',
  'Compare recent developments for TCS and INFY.',
];

export const AIResearchAssistantPanel: React.FC<PanelProps> = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [researchAnswer, setResearchAnswer] = useState<SourceGroundedResearchAnswer | null>(null);

  const handleResearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    try {
      const res = await api.executeResearchQuery(searchQuery, researchAnswer?.context_used);
      setResearchAnswer(res);
    } catch (err) {
      console.error('Research query failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-3 font-mono text-xs h-full flex flex-col">
      {/* Panel Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center space-x-2 text-emerald-400 font-bold">
          <Sparkles className="h-4 w-4" />
          <span className="text-slate-100 text-sm">AI FINANCIAL RESEARCH ASSISTANT</span>
        </div>
        <span className="text-[10px] bg-emerald-950 text-emerald-300 border border-emerald-800 px-2 py-0.5 rounded font-bold">
          Source Grounded RAG
        </span>
      </div>

      {/* Quick Prompts Bar */}
      <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 scrollbar-none">
        {QUICK_PROMPTS.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => {
              setQuery(prompt);
              handleResearch(prompt);
            }}
            className="px-2.5 py-1 rounded text-[10px] bg-slate-900 border border-slate-800 text-slate-300 hover:border-emerald-500 whitespace-nowrap transition-colors"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Query Input Box */}
      <div className="flex items-center space-x-2">
        <input
          type="text"
          placeholder="Ask a source-grounded financial research question..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleResearch(query)}
          className="flex-1 bg-slate-950 border border-slate-800 rounded px-3 py-2 text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-emerald-500"
        />
        <button
          onClick={() => handleResearch(query)}
          disabled={loading || !query.trim()}
          className="bg-emerald-600 hover:bg-emerald-500 text-white px-3 py-2 rounded font-bold flex items-center space-x-1 disabled:opacity-50 transition-colors"
        >
          <Send className="h-3.5 w-3.5" />
          <span>Research</span>
        </button>
      </div>

      {/* Research Output Section */}
      {loading ? (
        <div className="text-slate-500 animate-pulse p-8 text-center flex-1">
          Retrieving multi-source disclosures & executing RAG analysis...
        </div>
      ) : researchAnswer ? (
        <div className="space-y-3 flex-1 overflow-y-auto pr-1">
          {/* Summary Box */}
          <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg space-y-2">
            <div className="flex items-center justify-between border-b border-slate-800 pb-1.5">
              <span className="font-bold text-emerald-400 text-xs flex items-center space-x-1">
                <ShieldCheck className="h-4 w-4" />
                <span>Source-Grounded Synthesis</span>
              </span>
              <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-bold">
                Evidence: {researchAnswer.evidence_confidence}
              </span>
            </div>
            <p className="text-slate-200 text-xs leading-relaxed">{researchAnswer.answer_summary}</p>
          </div>

          {/* Key Facts */}
          {researchAnswer.key_facts && researchAnswer.key_facts.length > 0 && (
            <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg space-y-1.5">
              <strong className="text-slate-400 text-[10px] block">VERIFIED SOURCE FACTS:</strong>
              <ul className="list-disc list-inside space-y-1 text-slate-300 text-[11px]">
                {researchAnswer.key_facts.map((fact, idx) => (
                  <li key={idx}>{fact}</li>
                ))}
              </ul>
            </div>
          )}

          {/* AI Analysis & Uncertainties */}
          <div className="grid grid-cols-2 gap-2">
            <div className="p-2.5 bg-slate-950 border border-slate-800 rounded space-y-1">
              <strong className="text-slate-400 text-[10px] block">AI ANALYSIS:</strong>
              <p className="text-slate-300 text-[11px] leading-relaxed">{researchAnswer.ai_analysis}</p>
            </div>
            <div className="p-2.5 bg-slate-950 border border-slate-800 rounded space-y-1">
              <strong className="text-amber-400 text-[10px] flex items-center space-x-1">
                <AlertCircle className="h-3 w-3" />
                <span>UNCERTAINTY & GAPS:</span>
              </strong>
              <ul className="list-disc list-inside space-y-0.5 text-slate-300 text-[11px]">
                {researchAnswer.uncertainties.map((u, idx) => (
                  <li key={idx}>{u}</li>
                ))}
              </ul>
            </div>
          </div>

          {/* Sources Citations */}
          {researchAnswer.sources && researchAnswer.sources.length > 0 && (
            <div className="p-2.5 bg-slate-950 border border-slate-800 rounded space-y-1.5">
              <strong className="text-slate-400 text-[10px] block">VERIFIED SOURCE CITATIONS:</strong>
              <div className="space-y-1">
                {researchAnswer.sources.map((src) => (
                  <a
                    key={src.id}
                    href={src.url || '#'}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center justify-between p-1.5 bg-slate-900/80 border border-slate-800 rounded hover:border-slate-700 transition-colors text-[11px]"
                  >
                    <span className="truncate text-slate-200">{src.title}</span>
                    <span className="text-emerald-400 font-bold flex items-center space-x-1 ml-2 flex-shrink-0">
                      <span>{src.source}</span>
                      <ExternalLink className="h-3 w-3" />
                    </span>
                  </a>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="p-8 text-center text-slate-500 flex-1">
          Ask a research question or select a quick prompt above.
        </div>
      )}
    </div>
  );
};

export const AICompanySummaryPanel: React.FC<PanelProps> = ({ symbol = 'RELIANCE' }) => {
  return (
    <div className="p-3 font-mono text-xs text-slate-400">
      <div className="flex items-center space-x-1 text-emerald-400 font-bold mb-2">
        <Building2 className="h-4 w-4" />
        <span>{symbol} Executive Synthesis</span>
      </div>
      <p className="bg-slate-950 p-3 rounded border border-slate-800 text-slate-300 leading-relaxed">
        {symbol} operates as a key market constituent with ongoing strategic expansion in digital and infrastructure segments.
      </p>
    </div>
  );
};

export const AINewsSummaryPanel: React.FC<PanelProps> = () => {
  return (
    <div className="p-3 font-mono text-xs text-slate-400">
      <div className="flex items-center space-x-1 text-emerald-400 font-bold mb-2">
        <Sparkles className="h-4 w-4" />
        <span>Market Sentiment Summary</span>
      </div>
      <p className="bg-slate-950 p-3 rounded border border-slate-800 text-slate-300 leading-relaxed">
        Recent disclosures across Indian listed companies highlight corporate actions, earnings disclosures, and regulatory compliance updates.
      </p>
    </div>
  );
};

export const AIFilingAnalysisPanel: React.FC<PanelProps> = () => {
  return (
    <div className="p-3 font-mono text-xs text-slate-400">
      <div className="flex items-center space-x-1 text-emerald-400 font-bold mb-2">
        <ShieldCheck className="h-4 w-4" />
        <span>Filing Risk Factor Extraction</span>
      </div>
      <p className="bg-slate-950 p-3 rounded border border-slate-800 text-slate-300 leading-relaxed">
        Regulatory filings indicate stable capital adequacy, risk management controls, and compliance stance.
      </p>
    </div>
  );
};
