import React, { useState } from 'react';
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
} from 'lucide-react';
import { useAuthStore } from '../store/useAuthStore';
import { useWorkspaceStore } from '../store/useWorkspaceStore';
import { useWebSocket } from '../hooks/useWebSocket';

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
  } = useWorkspaceStore();

  const [searchQuery, setSearchQuery] = useState('');
  const [newWsName, setNewWsName] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);

  const navItems = [
    { id: 'market', label: 'Market Overview', icon: BarChart3 },
    { id: 'charts', label: 'Interactive Charts', icon: TrendingUp },
    { id: 'news', label: 'Financial News', icon: Newspaper },
    { id: 'portfolio', label: 'Portfolios', icon: Briefcase },
  ];

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 font-mono overflow-hidden">
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
        <header className="h-12 border-b border-slate-800 bg-slate-900/30 flex items-center justify-between px-4">
          <div className="relative w-80">
            <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-slate-500" />
            <input
              type="text"
              placeholder="Search symbol (Cmd+K)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded text-xs pl-9 pr-3 py-1.5 text-slate-200 placeholder-slate-600 focus:outline-none focus:border-emerald-500/50"
            />
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
