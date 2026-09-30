import React, { useEffect, useState } from 'react';
import { usePersonalWatchlistStore, Watchlist } from '../../../store/usePersonalWatchlistStore';
import { panelRegistry } from '../../../lib/panelRegistry';

export const PersonalizedWatchlistPanel: React.FC = () => {
  const {
    watchlists,
    activeWatchlistId,
    fetchWatchlists,
    setActiveWatchlistId,
    createWatchlist,
    addCompanyToWatchlist,
    removeCompanyFromWatchlist,
    isLoading,
    error,
  } = usePersonalWatchlistStore();

  const [newWatchlistName, setNewWatchlistName] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newSymbolInput, setNewSymbolInput] = useState('');
  const [addError, setAddError] = useState<string | null>(null);

  useEffect(() => {
    fetchWatchlists();
  }, [fetchWatchlists]);

  const activeWatchlist: Watchlist | undefined = watchlists.find(
    (w) => w.id === activeWatchlistId
  );

  const handleCreateWatchlist = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newWatchlistName.trim()) return;
    await createWatchlist(newWatchlistName.trim());
    setNewWatchlistName('');
    setShowCreateModal(false);
  };

  const handleAddSymbol = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeWatchlistId || !newSymbolInput.trim()) return;
    setAddError(null);
    try {
      await addCompanyToWatchlist(activeWatchlistId, newSymbolInput.trim().toUpperCase());
      setNewSymbolInput('');
    } catch (err: any) {
      setAddError(err.message || 'Failed to add symbol');
    }
  };

  return (
    <div className="h-full flex flex-col bg-slate-900 text-slate-100 p-4 border border-slate-800 rounded-lg overflow-hidden font-sans">
      {/* Header Tabs & Actions */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-2 overflow-x-auto no-scrollbar">
          {watchlists.map((wl) => (
            <button
              key={wl.id}
              onClick={() => setActiveWatchlistId(wl.id)}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-colors ${
                activeWatchlistId === wl.id
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'bg-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              {wl.name} ({wl.company_count})
            </button>
          ))}
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="ml-2 px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-blue-400 text-xs font-medium rounded-md border border-slate-700 transition-colors whitespace-nowrap"
        >
          + New Watchlist
        </button>
      </div>

      {/* Add Symbol Bar */}
      {activeWatchlist && (
        <form onSubmit={handleAddSymbol} className="mt-3 flex items-center space-x-2">
          <input
            type="text"
            placeholder="Add NSE/BSE Symbol or ISIN (e.g. RELIANCE, TCS)..."
            value={newSymbolInput}
            onChange={(e) => setNewSymbolInput(e.target.value)}
            className="flex-1 bg-slate-950 border border-slate-800 text-xs text-slate-200 px-3 py-1.5 rounded-md focus:outline-none focus:border-blue-500"
          />
          <button
            type="submit"
            className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-md transition-colors"
          >
            Add Symbol
          </button>
        </form>
      )}

      {addError && <div className="mt-2 text-xs text-red-400">{addError}</div>}

      {/* Symbol Table */}
      <div className="flex-1 overflow-y-auto mt-3">
        {isLoading ? (
          <div className="p-8 text-center text-xs text-slate-500">Loading watchlists...</div>
        ) : error ? (
          <div className="p-4 bg-red-950/40 border border-red-800/50 rounded-md text-xs text-red-400">
            {error}
          </div>
        ) : !activeWatchlist || activeWatchlist.companies.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-500 border border-dashed border-slate-800 rounded-md">
            No instruments in this watchlist yet. Add symbols above to enable personalized smart event alerts!
          </div>
        ) : (
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider text-[10px]">
                <th className="py-2 px-2">Symbol</th>
                <th className="py-2 px-2">Company Name</th>
                <th className="py-2 px-2">Exchange</th>
                <th className="py-2 px-2">Sector</th>
                <th className="py-2 px-2 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {activeWatchlist.companies.map((comp) => (
                <tr key={comp.symbol} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-2.5 px-2 font-bold text-blue-400">{comp.symbol}</td>
                  <td className="py-2.5 px-2 text-slate-300 font-medium">{comp.name}</td>
                  <td className="py-2.5 px-2 text-slate-400">{comp.exchange || 'NSE'}</td>
                  <td className="py-2.5 px-2 text-slate-400">{comp.sector || 'General'}</td>
                  <td className="py-2.5 px-2 text-right">
                    <button
                      onClick={() =>
                        activeWatchlistId &&
                        removeCompanyFromWatchlist(activeWatchlistId, comp.symbol)
                      }
                      className="text-red-400 hover:text-red-300 text-[11px] font-medium"
                    >
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Create Watchlist Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-lg max-w-sm w-full p-4 space-y-3">
            <h3 className="text-sm font-bold text-slate-100">Create New Custom Watchlist</h3>
            <form onSubmit={handleCreateWatchlist} className="space-y-3">
              <input
                type="text"
                placeholder="Watchlist Name (e.g. IT Giants, High Growth)..."
                value={newWatchlistName}
                onChange={(e) => setNewWatchlistName(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 text-xs text-slate-200 px-3 py-2 rounded-md focus:outline-none focus:border-blue-500"
                autoFocus
              />
              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-3 py-1.5 bg-slate-800 text-slate-300 text-xs font-medium rounded-md hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-3 py-1.5 bg-blue-600 text-white text-xs font-semibold rounded-md hover:bg-blue-500"
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export const PersonalNotificationCenterModal: React.FC = () => {
  const {
    notifications,
    unreadNotificationCount,
    isNotificationPanelOpen,
    toggleNotificationPanel,
    markNotificationRead,
    markAllNotificationsRead,
    fetchNotifications,
  } = usePersonalWatchlistStore();

  useEffect(() => {
    if (isNotificationPanelOpen) {
      fetchNotifications();
    }
  }, [isNotificationPanelOpen, fetchNotifications]);

  if (!isNotificationPanelOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 flex justify-end z-50">
      <div className="bg-slate-900 border-l border-slate-800 w-full max-w-md h-full flex flex-col p-4 shadow-xl">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <h2 className="text-sm font-bold text-slate-100">Personal Notification Center</h2>
            {unreadNotificationCount > 0 && (
              <span className="bg-red-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-full">
                {unreadNotificationCount} New
              </span>
            )}
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => markAllNotificationsRead()}
              className="text-xs text-blue-400 hover:text-blue-300 font-medium"
            >
              Mark all read
            </button>
            <button
              onClick={() => toggleNotificationPanel(false)}
              className="text-slate-400 hover:text-slate-200 text-base font-bold ml-2"
            >
              ✕
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto mt-3 space-y-2">
          {notifications.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-500">
              No personalized notifications yet. Watchlist alerts will trigger automatically!
            </div>
          ) : (
            notifications.map((n) => (
              <div
                key={n.id}
                onClick={() => !n.is_read && markNotificationRead(n.id)}
                className={`p-3 rounded-md border text-xs cursor-pointer transition-colors ${
                  n.is_read
                    ? 'bg-slate-900/60 border-slate-800/60 text-slate-400'
                    : 'bg-slate-800/80 border-blue-500/40 text-slate-200 shadow-sm'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span
                    className={`font-bold uppercase tracking-wider text-[10px] ${
                      n.importance === 'CRITICAL'
                        ? 'text-red-400'
                        : n.importance === 'HIGH'
                        ? 'text-orange-400'
                        : 'text-blue-400'
                    }`}
                  >
                    {n.importance} • {n.event_type}
                  </span>
                  <span className="text-[10px] text-slate-500">
                    {new Date(n.created_at).toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </span>
                </div>
                <h4 className="font-semibold text-slate-100 mt-1">{n.title}</h4>
                <p className="text-[11px] text-slate-300 mt-0.5 line-clamp-2">{n.summary}</p>
                {n.matched_symbol && (
                  <div className="mt-2 flex items-center justify-between text-[10px] text-slate-400">
                    <span>
                      Matched Symbol: <strong className="text-blue-400">{n.matched_symbol}</strong>
                    </span>
                    {n.trigger_reason && (
                      <span className="text-slate-500 italic">{n.trigger_reason}</span>
                    )}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

// Register in PanelRegistry
panelRegistry.register({
  type: 'PERSONALIZED_WATCHLIST',
  title: 'Personalized Watchlist & Smart Alerts',
  category: 'WATCHLIST',
  description: 'Manage personal multi-watchlists with tailored smart event notifications',
  component: PersonalizedWatchlistPanel,
  defaultWidth: 6,
  defaultHeight: 8,
});
