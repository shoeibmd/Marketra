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

export interface NewsArticle {
  id: string;
  instrument_id?: string;
  source_name: string;
  title: string;
  summary?: string;
  content?: string;
  url: string;
  published_at: string;
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
