import React, { useEffect, useState } from 'react';
import { api } from '../../../lib/api';
import { PanelProps } from '../../../types/panel';
import { ShieldAlert, Activity, GitCommit, Layers, AlertTriangle, RefreshCw } from 'lucide-react';

export const PortfolioRiskOverviewPanel: React.FC<PanelProps> = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRisk = async () => {
      try {
        const res = await api.getPortfolioRiskSummary();
        setData(res);
      } catch (err) {
        console.error('Failed to load risk summary:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchRisk();
  }, []);

  if (loading) return <div className="text-slate-500 animate-pulse p-4 text-center font-mono text-xs">Loading Portfolio Risk Overview...</div>;
  if (!data) return <div className="text-slate-500 p-4 text-center font-mono text-xs">Risk Summary Unavailable</div>;

  const varData = data.var_and_expected_shortfall;
  const divData = data.diversification;

  return (
    <div className="space-y-3 font-mono text-xs text-slate-200">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-slate-400">
        <div className="flex items-center space-x-1.5">
          <ShieldAlert className="h-3.5 w-3.5 text-red-400" />
          <span className="font-bold text-slate-200">Portfolio Risk & VaR Overview</span>
        </div>
        <span className="text-[10px] bg-slate-900 text-emerald-400 px-1.5 py-0.5 rounded border border-emerald-950 font-semibold">
          {varData?.data_quality_status || 'AVAILABLE'}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-2">
        <div className="bg-slate-950 p-2 rounded border border-slate-800">
          <span className="text-[10px] text-slate-500 block">HISTORICAL VaR (95%)</span>
          <span className="text-sm font-bold text-red-400">{varData?.value_at_risk?.historical_var_pct ?? 0}%</span>
          <span className="text-[10px] text-slate-400 block">₹{varData?.value_at_risk?.historical_var_amount?.toLocaleString() ?? 0}</span>
        </div>
        <div className="bg-slate-950 p-2 rounded border border-slate-800">
          <span className="text-[10px] text-slate-500 block">EXPECTED SHORTFALL (95%)</span>
          <span className="text-sm font-bold text-red-500">{varData?.expected_shortfall?.cvar_expected_shortfall_pct ?? 0}%</span>
          <span className="text-[10px] text-slate-400 block">₹{varData?.expected_shortfall?.cvar_expected_shortfall_amount?.toLocaleString() ?? 0}</span>
        </div>
        <div className="bg-slate-950 p-2 rounded border border-slate-800">
          <span className="text-[10px] text-slate-500 block">DIVERSIFICATION SCORE</span>
          <span className="text-sm font-bold text-indigo-400">{divData?.summary?.diversification_score ?? 0} / 100</span>
          <span className="text-[10px] text-slate-400 block">HHI: {divData?.summary?.hhi_index ?? 0}</span>
        </div>
      </div>

      <p className="text-[9px] text-slate-600 italic">
        VaR and Expected Shortfall are statistical observations based on historical return distributions.
      </p>
    </div>
  );
};

export const PortfolioStressTestPanel: React.FC<PanelProps> = () => {
  const [shockPct, setShockPct] = useState(-5.0);
  const [scenarioName, setScenarioName] = useState('NIFTY50 Market Shock');
  const [result, setResult] = useState<any>(null);
  const [running, setRunning] = useState(false);

  const handleRunStressTest = async () => {
    setRunning(true);
    try {
      const res = await api.runPortfolioStressTest({
        market_shock_pct: shockPct,
        scenario_name: scenarioName,
      });
      setResult(res);
    } catch (err) {
      console.error('Stress test failed:', err);
    } finally {
      setRunning(false);
    }
  };

  useEffect(() => {
    handleRunStressTest();
  }, []);

  return (
    <div className="space-y-3 font-mono text-xs text-slate-200">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-slate-400">
        <div className="flex items-center space-x-1.5">
          <Activity className="h-3.5 w-3.5 text-amber-400" />
          <span className="font-bold text-slate-200">Portfolio Stress Testing Simulator</span>
        </div>
      </div>

      {/* Preset Scenarios Controls */}
      <div className="flex items-center space-x-2">
        <select
          value={shockPct}
          onChange={(e) => setShockPct(Number(e.target.value))}
          className="bg-slate-950 border border-slate-800 text-slate-200 rounded px-2 py-1 text-xs"
        >
          <option value={-10.0}>NIFTY50 -10% Severe Crash</option>
          <option value={-5.0}>NIFTY50 -5% Correction</option>
          <option value={-3.0}>NIFTY50 -3% Moderate Dip</option>
          <option value={-1.0}>NIFTY50 -1% Minor Pullback</option>
          <option value={5.0}>NIFTY50 +5% Market Rally</option>
        </select>
        <button
          onClick={handleRunStressTest}
          disabled={running}
          className="bg-amber-950 hover:bg-amber-900 border border-amber-800 text-amber-400 px-3 py-1 rounded font-bold flex items-center space-x-1 transition-colors"
        >
          <RefreshCw className={`h-3 w-3 ${running ? 'animate-spin' : ''}`} />
          <span>Simulate</span>
        </button>
      </div>

      {result && result.hypothetical_impact && (
        <div className="bg-slate-950 p-2.5 rounded border border-slate-800 space-y-2">
          <div className="flex justify-between items-center text-slate-400 text-[10px]">
            <span>HYPOTHETICAL PORTFOLIO VALUE:</span>
            <span className="font-bold text-slate-100">₹{result.hypothetical_impact.scenario_portfolio_value.toLocaleString()}</span>
          </div>
          <div className="flex justify-between items-center text-slate-400 text-[10px]">
            <span>ESTIMATED P&L IMPACT:</span>
            <span className={`font-bold ${result.hypothetical_impact.absolute_pnl_impact >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
              ₹{result.hypothetical_impact.absolute_pnl_impact.toLocaleString()} ({result.hypothetical_impact.percentage_portfolio_impact}%)
            </span>
          </div>
        </div>
      )}

      <p className="text-[9px] text-slate-600 italic">
        {result?.disclaimer || 'Stress scenarios represent mathematical parallel shocks and do not constitute predictions.'}
      </p>
    </div>
  );
};

export const PortfolioCorrelationPanel: React.FC<PanelProps> = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCorr = async () => {
      try {
        const res = await api.getPortfolioCorrelation();
        setData(res);
      } catch (err) {
        console.error('Failed to load correlation:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchCorr();
  }, []);

  if (loading) return <div className="text-slate-500 animate-pulse p-4 text-center font-mono text-xs">Loading Correlation Matrix...</div>;

  const matrix = data?.holdings_correlation_matrix || {};
  const symbols = Object.keys(matrix);

  return (
    <div className="space-y-3 font-mono text-xs text-slate-200">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-slate-400">
        <div className="flex items-center space-x-1.5">
          <GitCommit className="h-3.5 w-3.5 text-cyan-400" />
          <span className="font-bold text-slate-200">Holdings Return Correlation Matrix</span>
        </div>
      </div>

      {symbols.length < 2 ? (
        <div className="p-3 text-center text-slate-500 text-[11px] bg-slate-950 border border-slate-800 rounded">
          Minimum 2 active position holdings required for correlation matrix.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-center text-[10px] border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="p-1 text-left">SYMBOL</th>
                {symbols.map((s) => (
                  <th key={s} className="p-1">{s}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {symbols.map((s1) => (
                <tr key={s1} className="border-b border-slate-800/40">
                  <td className="p-1 font-bold text-left text-slate-300">{s1}</td>
                  {symbols.map((s2) => {
                    const val = matrix[s1][s2];
                    const isHigh = val >= 0.70 && s1 !== s2;
                    return (
                      <td key={s2} className={`p-1 font-bold ${isHigh ? 'text-amber-400 bg-amber-950/30' : 'text-slate-300'}`}>
                        {val}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export const PortfolioDiversificationPanel: React.FC<PanelProps> = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDiv = async () => {
      try {
        const res = await api.getPortfolioDiversification();
        setData(res);
      } catch (err) {
        console.error('Failed to load diversification:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDiv();
  }, []);

  if (loading) return <div className="text-slate-500 animate-pulse p-4 text-center font-mono text-xs">Loading Diversification Metrics...</div>;

  const conc = data?.concentration || {};

  return (
    <div className="space-y-3 font-mono text-xs text-slate-200">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-slate-400">
        <div className="flex items-center space-x-1.5">
          <Layers className="h-3.5 w-3.5 text-indigo-400" />
          <span className="font-bold text-slate-200">Diversification & Sector Concentration</span>
        </div>
      </div>

      <div className="space-y-1.5">
        <span className="text-[10px] text-slate-400 font-bold">SECTOR ALLOCATION (% TOTAL EQUITY)</span>
        {Object.entries(conc.sector_concentration_pct || {}).map(([sec, pct]) => (
          <div key={sec} className="flex justify-between items-center p-1.5 bg-slate-950 border border-slate-800 rounded text-[10px]">
            <span className="text-slate-300 font-bold">{sec}</span>
            <span className="text-indigo-400 font-bold">{String(pct)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export const PortfolioRiskContributionPanel: React.FC<PanelProps> = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchContrib = async () => {
      try {
        const res = await api.getPortfolioRiskContribution();
        setData(res);
      } catch (err) {
        console.error('Failed to load risk contribution:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchContrib();
  }, []);

  if (loading) return <div className="text-slate-500 animate-pulse p-4 text-center font-mono text-xs">Loading Risk Contribution...</div>;

  const companyContrib = data?.risk_contribution_by_company || [];

  return (
    <div className="space-y-3 font-mono text-xs text-slate-200">
      <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-slate-400">
        <div className="flex items-center space-x-1.5">
          <AlertTriangle className="h-3.5 w-3.5 text-orange-400" />
          <span className="font-bold text-slate-200">Risk Contribution by Asset</span>
        </div>
      </div>

      <div className="space-y-1.5">
        {companyContrib.map((c: any) => (
          <div key={c.symbol} className="flex justify-between items-center p-1.5 bg-slate-950 border border-slate-800 rounded text-[10px]">
            <span className="font-bold text-slate-200">{c.symbol}</span>
            <span className="text-orange-400 font-bold">{c.estimated_risk_contribution_pct}%</span>
          </div>
        ))}
      </div>
    </div>
  );
};
