import React, { useEffect, useState } from 'react';
import { PanelProps } from '../../../types/panel';
import { ShieldCheck, Activity, Database, Cpu, Layers } from 'lucide-react';

interface SourceStatus {
  source_name: str;
  source_url: str;
  status: string;
  category: string;
  last_successful_fetch: string;
  last_error?: string;
  articles_processed: number;
  duplicates_detected: number;
}

interface SystemStatusReport {
  overall_status: string;
  free_open_source_compliance: string;
  total_articles_ingested: number;
  total_duplicates_filtered: number;
  ai_processing_status: string;
  sources: SourceStatus[];
  dependency_audit: Record<string, string>;
}

export const SystemStatusPanel: React.FC<PanelProps> = () => {
  const [report, setReport] = useState<SystemStatusReport | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

    fetch(`${API_BASE_URL}/api/v1/news/status`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then((data) => {
        setReport(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load news system status:', err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div className="text-slate-500 animate-pulse p-4 text-center font-mono text-xs">Loading System Audit...</div>;
  }

  return (
    <div className="space-y-4 font-mono text-xs overflow-y-auto h-full pr-1">
      {/* Top Compliance Header */}
      <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <ShieldCheck className="h-5 w-5 text-emerald-400" />
          <div>
            <h3 className="font-bold text-slate-100 text-xs">FREE / OPEN-SOURCE COMPLIANCE AUDIT</h3>
            <span className="text-[10px] text-emerald-400 font-bold block">{report?.free_open_source_compliance}</span>
          </div>
        </div>
        <span className="bg-emerald-950 border border-emerald-800 text-emerald-400 px-2 py-1 rounded text-[10px] font-bold">
          STATUS: {report?.overall_status || 'HEALTHY'}
        </span>
      </div>

      {/* Dependency Categorization Grid */}
      <div className="space-y-2">
        <h4 className="font-bold text-slate-300 text-xs flex items-center space-x-1.5">
          <Layers className="h-3.5 w-3.5 text-emerald-400" />
          <span>Dependency Audit & Classification</span>
        </h4>

        <div className="grid grid-cols-2 gap-2 text-[11px]">
          {report?.dependency_audit &&
            Object.entries(report.dependency_audit).map(([key, val]) => (
              <div key={key} className="p-2 bg-slate-950 border border-slate-800 rounded">
                <span className="text-slate-500 text-[10px] block">{key.toUpperCase()}</span>
                <strong className="text-slate-200">{val}</strong>
              </div>
            ))}
        </div>
      </div>

      {/* Live News Feeds Health */}
      <div className="space-y-2">
        <h4 className="font-bold text-slate-300 text-xs flex items-center space-x-1.5">
          <Activity className="h-3.5 w-3.5 text-emerald-400" />
          <span>Public News Source Feed Telemetry</span>
        </h4>

        <div className="space-y-1.5">
          {report?.sources?.map((src, idx) => (
            <div key={idx} className="p-2 bg-slate-950 border border-slate-800 rounded flex items-center justify-between">
              <div>
                <strong className="text-slate-200 text-xs block">{src.source_name}</strong>
                <span className="text-[10px] text-slate-500">Processed: {src.articles_processed} | Duplicates: {src.duplicates_detected}</span>
              </div>
              <span className="bg-slate-900 border border-slate-800 text-emerald-400 px-2 py-0.5 rounded text-[10px] font-bold">
                {src.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
