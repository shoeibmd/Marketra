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

export const useAuthStore = create<AuthState>((set) => {
  const savedToken = localStorage.getItem('auth_token');
  return {
    token: savedToken,
    user: savedToken
      ? {
          id: '11111111-1111-1111-1111-111111111111',
          email: 'trader@terminal.org',
          full_name: 'Alpha Trader',
        }
      : null,
    isAuthenticated: !!savedToken,
    login: (token, user) => {
      localStorage.setItem('auth_token', token);
      set({ token, user, isAuthenticated: true });
    },
    logout: () => {
      localStorage.removeItem('auth_token');
      set({ token: null, user: null, isAuthenticated: false });
    },
  };
});
