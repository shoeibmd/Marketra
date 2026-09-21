import { useEffect, useState } from 'react';

import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { ErrorBoundary } from './components/ErrorBoundary';
import { PanelAdder } from './components/panels/PanelAdder';
import { TerminalLayout } from './components/TerminalLayout';
import { GridPanelLayout, WorkspaceGrid, WorkspacePanelItem } from './components/workspace/WorkspaceGrid';
import { registerDefaultPanels } from './registerPanels';
import { useWorkspaceStore } from './store/useWorkspaceStore';

// Register panels in Registry catalog
registerDefaultPanels();

export function App() {
  const [activeTab, setActiveTab] = useState('market');

  const {
    panels,
    fetchWorkspaces,
    setPanelsAndDebounceSave,
    isLoading,
  } = useWorkspaceStore();

  useEffect(() => {
    fetchWorkspaces();
  }, [fetchWorkspaces]);

  const handleAddPanel = (type: string, title: string, defaultW: number, defaultH: number) => {
    const newId = `panel_${type}_${Date.now()}`;
    const newPanel: WorkspacePanelItem = {
      id: newId,
      type,
      title,
      symbol: 'RELIANCE',
      layout: { i: newId, x: 0, y: Infinity, w: defaultW, h: defaultH },
    };
    setPanelsAndDebounceSave([...panels, newPanel]);
  };

  const handleRemovePanel = (id: string) => {
    setPanelsAndDebounceSave(panels.filter((p) => p.id !== id));
  };

  const handleLayoutChange = (newLayouts: GridPanelLayout[]) => {
    const updated = panels.map((p) => {
      const match = newLayouts.find((l) => l.i === p.id);
      return match ? { ...p, layout: match } : p;
    });
    setPanelsAndDebounceSave(updated);
  };

  return (
    <ErrorBoundary>
      <ProtectedRoute>
        <TerminalLayout activeTab={activeTab} setActiveTab={setActiveTab}>
          <div className="space-y-4 font-mono">
            <div className="flex items-center justify-between border border-slate-800 bg-slate-900/40 rounded-lg p-3">
              <div>
                <h2 className="text-xs font-bold text-slate-200">
                  Indian Market Workspace (NSE/BSE): <span className="text-emerald-400 capitalize">{activeTab}</span>
                </h2>
                <p className="text-[11px] text-slate-500">
                  Phase 26 Real Authentication Flow Active (admin@marketra.com). Syncing layout changes automatically.
                </p>
              </div>
              <PanelAdder onAddPanel={handleAddPanel} />
            </div>

            {isLoading ? (
              <div className="text-xs text-slate-500 animate-pulse p-12 text-center">Loading Indian Market Layout...</div>
            ) : (
              <WorkspaceGrid
                panels={panels}
                onLayoutChange={handleLayoutChange}
                onRemovePanel={handleRemovePanel}
              />
            )}
          </div>
        </TerminalLayout>
      </ProtectedRoute>
    </ErrorBoundary>
  );
}

export default App;
