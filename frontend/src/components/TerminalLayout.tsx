import React, { useState, useEffect, useRef } from 'react';
import {
  BarChart3,
  TrendingUp,
  Newspaper,
  Briefcase,
  Search,
  Wifi,
  WifiOff,
  User,
  LogOut,
  FolderKanban,
  Trash2,
  Loader2,
  Building2,
} from 'lucide-react';
import { useAuthStore } from '../store/useAuthStore';
import { useWorkspaceStore } from '../store/useWorkspaceStore';
import { useWebSocket } from '../hooks/useWebSocket';
import { NewsToastNotification } from './notifications/NewsToastNotification';
import { api } from '../lib/api';
import { Instrument } from '../types/market';

interface NavigationProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  children: React.ReactNode;
}

export function TerminalLayout({ activeTab, setActiveTab, children }: NavigationProps) {
  const { user, logout } = useAuthStore();
  const { isConnected } = useWebSocket();
  const {
    workspaces,
    activeWorkspace,
    selectWorkspace,
    createNewWorkspace,
    deleteCurrentWorkspace,
    updateWorkspaceLayout,
  } = useWorkspaceStore();

  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Instrument[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);

  const [newWsName, setNewWsName] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);

  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      setIsSearching(false);
      setShowDropdown(false);
      return;
    }

    const timer = setTimeout(() => {
      setIsSearching(true);
      setShowDropdown(true);
      api
        .searchInstruments(searchQuery)
        .then((res) => {
          setSearchResults(res);
          setIsSearching(false);
        })
        .catch(() => {
          setSearchResults([]);
          setIsSearching(false);
        });
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelectInstrument = (inst: Instrument) => {
    setShowDropdown(false);
    setSearchQuery('');
    setActiveTab('charts');

    if (activeWorkspace) {
      const updatedLayout = activeWorkspace.layout_config.map((panel) => {
        if (panel.panelType === 'chart') {
          return { ...panel, symbol: inst.symbol, title: `${inst.symbol} Technical Candlestick Chart` };
        }
        return panel;
      });
      updateWorkspaceLayout(updatedLayout);
    }
  };

  const navItems = [
    { id: 'market', label: 'Market Overview', icon: BarChart3 },
    { id: 'charts', label: 'Interactive Charts', icon: TrendingUp },
    { id: 'news', label: 'Financial News', icon: Newspaper },
    { id: 'portfolio', label: 'Portfolios', icon: Briefcase },
  ];

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 font-mono overflow-hidden">
      {/* Real-time Toast Notifications */}
      <NewsToastNotification />

      {/* Sidebar Navigation */}
      <aside className="w-64 border-r border-slate-800 bg-slate-900/50 flex flex-col justify-between select-none">
        <div>
          {/* Header Branding */}
          <div className="p-4 border-b border-slate-800 flex items-center space-x-3">
            <div className="h-3 w-3 rounded-full bg-emerald-500 animate-pulse" />
            <div>
              <h1 className="font-bold text-sm tracking-wide text-slate-100">FINANCIAL TERMINAL</h1>
              <span className="text-[10px] text-slate-500 block">Open Source Platform v0.1</span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-2 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center space-x-3 px-3 py-2 rounded text-xs transition-colors ${
                    isActive
                      ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-800/50 font-semibold'
                      : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Connection & Auth User Profile */}
        <div className="p-3 border-t border-slate-800 bg-slate-950/80 text-xs">
          <div className="flex items-center justify-between mb-3 px-1">
            <span className="text-slate-500 text-[10px]">WEBSOCKET</span>
            <div className="flex items-center space-x-1">
              {isConnected ? (
                <>
                  <Wifi className="h-3 w-3 text-emerald-400" />
                  <span className="text-emerald-400 text-[10px]">LIVE</span>
                </>
              ) : (
                <>
                  <WifiOff className="h-3 w-3 text-amber-500" />
                  <span className="text-amber-500 text-[10px]">OFFLINE</span>
                </>
              )}
            </div>
          </div>

          <div className="flex items-center justify-between pt-2 border-t border-slate-900">
            <div className="flex items-center space-x-2">
              <User className="h-4 w-4 text-slate-400" />
              <span className="text-slate-300 text-xs truncate max-w-[110px]">{user?.full_name}</span>
            </div>
            <button
              onClick={logout}
              title="Logout"
              className="text-slate-500 hover:text-red-400 transition-colors"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Terminal Shell Content Area */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Top Command & Workspace Selector Bar */}
        <header className="h-12 border-b border-slate-800 bg-slate-900/30 flex items-center justify-between px-4 z-40">
          <div className="relative w-80" ref={dropdownRef}>
            <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-slate-500" />
            <input
              type="text"
              placeholder="Search company/symbol (RELIANCE, TCS...)"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onFocus={() => {
                if (searchQuery.trim()) setShowDropdown(true);
              }}
              className="w-full bg-slate-950 border border-slate-800 rounded text-xs pl-9 pr-8 py-1.5 text-slate-200 placeholder-slate-600 focus:outline-none focus:border-emerald-500/50"
            />
            {isSearching && (
              <Loader2 className="absolute right-3 top-2.5 h-3.5 w-3.5 text-emerald-400 animate-spin" />
            )}

            {/* Global Search Results Dropdown */}
            {showDropdown && (
              <div className="absolute left-0 right-0 mt-1.5 bg-slate-900 border border-slate-800 rounded-md shadow-2xl overflow-hidden z-50 text-xs max-h-72 overflow-y-auto">
                {isSearching ? (
                  <div className="p-3 text-center text-slate-500 flex items-center justify-center space-x-2">
                    <Loader2 className="h-3.5 w-3.5 animate-spin text-emerald-400" />
                    <span>Searching instruments...</span>
                  </div>
                ) : searchResults.length > 0 ? (
                  <div className="divide-y divide-slate-800/60">
                    <div className="px-3 py-1.5 bg-slate-950 text-[10px] text-slate-500 font-bold uppercase tracking-wider flex justify-between">
                      <span>Symbol / Name</span>
                      <span>Exchange / Type</span>
                    </div>
                    {searchResults.map((inst) => (
                      <button
                        key={inst.id}
                        onClick={() => handleSelectInstrument(inst)}
                        className="w-full text-left px-3 py-2 hover:bg-slate-800/80 transition-colors flex items-center justify-between group"
                      >
                        <div className="flex items-center space-x-2 truncate">
                          <Building2 className="h-3.5 w-3.5 text-emerald-400 flex-shrink-0" />
                          <div className="truncate">
                            <span className="font-bold text-slate-100 group-hover:text-emerald-400 mr-2">
                              {inst.symbol}
                            </span>
                            <span className="text-slate-400 text-[11px] truncate">{inst.name}</span>
                          </div>
                        </div>
                        <div className="text-right flex-shrink-0 ml-2">
                          <span className="text-[10px] bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded border border-slate-700">
                            {inst.exchange_code || 'NSE'} • {inst.instrument_type}
                          </span>
                        </div>
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="p-4 text-center text-slate-400">
                    No companies found.
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Workspace Controls */}
          <div className="flex items-center space-x-3 text-xs">
            <div className="flex items-center space-x-2">
              <FolderKanban className="h-4 w-4 text-slate-500" />
              <select
                value={activeWorkspace?.id || ''}
                onChange={(e) => selectWorkspace(e.target.value)}
                className="bg-slate-950 border border-slate-800 text-slate-200 text-xs rounded px-2 py-1 focus:outline-none focus:border-emerald-500"
              >
                {workspaces.map((w) => (
                  <option key={w.id} value={w.id}>
                    {w.name} {w.is_default ? '(Default)' : ''}
                  </option>
                ))}
              </select>
            </div>

            <button
              onClick={() => setShowCreateModal(true)}
              className="text-emerald-400 hover:text-emerald-300 border border-emerald-900 bg-emerald-950/60 px-2 py-1 rounded text-[11px]"
            >
              + New Workspace
            </button>

            {activeWorkspace && !activeWorkspace.is_default && (
              <button
                onClick={deleteCurrentWorkspace}
                title="Delete Workspace"
                className="text-slate-500 hover:text-red-400"
              >
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            )}
          </div>
        </header>

        {/* Modal for Workspace Creation */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 max-w-sm w-full space-y-3">
              <h3 className="text-xs font-bold text-slate-200">Create New Workspace Layout</h3>
              <input
                type="text"
                placeholder="Workspace name..."
                value={newWsName}
                onChange={(e) => setNewWsName(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-1.5 text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-emerald-500"
              />
              <div className="flex items-center justify-end space-x-2 pt-2">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="text-xs text-slate-400 hover:text-slate-200 px-3 py-1"
                >
                  Cancel
                </button>
                <button
                  onClick={async () => {
                    if (newWsName.trim()) {
                      await createNewWorkspace(newWsName.trim());
                      setNewWsName('');
                      setShowCreateModal(false);
                    }
                  }}
                  className="bg-emerald-950 hover:bg-emerald-900 border border-emerald-800 text-emerald-400 text-xs px-3 py-1 rounded"
                >
                  Create
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Dynamic Workspace Container */}
        <div className="flex-1 overflow-auto p-4">{children}</div>
      </main>
    </div>
  );
}
