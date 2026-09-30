import React, { useState } from 'react';
import { useNotificationStore, NotificationFilterSetting } from '../../store/useNotificationStore';
import { Bell, X, Settings } from 'lucide-react';

export const NewsToastNotification: React.FC = () => {
  const { activeAlert, dismissActiveAlert, filterSetting, setFilterSetting } = useNotificationStore();
  const [showSettings, setShowSettings] = useState(false);

  if (!activeAlert && !showSettings) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col space-y-2 font-mono text-xs max-w-sm">
      {/* Toast Alert Box */}
      {activeAlert && (
        <div className="p-3 bg-slate-900 border-2 border-emerald-500 rounded-xl shadow-2xl space-y-2 animate-bounce-short">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-1.5 text-emerald-400 font-bold text-xs">
              <Bell className="h-4 w-4 text-emerald-400 animate-pulse" />
              <span>🔔 {activeAlert.importance || 'HIGH'} IMPORTANCE</span>
            </div>
            <div className="flex items-center space-x-1">
              <button
                onClick={() => setShowSettings(!showSettings)}
                className="p-1 hover:bg-slate-800 rounded text-slate-400 hover:text-slate-200"
                title="Notification Settings"
              >
                <Settings className="h-3.5 w-3.5" />
              </button>
              <button
                onClick={dismissActiveAlert}
                className="p-1 hover:bg-slate-800 rounded text-slate-400 hover:text-slate-200"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>

          <div className="space-y-1">
            <span className="text-[10px] bg-emerald-950 text-emerald-300 border border-emerald-800 px-1.5 py-0.5 rounded font-bold">
              {activeAlert.company || activeAlert.symbol}
            </span>
            <h4 className="font-bold text-slate-100 text-xs leading-snug">{activeAlert.title}</h4>
            <p className="text-slate-400 text-[11px] line-clamp-2">{activeAlert.summary}</p>
          </div>

          <div className="pt-1 flex justify-end">
            <button
              onClick={dismissActiveAlert}
              className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold px-2.5 py-1 rounded text-[10px] transition-colors"
            >
              VIEW DETAILS
            </button>
          </div>
        </div>
      )}

      {/* Settings Panel */}
      {showSettings && (
        <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl space-y-2">
          <div className="flex items-center justify-between border-b border-slate-800 pb-1.5">
            <span className="font-bold text-slate-200 text-xs flex items-center space-x-1">
              <Settings className="h-3.5 w-3.5 text-emerald-400" />
              <span>Alert Preferences</span>
            </span>
            <button onClick={() => setShowSettings(false)} className="text-slate-500 hover:text-slate-300">
              <X className="h-3.5 w-3.5" />
            </button>
          </div>

          <div className="space-y-1 text-[11px]">
            {(
              [
                ['ALL_IMPORTANT_NEWS', 'ALL IMPORTANT NEWS'],
                ['HIGH_CRITICAL_ONLY', 'HIGH + CRITICAL ONLY'],
                ['MARKET_EVENTS', 'MARKET EVENTS'],
                ['CORPORATE_EVENTS', 'CORPORATE EVENTS'],
                ['MY_WATCHLIST', 'MY WATCHLIST'],
              ] as [NotificationFilterSetting, string][]
            ).map(([key, label]) => (
              <label key={key} className="flex items-center space-x-2 text-slate-300 cursor-pointer">
                <input
                  type="radio"
                  name="alertFilter"
                  checked={filterSetting === key}
                  onChange={() => setFilterSetting(key)}
                  className="accent-emerald-500"
                />
                <span>{label}</span>
              </label>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
