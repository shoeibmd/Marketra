import React, { useEffect, useState } from 'react';
import { api, FinancialEventItem } from '../../../lib/api';
import { PanelProps } from '../../../types/panel';
import { Calendar, Layers, Sparkles, Building, ChevronRight, X } from 'lucide-react';

export const EventIntelligencePanel: React.FC<PanelProps> = () => {
  const [events, setEvents] = useState<FinancialEventItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedEvent, setSelectedEvent] = useState<FinancialEventItem | null>(null);

  useEffect(() => {
    let isMounted = true;
    api.getEvents(1, 10).then((res) => {
      if (isMounted) {
        setEvents(res.items);
        setLoading(false);
      }
    }).catch(() => setLoading(false));
    return () => {
      isMounted = false;
    };
  }, []);

  if (loading) {
    return <div className="text-slate-500 animate-pulse p-4 text-center font-mono text-xs">Loading Financial Events...</div>;
  }

  return (
    <div className="space-y-3 font-mono text-xs h-full flex flex-col">
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center space-x-1.5 text-emerald-400 font-bold">
          <Sparkles className="h-4 w-4" />
          <span className="text-slate-100 text-sm">TODAY'S FINANCIAL EVENTS</span>
        </div>
        <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-bold">
          Structured Feed
        </span>
      </div>

      <div className="space-y-2 flex-1 overflow-y-auto pr-1">
        {events.map((ev) => (
          <div
            key={ev.id}
            onClick={() => setSelectedEvent(ev)}
            className="p-2.5 bg-slate-950 border border-slate-800 hover:border-slate-700 rounded-lg cursor-pointer transition-all space-y-1.5"
          >
            <div className="flex items-center justify-between text-[10px]">
              <span className="bg-emerald-950 text-emerald-300 border border-emerald-800 px-1.5 py-0.5 rounded font-bold">
                {ev.event_type}
              </span>
              <span className="text-slate-500">{new Date(ev.event_date).toLocaleDateString()}</span>
            </div>
            <h4 className="font-bold text-slate-100 text-xs leading-snug">{ev.event_title}</h4>
            <p className="text-slate-400 text-[11px] line-clamp-2">{ev.event_summary}</p>
          </div>
        ))}
      </div>

      {selectedEvent && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl w-full max-w-xl p-4 space-y-3 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <span className="font-bold text-emerald-400">{selectedEvent.event_type} DETAILS</span>
              <button onClick={() => setSelectedEvent(null)} className="p-1 hover:bg-slate-800 rounded text-slate-400">
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="space-y-2 text-slate-300 text-xs">
              <h3 className="font-bold text-slate-100">{selectedEvent.event_title}</h3>
              <p className="bg-slate-950 p-2.5 rounded border border-slate-800 leading-relaxed">{selectedEvent.event_summary}</p>

              <div>
                <strong className="text-slate-400 text-[10px] block mb-1">FACT VS AI ANALYSIS:</strong>
                <div className="p-2 bg-slate-950 border border-slate-800 rounded text-[11px] space-y-1">
                  <p><strong className="text-emerald-400">VERIFIED FACT:</strong> {selectedEvent.event_title}</p>
                  <p><strong className="text-slate-400">AI ANALYSIS:</strong> {selectedEvent.ai_analysis?.analysis || 'Structured event classification'}</p>
                  <p><strong className="text-amber-400">UNCERTAINTY:</strong> {selectedEvent.uncertainties?.uncertainties?.[0] || 'Long-term financial guidance omitted.'}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export const CompanyTimelinePanel: React.FC<PanelProps> = ({ symbol = 'RELIANCE' }) => {
  const [timeline, setTimeline] = useState<Array<{ id: string; date: string; event_type: string; title: string; summary: string }>>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    api.getCompanyTimeline(symbol).then((res) => {
      if (isMounted) {
        setTimeline(res.timeline);
        setLoading(false);
      }
    }).catch(() => setLoading(false));
    return () => {
      isMounted = false;
    };
  }, [symbol]);

  if (loading) {
    return <div className="text-slate-500 animate-pulse p-4 text-center font-mono text-xs">Loading {symbol} Timeline...</div>;
  }

  return (
    <div className="space-y-3 font-mono text-xs h-full flex flex-col">
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center space-x-1.5 text-emerald-400 font-bold">
          <Calendar className="h-4 w-4" />
          <span className="text-slate-100">{symbol} Historical Timeline</span>
        </div>
        <span className="text-[10px] bg-slate-800 text-emerald-400 px-2 py-0.5 rounded font-bold">{symbol}</span>
      </div>

      <div className="space-y-2 flex-1 overflow-y-auto pr-1">
        {timeline.map((item) => (
          <div key={item.id} className="flex items-start space-x-2 border-l-2 border-emerald-500 pl-3 py-1">
            <div>
              <div className="flex items-center space-x-2 text-[10px]">
                <span className="text-slate-500">{new Date(item.date).toLocaleDateString()}</span>
                <span className="bg-slate-800 text-emerald-400 px-1.5 py-0.2 rounded font-bold">{item.event_type}</span>
              </div>
              <h5 className="font-bold text-slate-200 mt-0.5">{item.title}</h5>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export const RelatedCompaniesPanel: React.FC<PanelProps> = ({ symbol = 'RELIANCE' }) => {
  const [relations, setRelations] = useState<Array<{ symbol: string; company_name: string; role: string; note: string }>>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    api.getCompanyRelationships(symbol).then((res) => {
      if (isMounted) {
        setRelations(res.related_companies);
        setLoading(false);
      }
    }).catch(() => setLoading(false));
    return () => {
      isMounted = false;
    };
  }, [symbol]);

  if (loading) {
    return <div className="text-slate-500 animate-pulse p-4 text-center font-mono text-xs">Loading Related Companies...</div>;
  }

  return (
    <div className="space-y-3 font-mono text-xs h-full flex flex-col">
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center space-x-1.5 text-emerald-400 font-bold">
          <Building className="h-4 w-4" />
          <span className="text-slate-100">{symbol} Evidenced Network</span>
        </div>
      </div>

      <div className="space-y-2 flex-1 overflow-y-auto pr-1">
        {relations.length === 0 ? (
          <p className="text-slate-500 text-center py-4">No evidenced company relationships recorded yet.</p>
        ) : (
          relations.map((r, idx) => (
            <div key={idx} className="p-2 bg-slate-950 border border-slate-800 rounded flex items-center justify-between">
              <div>
                <strong className="text-slate-200 font-bold block">{r.company_name} ({r.symbol})</strong>
                <span className="text-slate-500 text-[10px]">{r.note}</span>
              </div>
              <span className="bg-slate-800 text-emerald-400 px-2 py-0.5 rounded text-[10px] font-bold">{r.role}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
