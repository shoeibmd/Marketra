import { create } from 'zustand';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface WatchlistCompany {
  id?: string;
  symbol: string;
  name: string;
  exchange?: string;
  sector?: string;
}

export interface Watchlist {
  id: string;
  name: string;
  description?: string;
  is_default: boolean;
  company_count: number;
  companies: WatchlistCompany[];
}

export interface NotificationItem {
  id: string;
  event_id?: string;
  title: string;
  summary: string;
  importance: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  event_type: string;
  matched_symbol?: string;
  trigger_reason?: string;
  is_read: boolean;
  created_at: string;
}

interface PersonalWatchlistState {
  watchlists: Watchlist[];
  activeWatchlistId: string | null;
  notifications: NotificationItem[];
  unreadNotificationCount: number;
  isNotificationPanelOpen: boolean;
  isLoading: boolean;
  error: string | null;

  fetchWatchlists: () => Promise<void>;
  setActiveWatchlistId: (id: string) => void;
  createWatchlist: (name: string, description?: string) => Promise<void>;
  addCompanyToWatchlist: (watchlistId: string, symbolOrIsin: string) => Promise<void>;
  removeCompanyFromWatchlist: (watchlistId: string, symbol: string) => Promise<void>;
  fetchNotifications: () => Promise<void>;
  fetchUnreadCount: () => Promise<void>;
  markNotificationRead: (id: string) => Promise<void>;
  markAllNotificationsRead: () => Promise<void>;
  toggleNotificationPanel: (open?: boolean) => void;
  receiveRealtimeWatchlistAlert: (alertData: any) => void;
}

export const usePersonalWatchlistStore = create<PersonalWatchlistState>((set, get) => ({
  watchlists: [],
  activeWatchlistId: null,
  notifications: [],
  unreadNotificationCount: 0,
  isNotificationPanelOpen: false,
  isLoading: false,
  error: null,

  fetchWatchlists: async () => {
    const token = localStorage.getItem('auth_token');
    if (!token) return;
    set({ isLoading: true, error: null });
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/watchlists`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Failed to fetch watchlists');
      const data: Watchlist[] = await res.json();
      set({
        watchlists: data,
        activeWatchlistId: get().activeWatchlistId || (data.length > 0 ? data[0].id : null),
        isLoading: false,
      });
    } catch (err: any) {
      set({ error: err.message, isLoading: false });
    }
  },

  setActiveWatchlistId: (id: string) => set({ activeWatchlistId: id }),

  createWatchlist: async (name: string, description?: string) => {
    const token = localStorage.getItem('auth_token');
    if (!token) return;
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/watchlists`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ name, description }),
      });
      if (!res.ok) throw new Error('Failed to create watchlist');
      await get().fetchWatchlists();
    } catch (err: any) {
      set({ error: err.message });
    }
  },

  addCompanyToWatchlist: async (watchlistId: string, symbolOrIsin: string) => {
    const token = localStorage.getItem('auth_token');
    if (!token) return;
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/watchlists/${watchlistId}/companies`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ symbol_or_isin: symbolOrIsin }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Failed to add symbol');
      }
      await get().fetchWatchlists();
    } catch (err: any) {
      set({ error: err.message });
      throw err;
    }
  },

  removeCompanyFromWatchlist: async (watchlistId: string, symbol: string) => {
    const token = localStorage.getItem('auth_token');
    if (!token) return;
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/watchlists/${watchlistId}/companies/${symbol}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Failed to remove symbol');
      await get().fetchWatchlists();
    } catch (err: any) {
      set({ error: err.message });
    }
  },

  fetchNotifications: async () => {
    const token = localStorage.getItem('auth_token');
    if (!token) return;
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/notifications?limit=50`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Failed to fetch notifications');
      const data: NotificationItem[] = await res.json();
      set({ notifications: data });
      get().fetchUnreadCount();
    } catch (err: any) {
      set({ error: err.message });
    }
  },

  fetchUnreadCount: async () => {
    const token = localStorage.getItem('auth_token');
    if (!token) return;
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/notifications/unread-count`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) return;
      const data = await res.json();
      set({ unreadNotificationCount: data.unread_count });
    } catch {
      // Ignore count error
    }
  },

  markNotificationRead: async (id: string) => {
    const token = localStorage.getItem('auth_token');
    if (!token) return;
    try {
      await fetch(`${API_BASE_URL}/api/v1/notifications/${id}/read`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      set((state) => ({
        notifications: state.notifications.map((n) => (n.id === id ? { ...n, is_read: true } : n)),
        unreadNotificationCount: Math.max(0, state.unreadNotificationCount - 1),
      }));
    } catch {
      // Ignore error
    }
  },

  markAllNotificationsRead: async () => {
    const token = localStorage.getItem('auth_token');
    if (!token) return;
    try {
      await fetch(`${API_BASE_URL}/api/v1/notifications/read-all`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      set((state) => ({
        notifications: state.notifications.map((n) => ({ ...n, is_read: true })),
        unreadNotificationCount: 0,
      }));
    } catch {
      // Ignore error
    }
  },

  toggleNotificationPanel: (open?: boolean) => {
    set((state) => ({
      isNotificationPanelOpen: open !== undefined ? open : !state.isNotificationPanelOpen,
    }));
  },

  receiveRealtimeWatchlistAlert: (alertData: any) => {
    const newNotification: NotificationItem = {
      id: alertData.id || String(Date.now()),
      event_id: alertData.event_id,
      title: alertData.title || 'Smart Watchlist Alert',
      summary: alertData.summary || '',
      importance: alertData.importance || 'HIGH',
      event_type: alertData.event_type || 'ALERT',
      matched_symbol: alertData.matched_symbol,
      trigger_reason: alertData.trigger_reason,
      is_read: false,
      created_at: new Date().toISOString(),
    };

    set((state) => ({
      notifications: [newNotification, ...state.notifications],
      unreadNotificationCount: state.unreadNotificationCount + 1,
    }));
  },
}));
