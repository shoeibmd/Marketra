import React, { useEffect, useState } from 'react';
import { api } from '../../../lib/api';
import { PanelProps } from '../../../types/panel';
import { ShieldCheck, TrendingUp, Download, CheckCircle2, AlertCircle, RefreshCw, BarChart2 } from 'lucide-react';

export const PortfolioRiskCommandCenterPanel: React.FC<PanelProps> = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);

  const fetchCommandCenter = async () => {
    setLoading(true);
    try {
      const res = await api.getRiskCommandCenterData();
      setData(res);
    } catch (err) {
      console.error('Failed to load command center:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCommandCenter();
  }, []);

  const handleExportReport = async () => {
    setExporting(true);
    try {
      const res = await api.exportRiskCommandCenterReport();
      const blob = new Blob([res.markdown_content], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Portfolio_Risk_Report_${new Date().toISOString().slice(0, 10)}.md`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to export report:', err);
    } finally {
      setExporting(false);
    }
  };

  if (loading) return <div className="text-slate-500 animate-pulse p-4 text-center font-mono text-xs">Loading Portfolio Risk Command Center...</div>;
  if (!data) return <div className="text-slate-500 p-4 text-center font-mono text-xs">Command Center Data Unavailable</div>;

  const exec = data.executive_summary || {};

  return (
    <div className="space-y-3 font-mono text-xs text-slate-200">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-slate-400">
        <div className="flex items-center space-x-1.5">
          <ShieldCheck className="h-4 w-4 text-emerald-400" />
          <span className="font-bold text-slate-100 text-sm">Portfolio Risk Command Center</span>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={handleExportReport}
            disabled={exporting}
            className="bg-indigo-950 hover:bg-indigo-900 border border-indigo-800 text-indigo-300 px-2.5 py-1 rounded text-[10px] font-bold flex items-center space-x-1 transition-colors"
          >
            <Download className="h-3 w-3" />
            <span>{exporting ? 'Exporting...' : 'Export Report'}</span>
          </button>
          <button onClick={fetchCommandCenter} className="p-1 hover:bg-slate-800 text-slate-400 rounded">
            <RefreshCw className="h-3 w-3" />
          </button>
        </div>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-4 gap-2">
        <div className="bg-slate-950 p-2 rounded border border-slate-800">
          <span className="text-[10px] text-slate-500 block">TOTAL EQUITY</span>
          <span className="text-sm font-bold text-slate-100">₹{exec.portfolio_value?.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
        </div>
        <div className="bg-slate-950 p-2 rounded border border-slate-800">
          <span className="text-[10px] text-slate-500 block">TOTAL RETURN</span>
          <span className={`text-sm font-bold ${exec.total_return_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            {exec.total_return_pct >= 0 ? '+' : ''}{exec.total_return_pct}%
          </span>
        </div>
        <div className="bg-slate-950 p-2 rounded border border-slate-800">
          <span className="text-[10px] text-slate-500 block">MAX DRAWDOWN</span>
          <span className="text-sm font-bold text-red-400">{exec.current_drawdown_pct}%</span>
        </div>
        <div className="bg-slate-950 p-2 rounded border border-slate-800">
          <span className="text-[10px] text-slate-500 block">HISTORICAL VaR (95%)</span>
          <span className="text-sm font-bold text-amber-400">{exec.historical_var_95_pct}%</span>
        </div>
      </div>

      <p className="text-[9px] text-slate-600 italic">
        Analytical information only. Historical and hypothetical metrics do not guarantee future portfolio performance.
      </p>
    </div>
  );
};

export const PortfolioPerformanceSummaryPanel: React.FC<PanelProps> = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPerf = async () => {
      try {
        const res = await api.getRiskCommandCenterData();
        setData(res.performance_vs_benchmark || {});
      } catch (err) {
        console.error('Failed to load performance:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchPerf();
  }, []);

  if (loading) return <div className="text-slate-500 animate-pulse p-4 text-center font-mono text-xs">Loading Performance vs Benchmarks...</div>;

  return (
    <div className="space-y-3 font-mono text-xs text-slate-200">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-slate-400">
        <div className="flex items-center space-x-1.5">
          <TrendingUp className="h-3.5 w-3.5 text-emerald-400" />
          <span className="font-bold text-slate-200">Performance vs NIFTY50 & SENSEX</span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-center text-[10px] border-collapse">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400">
              <th className="p-1 text-left">PERIOD</th>
              <th className="p-1">PORTFOLIO</th>
              <th className="p-1">NIFTY50</th>
              <th className="p-1">SENSEX</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(data || {}).map(([period, row]: [string, any]) => (
              <tr key={period} className="border-b border-slate-800/40">
                <td className="p-1 font-bold text-left text-slate-300">{period}</td>
                <td className={`p-1 font-bold ${row.portfolio_return_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                  {row.portfolio_return_pct}%
                </td>
                <td className="p-1 text-slate-400">{row.nifty50_return_pct}%</td>
                <td className="p-1 text-slate-400">{row.sensex_return_pct}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export const PortfolioDataQualityPanel: React.FC<PanelProps> = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDQ = async () => {
      try {
        const res = await api.getRiskCommandCenterData();
        setData(res.data_quality_center || {});
      } catch (err) {
        console.error('Failed to load data quality:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDQ();
  }, []);

  if (loading) return <div className="text-slate-500 animate-pulse p-4 text-center font-mono text-xs">Loading Data Quality Center...</div>;

  return (
    <div className="space-y-3 font-mono text-xs text-slate-200">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-slate-400">
        <div className="flex items-center space-x-1.5">
          <BarChart2 className="h-3.5 w-3.5 text-cyan-400" />
          <span className="font-bold text-slate-200">Data Quality & Telemetry Center</span>
        </div>
      </div>

      <div className="space-y-1.5">
        <div className="p-2 bg-slate-950 border border-slate-800 rounded flex justify-between items-center text-[10px]">
          <span className="text-slate-400 font-bold">OVERALL DATA STATUS</span>
          <span className="text-emerald-400 font-bold flex items-center space-x-1">
            <CheckCircle2 className="h-3 w-3" />
            <span>{data?.overall_status || 'AVAILABLE'}</span>
          </span>
        </div>
        <div className="p-2 bg-slate-950 border border-slate-800 rounded flex justify-between items-center text-[10px]">
          <span className="text-slate-400">VaR DATA OBSERVATIONS</span>
          <span className="text-slate-200">{data?.var_data_status || 'AVAILABLE'}</span>
        </div>
        <div className="p-2 bg-slate-950 border border-slate-800 rounded flex justify-between items-center text-[10px]">
          <span className="text-slate-400">CORRELATION BARS</span>
          <span className="text-slate-200">{data?.correlation_data_status || 'AVAILABLE'}</span>
        </div>
      </div>
    </div>
  );
};
