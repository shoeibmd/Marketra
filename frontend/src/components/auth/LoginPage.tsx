import React, { useState } from 'react';
import { api } from '../../lib/api';
import { useAuthStore } from '../../store/useAuthStore';

export const LoginPage: React.FC = () => {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('admin@marketra.com');
  const [password, setPassword] = useState('Password123!');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const setAuth = useAuthStore((state) => state.setAuth);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      if (isRegister) {
        await api.register(email, password, fullName);
      }

      const res = await api.login(email, password);
      localStorage.setItem('auth_token', res.access_token);

      const user = await api.getMe();
      setAuth(res.access_token, user);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-xl p-8 shadow-2xl">
        <div className="mb-6 text-center">
          <div className="flex items-center justify-center space-x-2 text-emerald-400 font-bold text-xl mb-1">
            <span className="inline-block w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>FINANCIAL TERMINAL</span>
          </div>
          <p className="text-xs text-slate-400">Open-Source Indian Market Platform v0.1</p>
        </div>

        <h2 className="text-lg font-semibold mb-4 text-center">
          {isRegister ? 'Create an Account' : 'Sign in to Terminal'}
        </h2>

        {error && (
          <div className="mb-4 p-3 bg-rose-950/60 border border-rose-800 text-rose-200 text-xs rounded">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {isRegister && (
            <div>
              <label className="block text-xs text-slate-400 mb-1">Full Name</label>
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Enter full name"
                className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-sm focus:outline-none focus:border-emerald-500"
              />
            </div>
          )}

          <div>
            <label className="block text-xs text-slate-400 mb-1">Email Address</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="admin@marketra.com"
              className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-sm focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div>
            <label className="block text-xs text-slate-400 mb-1">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-sm focus:outline-none focus:border-emerald-500"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-emerald-600 hover:bg-emerald-500 text-white py-2 rounded text-sm font-medium transition duration-150 disabled:opacity-50"
          >
            {isLoading ? 'Processing...' : isRegister ? 'Register & Login' : 'Sign In'}
          </button>
        </form>

        <div className="mt-6 text-center text-xs text-slate-400">
          {isRegister ? (
            <p>
              Already have an account?{' '}
              <button
                type="button"
                onClick={() => setIsRegister(false)}
                className="text-emerald-400 hover:underline"
              >
                Sign In
              </button>
            </p>
          ) : (
            <p>
              Don't have an account?{' '}
              <button
                type="button"
                onClick={() => setIsRegister(true)}
                className="text-emerald-400 hover:underline"
              >
                Register
              </button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
};
