import {
  Fundamental,
  Instrument,
  NewsArticle,
  OHLCV,
  PortfolioSummary,
  Position,
  Quote,
} from '../types/market';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface MarketOverviewResponse {
  status: string;
  market_status: string;
  indices: Array<{
    symbol: string;
    name: string;
    last_price: number;
    change_percent: number;
  }>;
  gainers: Array<{
    symbol: string;
    name: string;
    last_price: number;
    change_percent: number;
  }>;
  losers: Array<{
    symbol: string;
    name: string;
    last_price: number;
    change_percent: number;
  }>;
}

export interface WatchlistItemResponse {
  symbol: string;
  name: string;
  currency: string;
  quote: Quote;
}

export interface WorkspaceResponse {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  is_default: boolean;
  layout_config: Array<{
    panelId: string;
    panelType: string;
    title: string;
    symbol?: string;
    x: number;
    y: number;
    w: number;
    h: number;
  }>;
  created_at: string;
  updated_at: string;
}

class ApiClient {
  private getHeaders(): HeadersInit {
    const token = localStorage.getItem('auth_token');
    return {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Network request failed' }));
      throw new Error(errorData.detail || `HTTP Error ${response.status}`);
    }

    return response.json();
  }

  // Workspaces Persisted CRUD
  async getWorkspaces(): Promise<WorkspaceResponse[]> {
    return this.request<WorkspaceResponse[]>('/api/v1/workspaces');
  }

  async getWorkspace(id: string): Promise<WorkspaceResponse> {
    return this.request<WorkspaceResponse>(`/api/v1/workspaces/${id}`);
  }

  async createWorkspace(name: string, description?: string, layoutConfig: unknown[] = []): Promise<WorkspaceResponse> {
    return this.request<WorkspaceResponse>('/api/v1/workspaces', {
      method: 'POST',
      body: JSON.stringify({ name, description, layout_config: layoutConfig }),
    });
  }

  async updateWorkspace(id: string, name?: string, layoutConfig?: unknown[]): Promise<WorkspaceResponse> {
    return this.request<WorkspaceResponse>(`/api/v1/workspaces/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ name, layout_config: layoutConfig }),
    });
  }

  async deleteWorkspace(id: string): Promise<{ status: string }> {
    return this.request<{ status: string }>(`/api/v1/workspaces/${id}`, {
      method: 'DELETE',
    });
  }

  // Instruments
  async searchInstruments(query: string): Promise<Instrument[]> {
    return this.request<Instrument[]>(`/api/v1/instruments/search?q=${encodeURIComponent(query)}`);
  }

  async getInstrument(symbolOrId: string): Promise<Instrument> {
    return this.request<Instrument>(`/api/v1/instruments/${encodeURIComponent(symbolOrId)}`);
  }

  async getQuote(symbolOrId: string): Promise<Quote> {
    return this.request<Quote>(`/api/v1/instruments/${encodeURIComponent(symbolOrId)}/quote`);
  }

  // Market
  async getOHLCV(symbol: string, interval = '1d', daysBack = 30): Promise<OHLCV[]> {
    return this.request<OHLCV[]>(`/api/v1/market/ohlcv/${symbol}?interval=${interval}&days_back=${daysBack}`);
  }

  async getMarketOverview(): Promise<MarketOverviewResponse> {
    return this.request<MarketOverviewResponse>('/api/v1/market/overview');
  }

  async getWatchlist(): Promise<WatchlistItemResponse[]> {
    return this.request<WatchlistItemResponse[]>('/api/v1/market/watchlist');
  }

  // Fundamentals & News
  async getFundamentals(symbol: string): Promise<Fundamental> {
    return this.request<Fundamental>(`/api/v1/fundamentals/${symbol}`);
  }

  async getNews(symbol?: string, limit = 10): Promise<NewsArticle[]> {
    const url = symbol ? `/api/v1/news?symbol=${symbol}&limit=${limit}` : `/api/v1/news?limit=${limit}`;
    return this.request<NewsArticle[]>(url);
  }

  // Portfolio
  async getPortfolio(): Promise<{ portfolio_name: string; cash_balance: number; positions: Position[] }> {
    return this.request<{ portfolio_name: string; cash_balance: number; positions: Position[] }>('/api/v1/portfolio');
  }

  async getPortfolioSummary(): Promise<PortfolioSummary> {
    return this.request<PortfolioSummary>('/api/v1/portfolio/summary');
  }
}

export const api = new ApiClient();
