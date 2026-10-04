import React, { useState } from 'react';
import { api } from '../../lib/api';
import { useAuthStore } from '../../store/useAuthStore';

export const LoginPage: React.FC = () => {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const setAuth = useAuthStore((state) => state.setAuth);

  // Client-side password policy checks
  const hasMinLength = password.length >= 8;
  const hasUppercase = /[A-Z]/.test(password);
  const hasLowercase = /[a-z]/.test(password);
  const hasDigit = /\d/.test(password);
  const hasSpecial = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>/?]/.test(password);

  const isPasswordValid = hasMinLength && hasUppercase && hasLowercase && hasDigit && hasSpecial;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (isRegister && !isPasswordValid) {
      setError('Please ensure your password meets all complexity requirements below.');
      return;
    }

    setIsLoading(true);

    try {
      if (isRegister) {
        await api.register(email.trim().toLowerCase(), password, fullName.trim());
      }

      const res = await api.login(email.trim().toLowerCase(), password);
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
    <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center p-4 font-mono">
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-xl p-8 shadow-2xl space-y-6">
        <div className="text-center space-y-1">
          <div className="flex items-center justify-center space-x-2 text-emerald-400 font-bold text-xl">
            <span className="inline-block w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>MARKETRA TERMINAL</span>
          </div>
          <p className="text-xs text-slate-400">Open-Source Indian Market Platform v1.1.0</p>
        </div>

        <h2 className="text-sm font-bold text-slate-200 text-center uppercase tracking-wider">
          {isRegister ? 'Create Marketra Account' : 'Sign in to Terminal'}
        </h2>

        {error && (
          <div className="p-3 bg-rose-950/80 border border-rose-800 text-rose-200 text-xs rounded leading-relaxed">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          {isRegister && (
            <div>
              <label className="block text-slate-400 mb-1 font-bold">FULL NAME</label>
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Marketra User"
                className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-slate-100 focus:outline-none focus:border-emerald-500"
              />
            </div>
          )}

          <div>
            <label className="block text-slate-400 mb-1 font-bold">EMAIL ADDRESS</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="user@marketra.com"
              className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-slate-100 focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div>
            <label className="block text-slate-400 mb-1 font-bold">PASSWORD</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-slate-100 focus:outline-none focus:border-emerald-500"
            />
          </div>

          {/* Password Requirements Checklist for Registration */}
          {isRegister && (
            <div className="p-3 bg-slate-950 border border-slate-800 rounded space-y-1 text-[10px]">
              <span className="text-slate-400 font-bold block mb-1">PASSWORD REQUIREMENTS:</span>
              <div className={`flex items-center space-x-1.5 ${hasMinLength ? 'text-emerald-400' : 'text-slate-500'}`}>
                <span>{hasMinLength ? '✓' : '○'}</span>
                <span>Minimum 8 characters</span>
              </div>
              <div className={`flex items-center space-x-1.5 ${hasLowercase ? 'text-emerald-400' : 'text-slate-500'}`}>
                <span>{hasLowercase ? '✓' : '○'}</span>
                <span>One lowercase letter (a-z)</span>
              </div>
              <div className={`flex items-center space-x-1.5 ${hasUppercase ? 'text-emerald-400' : 'text-slate-500'}`}>
                <span>{hasUppercase ? '✓' : '○'}</span>
                <span>One uppercase letter (A-Z)</span>
              </div>
              <div className={`flex items-center space-x-1.5 ${hasDigit ? 'text-emerald-400' : 'text-slate-500'}`}>
                <span>{hasDigit ? '✓' : '○'}</span>
                <span>One number (0-9)</span>
              </div>
              <div className={`flex items-center space-x-1.5 ${hasSpecial ? 'text-emerald-400' : 'text-slate-500'}`}>
                <span>{hasSpecial ? '✓' : '○'}</span>
                <span>One special character (!@#$%^&*)</span>
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading || (isRegister && !isPasswordValid)}
            className="w-full bg-emerald-600 hover:bg-emerald-500 text-white py-2 rounded font-bold transition duration-150 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Authenticating...' : isRegister ? 'Register & Enter Terminal' : 'Sign In'}
          </button>
        </form>

        <div className="text-center text-xs text-slate-400 border-t border-slate-800/80 pt-4">
          {isRegister ? (
            <p>
              Already have an account?{' '}
              <button
                type="button"
                onClick={() => { setIsRegister(false); setError(null); }}
                className="text-emerald-400 font-bold hover:underline"
              >
                Sign In
              </button>
            </p>
          ) : (
            <p>
              Need an account?{' '}
              <button
                type="button"
                onClick={() => { setIsRegister(true); setError(null); }}
                className="text-emerald-400 font-bold hover:underline"
              >
                Create Account
              </button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
};
