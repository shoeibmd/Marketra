import React, { useEffect, useState } from 'react';
import { api } from '../../../lib/api';
import { Fundamental } from '../../../types/market';
import { PanelProps } from '../../../types/panel';
import { Building2, FileText, PieChart } from 'lucide-react';

export const CompanyProfilePanel: React.FC<PanelProps> = ({ symbol = 'AAPL' }) => {
  return (
    <div className="space-y-3 font-mono text-xs">
      <div className="flex items-center space-x-2 border-b border-slate-800 pb-1.5 text-slate-300">
        <Building2 className="h-4 w-4 text-emerald-400" />
        <span className="font-bold">{symbol} Company Profile</span>
      </div>
      <div className="space-y-1.5 text-slate-300 bg-slate-950 p-2.5 rounded border border-slate-800">
        <div className="flex justify-between"><span className="text-slate-500">Sector:</span><span>Technology</span></div>
        <div className="flex justify-between"><span className="text-slate-500">Industry:</span><span>Consumer Electronics</span></div>
        <div className="flex justify-between"><span className="text-slate-500">Employees:</span><span>161,000</span></div>
        <div className="flex justify-between"><span className="text-slate-500">Country:</span><span>United States</span></div>
      </div>
    </div>
  );
};

export const FinancialStatementsPanel: React.FC<PanelProps> = ({ symbol = 'AAPL' }) => {
  const [activeTab, setActiveTab] = useState<'income' | 'balance' | 'cash'>('income');

  return (
    <div className="space-y-3 font-mono text-xs">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1.5">
        <span className="font-bold text-slate-200 flex items-center gap-1">
          <FileText className="h-3.5 w-3.5 text-blue-400" /> {symbol} Statements
        </span>
        <div className="flex space-x-1">
          {(['income', 'balance', 'cash'] as const).map((t) => (
            <button
              key={t}
              onClick={() => setActiveTab(t)}
              className={`px-1.5 py-0.5 text-[10px] rounded uppercase ${
                activeTab === t ? 'bg-blue-950 text-blue-400 font-bold border border-blue-800' : 'text-slate-500'
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      <div className="bg-slate-950 p-3 rounded border border-slate-800 space-y-1.5">
        {activeTab === 'income' && (
          <>
            <div className="flex justify-between"><span className="text-slate-500">Total Revenue:</span><span className="font-bold">$383.28B</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Operating Income:</span><span>$114.30B</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Net Income:</span><span className="text-emerald-400 font-bold">$96.99B</span></div>
          </>
        )}
        {activeTab === 'balance' && (
          <>
            <div className="flex justify-between"><span className="text-slate-500">Total Assets:</span><span>$352.58B</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Total Liabilities:</span><span>$290.43B</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Total Equity:</span><span className="font-bold">$62.14B</span></div>
          </>
        )}
        {activeTab === 'cash' && (
          <>
            <div className="flex justify-between"><span className="text-slate-500">Operating Cash Flow:</span><span>$110.54B</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Capital Expenditures:</span><span>-$10.95B</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Free Cash Flow:</span><span className="text-emerald-400 font-bold">$99.58B</span></div>
          </>
        )}
      </div>
    </div>
  );
};

export const KeyRatiosPanel: React.FC<PanelProps> = ({ symbol = 'AAPL' }) => {
  const [fund, setFund] = useState<Fundamental | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getFundamentals(symbol).then((res) => {
      setFund(res);
      setLoading(false);
    });
  }, [symbol]);

  if (loading) return <div className="text-slate-500 animate-pulse p-4 text-center">Loading Ratios...</div>;

  return (
    <div className="space-y-2 font-mono text-xs">
      <div className="flex items-center space-x-1.5 border-b border-slate-800 pb-1.5 text-slate-400">
        <PieChart className="h-3.5 w-3.5 text-amber-400" />
        <span className="font-bold text-slate-200">{symbol} Valuation Metrics</span>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <div className="bg-slate-950 p-2 rounded border border-slate-800">
          <span className="text-[10px] text-slate-500 block">P/E RATIO</span>
          <span className="font-bold text-slate-100">{fund?.pe_ratio ?? 'N/A'}</span>
        </div>
        <div className="bg-slate-950 p-2 rounded border border-slate-800">
          <span className="text-[10px] text-slate-500 block">P/B RATIO</span>
          <span className="font-bold text-slate-100">{fund?.pb_ratio ?? 'N/A'}</span>
        </div>
        <div className="bg-slate-950 p-2 rounded border border-slate-800">
          <span className="text-[10px] text-slate-500 block">DIV YIELD</span>
          <span className="font-bold text-emerald-400">{fund?.dividend_yield ? `${(fund.dividend_yield * 100).toFixed(2)}%` : 'N/A'}</span>
        </div>
        <div className="bg-slate-950 p-2 rounded border border-slate-800">
          <span className="text-[10px] text-slate-500 block">EPS</span>
          <span className="font-bold text-slate-100">${fund?.eps?.toFixed(2) ?? 'N/A'}</span>
        </div>
      </div>
    </div>
  );
};
