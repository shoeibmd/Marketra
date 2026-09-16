import { create } from 'zustand';
import { Quote } from '../types/market';

interface MarketState {
  quotes: Record<string, Quote>;
  activeSymbol: string;
  updateQuote: (quote: Quote) => void;
  setActiveSymbol: (symbol: string) => void;
}

export const useMarketStore = create<MarketState>((set) => ({
  quotes: {},
  activeSymbol: 'AAPL',
  updateQuote: (quote) =>
    set((state) => ({
      quotes: {
        ...state.quotes,
        [quote.instrument_id]: quote,
      },
    })),
  setActiveSymbol: (symbol) => set({ activeSymbol: symbol }),
}));
