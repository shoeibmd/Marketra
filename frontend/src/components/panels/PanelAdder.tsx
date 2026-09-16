import React, { useState } from 'react';
import { Plus, LayoutGrid } from 'lucide-react';
import { panelRegistry } from '../../lib/panelRegistry';

interface PanelAdderProps {
  onAddPanel: (type: string, title: string, defaultW: number, defaultH: number) => void;
}

export const PanelAdder: React.FC<PanelAdderProps> = ({ onAddPanel }) => {
  const [isOpen, setIsOpen] = useState(false);
  const availablePanels = panelRegistry.getAll();

  return (
    <div className="relative font-mono">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-1.5 bg-emerald-950 hover:bg-emerald-900 border border-emerald-800 text-emerald-400 text-xs px-3 py-1.5 rounded transition-colors"
      >
        <Plus className="h-3.5 w-3.5" />
        <span>Add Panel</span>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-72 bg-slate-900 border border-slate-800 rounded-lg shadow-2xl z-50 p-2 text-xs">
          <div className="flex items-center space-x-2 px-2 py-1.5 border-b border-slate-800 mb-2 text-slate-400">
            <LayoutGrid className="h-3.5 w-3.5" />
            <span className="font-semibold text-slate-200">Panel Registry Catalog</span>
          </div>

          <div className="space-y-1 max-h-60 overflow-auto">
            {availablePanels.map((p) => (
              <button
                key={p.type}
                onClick={() => {
                  onAddPanel(p.type, p.title, p.defaultWidth, p.defaultHeight);
                  setIsOpen(false);
                }}
                className="w-full text-left p-2 rounded hover:bg-slate-800 transition-colors flex flex-col group"
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-200 group-hover:text-emerald-400">{p.title}</span>
                  <span className="text-[10px] bg-slate-950 px-1.5 py-0.5 rounded text-slate-500 border border-slate-800">
                    {p.category}
                  </span>
                </div>
                <span className="text-[10px] text-slate-400 mt-0.5">{p.description}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
