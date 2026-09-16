import React, { ComponentType } from 'react';
import { X, Maximize2, Settings, GripHorizontal } from 'lucide-react';
import { panelRegistry } from '../../lib/panelRegistry';
import { PanelProps } from '../../types/panel';

interface PanelContainerProps {
  panelId: string;
  panelType: string;
  title: string;
  symbol?: string;
  settings?: Record<string, unknown>;
  onRemove?: (panelId: string) => void;
}

export const PanelContainer: React.FC<PanelContainerProps> = ({
  panelId,
  panelType,
  title,
  symbol,
  settings,
  onRemove,
}) => {
  const panelDef = panelRegistry.get(panelType);

  return (
    <div className="flex flex-col h-full bg-slate-900 border border-slate-800 rounded-lg overflow-hidden shadow-lg select-none font-mono">
      {/* Panel Header & Drag Handle */}
      <div className="panel-drag-handle flex items-center justify-between px-3 py-1.5 bg-slate-950 border-b border-slate-800 cursor-move">
        <div className="flex items-center space-x-2 truncate">
          <GripHorizontal className="h-3.5 w-3.5 text-slate-500" />
          <span className="text-xs font-semibold text-slate-200 truncate">{title}</span>
          {symbol && (
            <span className="text-[10px] bg-slate-800 text-emerald-400 px-1.5 py-0.5 rounded font-bold">
              {symbol}
            </span>
          )}
        </div>

        {/* Panel Action Controls */}
        <div className="flex items-center space-x-1">
          <button className="text-slate-500 hover:text-slate-300 p-1 rounded transition-colors" title="Settings">
            <Settings className="h-3 w-3" />
          </button>
          <button className="text-slate-500 hover:text-slate-300 p-1 rounded transition-colors" title="Expand">
            <Maximize2 className="h-3 w-3" />
          </button>
          {onRemove && (
            <button
              onClick={() => onRemove(panelId)}
              className="text-slate-500 hover:text-red-400 p-1 rounded transition-colors"
              title="Remove Panel"
            >
              <X className="h-3 w-3" />
            </button>
          )}
        </div>
      </div>

      {/* Panel Content Body */}
      <div className="flex-1 overflow-auto p-3 bg-slate-900/90 text-slate-300 text-xs">
        {panelDef ? (
          React.createElement(panelDef.component as ComponentType<PanelProps>, {
            panelId,
            symbol,
            settings,
          })
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-slate-500 space-y-2">
            <span className="text-amber-400 font-semibold">Unknown Panel Type: {panelType}</span>
            <span className="text-[10px]">Ensure this panel is registered in PanelRegistry</span>
          </div>
        )}
      </div>
    </div>
  );
};
