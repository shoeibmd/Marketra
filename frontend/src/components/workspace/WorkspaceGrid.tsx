import React from 'react';
import 'react-grid-layout/css/styles.css';

import { PanelContainer } from '../panels/PanelContainer';

export interface GridPanelLayout {
  i: string;
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface WorkspacePanelItem {
  id: string;
  type: string;
  title: string;
  symbol?: string;
  layout: GridPanelLayout;
}

interface WorkspaceGridProps {
  panels: WorkspacePanelItem[];
  onLayoutChange?: (newLayout: GridPanelLayout[]) => void;
  onRemovePanel?: (id: string) => void;
}

export const WorkspaceGrid: React.FC<WorkspaceGridProps> = ({
  panels,
  onRemovePanel,
}) => {
  return (
    <div className="grid grid-cols-12 gap-3 min-h-[calc(100vh-80px)] font-mono">
      {panels.map((p) => {
        const colSpanClass =
          p.layout.w >= 12
            ? 'col-span-12'
            : p.layout.w >= 8
            ? 'col-span-12 lg:col-span-8'
            : p.layout.w >= 6
            ? 'col-span-12 md:col-span-6'
            : 'col-span-12 md:col-span-4';

        return (
          <div key={p.id} className={`${colSpanClass} h-80`}>
            <PanelContainer
              panelId={p.id}
              panelType={p.type}
              title={p.title}
              symbol={p.symbol}
              onRemove={onRemovePanel}
            />
          </div>
        );
      })}
    </div>
  );
};
