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

export interface NewsPaginatedResponse {
  page: number;
  page_size: number;
  total_returned: number;
  items: NewsArticle[];
}

export interface FinancialEventItem {
  id: string;
  news_id?: string;
  cluster_id?: string;
  event_type: string;
  event_title: string;
  event_summary: string;
  event_date: string;
  detected_at: string;
  primary_company_id?: string;
  sector: string;
  importance: string;
  confidence: number;
  source_name: string;
  source_url?: string;
  verified_facts: Record<string, any>;
  ai_analysis: Record<string, any>;
  potential_impact: string;
  uncertainties: Record<string, any>;
  company_roles: Array<{ symbol: string; company_name: string; role: string; note?: string }>;
}

export interface EventsPaginatedResponse {
  page: number;
  page_size: number;
  total_returned: number;
  items: FinancialEventItem[];
}

export interface SourceGroundedResearchAnswer {
  answer_summary: string;
  key_facts: string[];
  recent_events: Array<{ id: string; type: string; title: string; summary: string; date: string; importance: string; source: string; url?: string }>;
  ai_analysis: string;
  potential_impact: string;
  uncertainties: string[];
  sources: Array<{ id: string; type: string; title: string; source: string; url?: string }>;
  related_companies: Array<{ symbol: string; name: string; role: string }>;
  market_context?: { symbol: string; company_name: string; current_price: number; change_percent: number; volume: number; sector: string };
  evidence_confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  context_used: { company?: string; symbol?: string; sector?: string; event_type?: string; date_range?: string; last_query?: string };
}

class ApiClient {
  private getHeaders(): HeadersInit {
    const token = localStorage.getItem('auth_token');
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    try {
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

      return await response.json();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      if (msg.includes('Failed to fetch') || msg.includes('NetworkError')) {
        throw new Error(`Cannot connect to backend. Please ensure backend is running at ${API_BASE_URL}`);
      }
      throw err;
    }
  }

  // Auth
  async login(email: string, password: string): Promise<{ access_token: string; refresh_token: string }> {
    return this.request<{ access_token: string; refresh_token: string }>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async register(email: string, password: string, fullName?: string): Promise<{ id: string; email: string; role: string }> {
    return this.request<{ id: string; email: string; role: string }>('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name: fullName }),
    });
  }

  async getMe(): Promise<{ id: string; email: string; full_name?: string; role: string }> {
    return this.request<{ id: string; email: string; full_name?: string; role: string }>('/api/v1/auth/me');
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

  async getLiveNews(page = 1, pageSize = 10, category?: string): Promise<NewsPaginatedResponse> {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    if (category && category !== 'ALL') {
      params.append('category', category.toLowerCase());
    }
    return this.request<NewsPaginatedResponse>(`/api/v1/news/live?${params.toString()}`);
  }

  async searchNews(
    query?: string,
    category?: string,
    page = 1,
    pageSize = 10
  ): Promise<NewsPaginatedResponse> {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    if (query) params.append('q', query);
    if (category && category !== 'ALL') params.append('category', category.toLowerCase());
    return this.request<NewsPaginatedResponse>(`/api/v1/news/search?${params.toString()}`);
  }

  async getNewsArticleDetail(id: string): Promise<NewsArticle> {
    return this.request<NewsArticle>(`/api/v1/news/${id}`);
  }

  // Phase 10: Financial Events & Intelligence
  async getEvents(page = 1, pageSize = 10, eventType?: string, importance?: string): Promise<EventsPaginatedResponse> {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    if (eventType) params.append('event_type', eventType);
    if (importance) params.append('importance', importance);
    return this.request<EventsPaginatedResponse>(`/api/v1/events?${params.toString()}`);
  }

  async getCompanyTimeline(symbol: string): Promise<{ symbol: string; total_events: number; timeline: Array<{ id: string; date: string; event_type: string; title: string; importance: string; summary: string }> }> {
    return this.request<{ symbol: string; total_events: number; timeline: Array<{ id: string; date: string; event_type: string; title: string; importance: string; summary: string }> }>(`/api/v1/events/company/${symbol}/timeline`);
  }

  async getCompanyRelationships(symbol: string): Promise<{ symbol: string; related_companies: Array<{ symbol: string; company_name: string; role: string; note: string }> }> {
    return this.request<{ symbol: string; related_companies: Array<{ symbol: string; company_name: string; role: string; note: string }> }>(`/api/v1/events/company/${symbol}/relationships`);
  }

  // Phase 11: AI Research Assistant
  async executeResearchQuery(query: string, context?: Record<string, any>): Promise<SourceGroundedAnswer> {
    return this.request<SourceGroundedAnswer>('/api/v1/ai/research', {
      method: 'POST',
      body: JSON.stringify({ query, context }),
    });
  }

  // Portfolio
  async getPortfolio(): Promise<{ portfolio_name: string; cash_balance: number; positions: Position[] }> {
    return this.request<{ portfolio_name: string; cash_balance: number; positions: Position[] }>('/api/v1/portfolio');
  }

  async getPortfolioSummary(): Promise<PortfolioSummary> {
    return this.request<PortfolioSummary>('/api/v1/portfolio/summary');
  }

  async getPortfolioAnalytics(): Promise<any> {
    return this.request<any>('/api/v1/portfolio-analytics/summary');
  }

  // Phase 25: Advanced Portfolio Risk & Stress Testing
  async getPortfolioRiskSummary(): Promise<any> {
    return this.request<any>('/api/v1/portfolio/risk/summary');
  }

  async getPortfolioVaR(confidenceLevel = 0.95): Promise<any> {
    return this.request<any>(`/api/v1/portfolio/risk/var?confidence_level=${confidenceLevel}`);
  }

  async getPortfolioCorrelation(): Promise<any> {
    return this.request<any>('/api/v1/portfolio/risk/correlation');
  }

  async getPortfolioDiversification(): Promise<any> {
    return this.request<any>('/api/v1/portfolio/risk/diversification');
  }

  async getPortfolioRiskContribution(): Promise<any> {
    return this.request<any>('/api/v1/portfolio/risk/contribution');
  }

  async runPortfolioStressTest(body: {
    market_shock_pct?: number;
    sector_shocks?: Record<string, number>;
    symbol_shocks?: Record<string, number>;
    scenario_name?: string;
  }): Promise<any> {
    return this.request<any>('/api/v1/portfolio/risk/stress-test', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  // Phase 26: Portfolio Risk Monitoring & Alerts
  async getRiskAlerts(statusFilter?: string): Promise<any[]> {
    const url = statusFilter ? `/api/v1/portfolio/risk/alerts?status_filter=${statusFilter}` : '/api/v1/portfolio/risk/alerts';
    return this.request<any[]>(url);
  }

  async getRiskAlertPreferences(): Promise<any> {
    return this.request<any>('/api/v1/portfolio/risk/alerts/preferences');
  }

  async updateRiskAlertPreferences(body: any): Promise<any> {
    return this.request<any>('/api/v1/portfolio/risk/alerts/preferences', {
      method: 'PUT',
      body: JSON.stringify(body),
    });
  }

  async resetRiskAlertPreferences(): Promise<any> {
    return this.request<any>('/api/v1/portfolio/risk/alerts/preferences/reset', {
      method: 'POST',
    });
  }

  async markRiskAlertRead(alertId: string): Promise<any> {
    return this.request<any>(`/api/v1/portfolio/risk/alerts/${alertId}/read`, {
      method: 'POST',
    });
  }

  async triggerRiskEvaluationTest(): Promise<any> {
    return this.request<any>('/api/v1/portfolio/risk/alerts/test', {
      method: 'POST',
    });
  }

  async getRiskHistory(): Promise<any> {
    return this.request<any>('/api/v1/portfolio/risk/history');
  }

  // Phase 27: Portfolio Risk Command Center & Executive Intelligence
  async getRiskCommandCenterData(): Promise<any> {
    return this.request<any>('/api/v1/portfolio/risk-command-center');
  }

  async exportRiskCommandCenterReport(): Promise<any> {
    return this.request<any>('/api/v1/portfolio/risk-command-center/export');
  }

  // Phase 28: Automated Portfolio Intelligence & Briefings
  async getBriefings(type?: string): Promise<any[]> {
    const url = type ? `/api/v1/portfolio/briefings?briefing_type=${type}` : '/api/v1/portfolio/briefings';
    return this.request<any[]>(url);
  }

  async getBriefingDetail(briefingId: string): Promise<any> {
    return this.request<any>(`/api/v1/portfolio/briefings/${briefingId}`);
  }

  async generateBriefingOnDemand(briefingType = 'DAILY'): Promise<any> {
    return this.request<any>('/api/v1/portfolio/briefings/generate', {
      method: 'POST',
      body: JSON.stringify({ briefing_type: briefingType }),
    });
  }

  async getBriefingPreferences(): Promise<any> {
    return this.request<any>('/api/v1/portfolio/briefings/preferences');
  }

  async updateBriefingPreferences(body: any): Promise<any> {
    return this.request<any>('/api/v1/portfolio/briefings/preferences', {
      method: 'PUT',
      body: JSON.stringify(body),
    });
  }

  async getPortfolioChanges(): Promise<any[]> {
    return this.request<any[]>('/api/v1/portfolio/briefings/changes');
  }
}

export const api = new ApiClient();
