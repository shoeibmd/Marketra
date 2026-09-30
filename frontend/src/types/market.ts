export interface Instrument {
  id: string;
  symbol: string;
  exchange_code: string;
  name: string;
  isin?: string;
  currency: string;
  instrument_type: string;
  provider_symbol: string;
}

export interface Quote {
  timestamp: string;
  instrument_id: string;
  bid_price: number;
  bid_size: number;
  ask_price: number;
  ask_size: number;
  last_price: number;
  last_size: number;
}

export interface OHLCV {
  timestamp: string;
  instrument_id: string;
  interval: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface Fundamental {
  instrument_id: string;
  market_cap?: number;
  pe_ratio?: number;
  pb_ratio?: number;
  dividend_yield?: number;
  eps?: number;
  beta?: number;
  high_52_week?: number;
  low_52_week?: number;
}

export interface MarketContextData {
  symbol: string;
  company_name: string;
  currency: string;
  current_price: number;
  previous_close: number;
  change_percent: number;
  volume: number;
  sector: string;
  market_relevance_note: string;
  high_52_week?: number;
  low_52_week?: number;
}

export interface NewsAIAnalysisData {
  what_happened: string;
  primary_company_affected: string;
  related_companies: string[];
  event_category: string;
  importance_reason: string;
  source_facts: string[];
  potential_impact: 'POSITIVE' | 'NEGATIVE' | 'MIXED' | 'NEUTRAL' | 'UNCLEAR';
  importance_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  ai_confidence: number;
  user_monitoring_checklist: string[];
  related_sector: string;
  related_announcements: string[];
  uncertainties_or_gaps: string[];
  model_used: string;
}

export interface NewsArticle {
  id: string;
  instrument_id?: string;
  source_name: string;
  source_url?: string;
  title: string;
  summary?: string;
  content?: string;
  url: string;
  published_at: string;
  discovered_at?: string;
  company?: string;
  symbol?: string;
  exchange?: string;
  category?: string;
  associated_symbols?: string[];
  ai_status?: string;
  ai_importance?: string;
  ai_impact?: string;
  ai_analysis?: NewsAIAnalysisData;
  market_context?: MarketContextData;
  related_market_contexts?: MarketContextData[];
}

export interface Position {
  symbol: string;
  name: string;
  quantity: number;
  average_buy_price: number;
  current_price: number;
  market_value: number;
  unrealized_pnl: number;
  unrealized_pnl_percent: number;
}

export interface PortfolioSummary {
  portfolio_name: string;
  currency: string;
  cash_balance: number;
  total_market_value: number;
  total_pnl: number;
  total_pnl_percent: number;
  positions_count: number;
}
