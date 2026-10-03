import { panelRegistry } from './lib/panelRegistry';
import {
  GainersLosersPanel,
  MarketOverviewPanel,
  MostActivePanel,
  WatchlistPanel,
} from './components/panels/market/MarketPanels';
import {
  MACDPanel,
  OHLCChartPanel,
  RSIPanel,
  VolumePanel,
  VWAPPanel,
} from './components/panels/charts/ChartPanels';
import {
  CompanyNewsPanel,
  MarketNewsPanel,
  NewsSearchPanel,
} from './components/panels/news/NewsPanels';
import {
  CompanyProfilePanel,
  FinancialStatementsPanel,
  KeyRatiosPanel,
} from './components/panels/fundamentals/FundamentalPanels';
import {
  AddTransactionPanel,
  HoldingsPanel,
  PortfolioAnalyticsPanel,
  PortfolioSummaryPanel,
  TransactionHistoryPanel,
} from './components/panels/portfolio/PortfolioPanels';
import {
  AICompanySummaryPanel,
  AIFilingAnalysisPanel,
  AINewsSummaryPanel,
  AIResearchAssistantPanel,
} from './components/panels/ai/AIPanels';
import { SystemStatusPanel } from './components/panels/admin/SystemStatusPanel';
import {
  CompanyTimelinePanel,
  EventIntelligencePanel,
  RelatedCompaniesPanel,
} from './components/panels/events/EventPanels';
import { PersonalizedWatchlistPanel } from './components/panels/watchlist/WatchlistPanels';
import {
  PortfolioCorrelationPanel,
  PortfolioDiversificationPanel,
  PortfolioRiskContributionPanel,
  PortfolioRiskOverviewPanel,
  PortfolioStressTestPanel,
} from './components/panels/risk/PortfolioRiskPanels';
import {
  PortfolioRiskAlertsPanel,
  PortfolioRiskAlertSettingsPanel,
  PortfolioRiskHistoryPanel,
} from './components/panels/risk/PortfolioRiskAlertPanels';
import {
  PortfolioDataQualityPanel,
  PortfolioPerformanceSummaryPanel,
  PortfolioRiskCommandCenterPanel,
} from './components/panels/risk/PortfolioRiskCommandCenterPanels';
import {
  PortfolioBriefingPanel,
  PortfolioBriefingSettingsPanel,
  PortfolioChangeTimelinePanel,
} from './components/panels/briefings/PortfolioBriefingPanels';
import {
  DuplicateExposurePanel,
  MultiPortfolioOverviewPanel,
  PortfolioAttributionPanel,
  PortfolioComparisonPanel,
} from './components/panels/portfolio/MultiPortfolioPanels';
import {
  MarketAnomaliesPanel,
  MarketBreadthPanel,
  MarketIntelligenceCommandCenterPanel,
  MarketRegimePanel,
  SectorIntelligencePanel,
} from './components/panels/market/MarketIntelligencePanels';
import './components/panels/analytics/AnalyticsPanels';
import './components/panels/paper/PaperTradingPanels';
import './components/panels/trading/TradingPanels';

export function registerDefaultPanels() {
  // Phase 11 - Market Panels
  panelRegistry.register({
    type: 'overview',
    title: 'Market Overview',
    description: 'Major indices, market breadth, and sector performance',
    category: 'Market',
    defaultWidth: 4,
    defaultHeight: 3,
    component: MarketOverviewPanel,
  });

  panelRegistry.register({
    type: 'watchlist',
    title: 'Live Watchlist',
    description: 'Tracked instruments with streaming quotes',
    category: 'Market',
    defaultWidth: 4,
    defaultHeight: 3,
    component: WatchlistPanel,
  });

  panelRegistry.register({
    type: 'personal_watchlist',
    title: 'Personalized Watchlists & Smart Alerts',
    description: 'Manage personal multi-watchlists with tailored smart event notifications',
    category: 'Market',
    defaultWidth: 6,
    defaultHeight: 4,
    component: PersonalizedWatchlistPanel,
  });

  panelRegistry.register({
    type: 'gainers_losers',
    title: 'Gainers & Losers',
    description: 'Top market movers by percentage change',
    category: 'Market',
    defaultWidth: 4,
    defaultHeight: 3,
    component: GainersLosersPanel,
  });

  panelRegistry.register({
    type: 'market_intelligence_command_center',
    title: 'Market Intelligence Command Center',
    description: 'Market-wide indices, market breadth, sector performance, and regime cockpit',
    category: 'Market',
    defaultWidth: 8,
    defaultHeight: 4,
    component: MarketIntelligenceCommandCenterPanel,
  });

  panelRegistry.register({
    type: 'market_breadth_panel',
    title: 'Market Breadth Meter',
    description: 'Advances, declines, A/D volume, and breadth percentages',
    category: 'Market',
    defaultWidth: 4,
    defaultHeight: 3,
    component: MarketBreadthPanel,
  });

  panelRegistry.register({
    type: 'sector_intelligence',
    title: 'Sector Performance Matrix',
    description: 'Sector returns, volatility, and sector correlation matrix',
    category: 'Market',
    defaultWidth: 6,
    defaultHeight: 3,
    component: SectorIntelligencePanel,
  });

  panelRegistry.register({
    type: 'market_regime',
    title: 'Market Regime Classification',
    description: 'Historical market regime classification and volatility regime',
    category: 'Market',
    defaultWidth: 4,
    defaultHeight: 3,
    component: MarketRegimePanel,
  });

  panelRegistry.register({
    type: 'market_anomalies',
    title: 'Market Anomaly Radar',
    description: 'Statistically detected unusual market price/volume shocks',
    category: 'Market',
    defaultWidth: 6,
    defaultHeight: 3,
    component: MarketAnomaliesPanel,
  });

  panelRegistry.register({
    type: 'most_active',
    title: 'Most Active',
    description: 'Highest volume traded instruments',
    category: 'Market',
    defaultWidth: 4,
    defaultHeight: 3,
    component: MostActivePanel,
  });

  // Phase 12 - Chart Panels
  panelRegistry.register({
    type: 'chart',
    title: 'OHLC Candlestick Chart',
    description: 'Candlestick price chart with timeframe selector',
    category: 'Charts',
    defaultWidth: 8,
    defaultHeight: 4,
    component: OHLCChartPanel,
  });

  panelRegistry.register({
    type: 'volume',
    title: 'Volume Histogram',
    description: 'Realtime volume bars synchronized with market action',
    category: 'Charts',
    defaultWidth: 4,
    defaultHeight: 2,
    component: VolumePanel,
  });

  panelRegistry.register({
    type: 'rsi',
    title: 'RSI Indicator',
    description: 'Relative Strength Index (14-period)',
    category: 'Charts',
    defaultWidth: 4,
    defaultHeight: 2,
    component: RSIPanel,
  });

  panelRegistry.register({
    type: 'macd',
    title: 'MACD Indicator',
    description: 'Moving Average Convergence Divergence',
    category: 'Charts',
    defaultWidth: 4,
    defaultHeight: 2,
    component: MACDPanel,
  });

  panelRegistry.register({
    type: 'vwap',
    title: 'VWAP Overlay',
    description: 'Volume Weighted Average Price analysis',
    category: 'Charts',
    defaultWidth: 4,
    defaultHeight: 2,
    component: VWAPPanel,
  });

  // Phase 13 - News Panels
  panelRegistry.register({
    type: 'market_news',
    title: 'Market News Feed',
    description: 'Global financial news and headlines',
    category: 'News',
    defaultWidth: 4,
    defaultHeight: 3,
    component: MarketNewsPanel,
  });

  panelRegistry.register({
    type: 'company_news',
    title: 'Company Coverage',
    description: 'Instrument-filtered article feed',
    category: 'News',
    defaultWidth: 4,
    defaultHeight: 3,
    component: CompanyNewsPanel,
  });

  panelRegistry.register({
    type: 'news_search',
    title: 'News Search Archive',
    description: 'Search news by keyword and date',
    category: 'News',
    defaultWidth: 4,
    defaultHeight: 2,
    component: NewsSearchPanel,
  });

  // Phase 10 - Financial Event Intelligence Panels
  panelRegistry.register({
    type: 'event_intelligence',
    title: 'Financial Event Feed',
    description: 'Structured financial event extraction and fact analysis',
    category: 'News',
    defaultWidth: 6,
    defaultHeight: 3,
    component: EventIntelligencePanel,
  });

  panelRegistry.register({
    type: 'company_timeline',
    title: 'Company Event Timeline',
    description: 'Historical event disclosure chronology',
    category: 'News',
    defaultWidth: 4,
    defaultHeight: 3,
    component: CompanyTimelinePanel,
  });

  panelRegistry.register({
    type: 'related_companies',
    title: 'Evidenced Network',
    description: 'Co-mentioned and role-mapped company network',
    category: 'News',
    defaultWidth: 4,
    defaultHeight: 3,
    component: RelatedCompaniesPanel,
  });

  // Phase 7 - Admin / System Status Panel
  panelRegistry.register({
    type: 'system_status',
    title: 'System Health & Compliance',
    description: 'Free/Open-source compliance audit and feed telemetry',
    category: 'Admin',
    defaultWidth: 4,
    defaultHeight: 3,
    component: SystemStatusPanel,
  });

  // Phase 14 - Fundamental Panels
  panelRegistry.register({
    type: 'company_profile',
    title: 'Company Profile',
    description: 'Sector, industry, description, and employee metrics',
    category: 'Fundamentals',
    defaultWidth: 4,
    defaultHeight: 2,
    component: CompanyProfilePanel,
  });

  panelRegistry.register({
    type: 'financial_statements',
    title: 'Financial Statements',
    description: 'Income statement, balance sheet, and cash flow',
    category: 'Fundamentals',
    defaultWidth: 4,
    defaultHeight: 3,
    component: FinancialStatementsPanel,
  });

  panelRegistry.register({
    type: 'key_ratios',
    title: 'Key Valuation Ratios',
    description: 'P/E, P/B, EPS, dividend yield, and beta',
    category: 'Fundamentals',
    defaultWidth: 4,
    defaultHeight: 2,
    component: KeyRatiosPanel,
  });

  // Phase 15 & 25 - Portfolio Risk Panels
  panelRegistry.register({
    type: 'portfolio_risk_overview',
    title: 'Portfolio Risk & VaR Overview',
    description: 'Historical VaR, Expected Shortfall (CVaR), and risk summary',
    category: 'Portfolio',
    defaultWidth: 6,
    defaultHeight: 3,
    component: PortfolioRiskOverviewPanel,
  });

  panelRegistry.register({
    type: 'portfolio_stress_test',
    title: 'Portfolio Stress Testing Simulator',
    description: 'Hypothetical market shocks, sector shocks, and P&L impact analysis',
    category: 'Portfolio',
    defaultWidth: 6,
    defaultHeight: 4,
    component: PortfolioStressTestPanel,
  });

  panelRegistry.register({
    type: 'portfolio_correlation',
    title: 'Holdings Correlation Matrix',
    description: 'Holding-to-holding return correlation and highly correlated pair detection',
    category: 'Portfolio',
    defaultWidth: 6,
    defaultHeight: 4,
    component: PortfolioCorrelationPanel,
  });

  panelRegistry.register({
    type: 'portfolio_diversification',
    title: 'Diversification & HHI Concentration',
    description: 'Sector concentration, Herfindahl-Hirschman index, and diversification score',
    category: 'Portfolio',
    defaultWidth: 4,
    defaultHeight: 3,
    component: PortfolioDiversificationPanel,
  });

  panelRegistry.register({
    type: 'portfolio_risk_contribution',
    title: 'Asset Risk Contribution',
    description: 'Marginal risk contribution by company and sector',
    category: 'Portfolio',
    defaultWidth: 4,
    defaultHeight: 3,
    component: PortfolioRiskContributionPanel,
  });

  panelRegistry.register({
    type: 'portfolio_risk_alerts',
    title: 'Portfolio Risk Alerts Dashboard',
    description: 'Active and historical threshold risk notifications',
    category: 'Portfolio',
    defaultWidth: 6,
    defaultHeight: 4,
    component: PortfolioRiskAlertsPanel,
  });

  panelRegistry.register({
    type: 'portfolio_risk_alert_settings',
    title: 'Risk Threshold Settings',
    description: 'User-configurable risk alert parameters and preferences',
    category: 'Portfolio',
    defaultWidth: 4,
    defaultHeight: 3,
    component: PortfolioRiskAlertSettingsPanel,
  });

  panelRegistry.register({
    type: 'portfolio_risk_command_center',
    title: 'Portfolio Risk Command Center',
    description: 'Executive portfolio risk, performance, alerts, and stress testing cockpit',
    category: 'Portfolio',
    defaultWidth: 8,
    defaultHeight: 4,
    component: PortfolioRiskCommandCenterPanel,
  });

  panelRegistry.register({
    type: 'portfolio_performance_summary',
    title: 'Performance vs NIFTY50 / SENSEX',
    description: 'Period returns compared against major Indian indices',
    category: 'Portfolio',
    defaultWidth: 6,
    defaultHeight: 3,
    component: PortfolioPerformanceSummaryPanel,
  });

  panelRegistry.register({
    type: 'portfolio_data_quality',
    title: 'Data Quality & Telemetry Center',
    description: 'Data-quality statuses and statistical observation counts',
    category: 'Portfolio',
    defaultWidth: 4,
    defaultHeight: 3,
    component: PortfolioDataQualityPanel,
  });

  panelRegistry.register({
    type: 'portfolio_briefing',
    title: 'Portfolio Research Briefing',
    description: 'Daily, pre-market, intraday, and weekly source-grounded research briefings',
    category: 'Portfolio',
    defaultWidth: 6,
    defaultHeight: 4,
    component: PortfolioBriefingPanel,
  });

  panelRegistry.register({
    type: 'portfolio_change_timeline',
    title: 'Real-time Portfolio Change Timeline',
    description: 'Chronological timeline of material portfolio value, risk, and event changes',
    category: 'Portfolio',
    defaultWidth: 6,
    defaultHeight: 3,
    component: PortfolioChangeTimelinePanel,
  });

  panelRegistry.register({
    type: 'multi_portfolio_overview',
    title: 'Multi-Portfolio Overview & Selector',
    description: 'Consolidated multi-account equity summary and portfolio account manager',
    category: 'Portfolio',
    defaultWidth: 6,
    defaultHeight: 4,
    component: MultiPortfolioOverviewPanel,
  });

  panelRegistry.register({
    type: 'portfolio_comparison',
    title: 'Side-by-Side Portfolio Comparison',
    description: 'Factual metrics comparison across user-owned portfolio accounts',
    category: 'Portfolio',
    defaultWidth: 8,
    defaultHeight: 4,
    component: PortfolioComparisonPanel,
  });

  panelRegistry.register({
    type: 'duplicate_exposure',
    title: 'Duplicate Cross-Portfolio Exposure',
    description: 'Identifies overlapping company and sector holdings across portfolios',
    category: 'Portfolio',
    defaultWidth: 6,
    defaultHeight: 3,
    component: DuplicateExposurePanel,
  });

  panelRegistry.register({
    type: 'portfolio_attribution',
    title: 'Performance Attribution',
    description: 'P&L contribution attribution by portfolio account',
    category: 'Portfolio',
    defaultWidth: 6,
    defaultHeight: 3,
    component: PortfolioAttributionPanel,
  });

  panelRegistry.register({
    type: 'portfolio_briefing_settings',
    title: 'Briefing Schedule & Preferences',
    description: 'User delivery schedules and significance threshold preferences',
    category: 'Portfolio',
    defaultWidth: 4,
    defaultHeight: 3,
    component: PortfolioBriefingSettingsPanel,
  });

  panelRegistry.register({
    type: 'portfolio_risk_history',
    title: 'Visual Risk Timeline & History',
    description: 'Historical risk snapshot trend chronology',
    category: 'Portfolio',
    defaultWidth: 6,
    defaultHeight: 3,
    component: PortfolioRiskHistoryPanel,
  });

  panelRegistry.register({
    type: 'portfolio_analytics',
    title: 'Portfolio Risk & Intelligence Analytics',
    description: 'Sharpe/Sortino ratios, max drawdown, sector concentration, and benchmark alpha',
    category: 'Portfolio',
    defaultWidth: 6,
    defaultHeight: 4,
    component: PortfolioAnalyticsPanel,
  });

  panelRegistry.register({
    type: 'portfolio_summary',
    title: 'Portfolio Summary',
    description: 'Total value, daily P&L, and cash balance',
    category: 'Portfolio',
    defaultWidth: 4,
    defaultHeight: 3,
    component: PortfolioSummaryPanel,
  });

  panelRegistry.register({
    type: 'holdings',
    title: 'Asset Holdings',
    description: 'Positions list with market values and unrealized P&L',
    category: 'Portfolio',
    defaultWidth: 6,
    defaultHeight: 3,
    component: HoldingsPanel,
  });

  panelRegistry.register({
    type: 'transaction_history',
    title: 'Transaction History',
    description: 'Execution ledger of buy and sell orders',
    category: 'Portfolio',
    defaultWidth: 6,
    defaultHeight: 3,
    component: TransactionHistoryPanel,
  });

  panelRegistry.register({
    type: 'add_transaction',
    title: 'Record Trade Order',
    description: 'Form to execute buy/sell position records',
    category: 'Portfolio',
    defaultWidth: 4,
    defaultHeight: 3,
    component: AddTransactionPanel,
  });

  // Phase 16 - AI Panels
  panelRegistry.register({
    type: 'ai_research',
    title: 'AI Research Assistant',
    description: 'Chat-style RAG query interface with cited sources',
    category: 'AI',
    defaultWidth: 6,
    defaultHeight: 4,
    component: AIResearchAssistantPanel,
  });

  panelRegistry.register({
    type: 'ai_summary',
    title: 'AI Executive Summary',
    description: 'Auto-generated structured company synthesis',
    category: 'AI',
    defaultWidth: 4,
    defaultHeight: 3,
    component: AICompanySummaryPanel,
  });

  panelRegistry.register({
    type: 'ai_news_summary',
    title: 'AI News Synthesis',
    description: 'Key themes and market sentiment extracted by AI',
    category: 'AI',
    defaultWidth: 4,
    defaultHeight: 3,
    component: AINewsSummaryPanel,
  });

  panelRegistry.register({
    type: 'ai_filing_analysis',
    title: 'AI SEC Filing Analysis',
    description: 'Automatic risk factor and management extractor',
    category: 'AI',
    defaultWidth: 6,
    defaultHeight: 3,
    component: AIFilingAnalysisPanel,
  });
}
