import { create } from 'zustand';

export type NotificationFilterSetting =
  | 'ALL_IMPORTANT_NEWS'
  | 'HIGH_CRITICAL_ONLY'
  | 'MARKET_EVENTS'
  | 'CORPORATE_EVENTS'
  | 'MY_WATCHLIST';

export interface RealtimeNewsAlert {
  news_id: string;
  symbol: string;
  company: string;
  title: string;
  category: string;
  importance: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  summary: string;
  published_at: string;
}

interface NotificationState {
  filterSetting: NotificationFilterSetting;
  watchlistSymbols: string[];
  activeAlert: RealtimeNewsAlert | null;
  alertHistory: RealtimeNewsAlert[];
  seenNewsIds: Set<string>;
  setFilterSetting: (setting: NotificationFilterSetting) => void;
  setWatchlistSymbols: (symbols: string[]) => void;
  receiveNewsAlert: (alert: RealtimeNewsAlert) => void;
  dismissActiveAlert: () => void;
}

export const useNotificationStore = create<NotificationState>((set, get) => ({
  filterSetting: 'ALL_IMPORTANT_NEWS',
  watchlistSymbols: ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK'],
  activeAlert: null,
  alertHistory: [],
  seenNewsIds: new Set<string>(),

  setFilterSetting: (setting: NotificationFilterSetting) => set({ filterSetting: setting }),
  setWatchlistSymbols: (symbols: string[]) => set({ watchlistSymbols: symbols }),

  receiveNewsAlert: (alert: RealtimeNewsAlert) => {
    const { filterSetting, watchlistSymbols, seenNewsIds, alertHistory } = get();

    // Prevent notification spam & deduplicate
    if (seenNewsIds.has(alert.news_id)) return;

    // Filter rules
    if (filterSetting === 'HIGH_CRITICAL_ONLY') {
      if (alert.importance !== 'HIGH' && alert.importance !== 'CRITICAL') return;
    } else if (filterSetting === 'MARKET_EVENTS') {
      if (!alert.category.includes('monetary') && !alert.category.includes('regulation') && !alert.category.includes('macro')) return;
    } else if (filterSetting === 'CORPORATE_EVENTS') {
      if (!alert.category.includes('corporate') && !alert.category.includes('earnings') && !alert.category.includes('dividend')) return;
    } else if (filterSetting === 'MY_WATCHLIST') {
      if (!watchlistSymbols.includes(alert.symbol)) return;
    }

    const updatedSeen = new Set(seenNewsIds).add(alert.news_id);
    set({
      activeAlert: alert,
      alertHistory: [alert, ...alertHistory],
      seenNewsIds: updatedSeen,
    });
  },

  dismissActiveAlert: () => set({ activeAlert: null }),
}));
