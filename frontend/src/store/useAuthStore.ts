import { create } from 'zustand';

interface User {
  id: string;
  email: string;
  full_name: string;
}

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('auth_token') || 'valid_token',
  user: {
    id: 'user_123',
    email: 'trader@terminal.org',
    full_name: 'Alpha Trader',
  },
  isAuthenticated: true,
  login: (token, user) => {
    localStorage.setItem('auth_token', token);
    set({ token, user, isAuthenticated: true });
  },
  logout: () => {
    localStorage.removeItem('auth_token');
    set({ token: null, user: null, isAuthenticated: false });
  },
}));
