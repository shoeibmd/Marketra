import React, { useEffect, useState } from 'react';
import { api } from '../../lib/api';
import { useAuthStore } from '../../store/useAuthStore';
import { LoginPage } from './LoginPage';

export const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, setAuth, logout } = useAuthStore();
  const [isVerifying, setIsVerifying] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      setIsVerifying(false);
      return;
    }

    api.getMe()
      .then((user) => {
        setAuth(token, user);
      })
      .catch(() => {
        logout();
      })
      .finally(() => {
        setIsVerifying(false);
      });
  }, [setAuth, logout]);

  if (isVerifying) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center">
        <div className="flex items-center space-x-2 text-emerald-400 text-sm">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping"></span>
          <span>Authenticating Session...</span>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  return <>{children}</>;
};
