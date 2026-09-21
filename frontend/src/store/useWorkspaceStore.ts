import { create } from 'zustand';
import { api, WorkspaceResponse } from '../lib/api';
import { WorkspacePanelItem } from '../components/workspace/WorkspaceGrid';

const DEFAULT_PANELS: WorkspacePanelItem[] = [
  {
    id: 'panel_chart_1',
    type: 'chart',
    title: 'RELIANCE Technical Candlestick Chart',
    symbol: 'RELIANCE',
    layout: { i: 'panel_chart_1', x: 0, y: 0, w: 8, h: 3 },
  },
  {
    id: 'panel_overview_1',
    type: 'overview',
    title: 'NIFTY50 & BSE Sensex Overview',
    symbol: 'NIFTY50',
    layout: { i: 'panel_overview_1', x: 8, y: 0, w: 4, h: 3 },
  },
];

interface WorkspaceState {
  workspaces: WorkspaceResponse[];
  activeWorkspace: WorkspaceResponse | null;
  panels: WorkspacePanelItem[];
  isLoading: boolean;
  saveTimer: ReturnType<typeof setTimeout> | null;
  fetchWorkspaces: () => Promise<void>;
  selectWorkspace: (id: string) => Promise<void>;
  createNewWorkspace: (name: string) => Promise<void>;
  deleteCurrentWorkspace: () => Promise<void>;
  setPanelsAndDebounceSave: (panels: WorkspacePanelItem[]) => void;
}

export const useWorkspaceStore = create<WorkspaceState>((set, get) => ({
  workspaces: [],
  activeWorkspace: null,
  panels: DEFAULT_PANELS,
  isLoading: false,
  saveTimer: null,

  fetchWorkspaces: async () => {
    set({ isLoading: true });
    try {
      const list = await api.getWorkspaces();
      const active = list.find((w) => w.is_default) || list[0] || null;

      const loadedPanels: WorkspacePanelItem[] = active && active.layout_config && active.layout_config.length > 0
        ? active.layout_config.map((item, idx) => ({
            id: item.panelId || `p_${idx}`,
            type: item.panelType || 'chart',
            title: item.title || 'Panel',
            symbol: item.symbol || 'RELIANCE',
            layout: {
              i: item.panelId || `p_${idx}`,
              x: item.x !== undefined ? item.x : 0,
              y: item.y !== undefined ? item.y : 0,
              w: item.w || 4,
              h: item.h || 2,
            },
          }))
        : DEFAULT_PANELS;

      set({ workspaces: list, activeWorkspace: active, panels: loadedPanels, isLoading: false });
    } catch (err) {
      console.error('Failed to load workspaces, falling back to default:', err);
      set({ panels: DEFAULT_PANELS, isLoading: false });
    }
  },

  selectWorkspace: async (id: string) => {
    set({ isLoading: true });
    try {
      const ws = await api.getWorkspace(id);
      const loadedPanels: WorkspacePanelItem[] = ws.layout_config && ws.layout_config.length > 0
        ? ws.layout_config.map((item, idx) => ({
            id: item.panelId || `p_${idx}`,
            type: item.panelType || 'chart',
            title: item.title || 'Panel',
            symbol: item.symbol || 'RELIANCE',
            layout: {
              i: item.panelId || `p_${idx}`,
              x: item.x !== undefined ? item.x : 0,
              y: item.y !== undefined ? item.y : 0,
              w: item.w || 4,
              h: item.h || 2,
            },
          }))
        : DEFAULT_PANELS;

      set({ activeWorkspace: ws, panels: loadedPanels, isLoading: false });
    } catch (err) {
      console.error('Failed to select workspace:', err);
      set({ isLoading: false });
    }
  },

  createNewWorkspace: async (name: string) => {
    try {
      const newWs = await api.createWorkspace(name, 'Custom Indian Market Workspace', []);
      await get().fetchWorkspaces();
      await get().selectWorkspace(newWs.id);
    } catch (err) {
      console.error('Failed to create workspace:', err);
    }
  },

  deleteCurrentWorkspace: async () => {
    const { activeWorkspace } = get();
    if (!activeWorkspace) return;
    try {
      await api.deleteWorkspace(activeWorkspace.id);
      await get().fetchWorkspaces();
    } catch (err) {
      console.error('Failed to delete workspace:', err);
    }
  },

  setPanelsAndDebounceSave: (newPanels: WorkspacePanelItem[]) => {
    const state = get();
    if (state.saveTimer) {
      clearTimeout(state.saveTimer);
    }

    set({ panels: newPanels });

    // 500ms Debounce save to prevent thrashing
    const timer = setTimeout(async () => {
      const currentWs = get().activeWorkspace;
      if (!currentWs) return;

      const serializedLayout = newPanels.map((p) => ({
        panelId: p.id,
        panelType: p.type,
        title: p.title,
        symbol: p.symbol,
        x: p.layout.x,
        y: p.layout.y,
        w: p.layout.w,
        h: p.layout.h,
      }));

      try {
        await api.updateWorkspace(currentWs.id, currentWs.name, serializedLayout);
      } catch (err) {
        console.error('Failed to auto-save workspace layout:', err);
      }
    }, 500);

    set({ saveTimer: timer });
  },
}));
