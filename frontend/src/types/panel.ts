import { ComponentType } from 'react';

export interface PanelProps {
  panelId: string;
  symbol?: string;
  settings?: Record<string, unknown>;
}

export interface PanelDefinition {
  type: string;
  title: string;
  description: string;
  category: 'Market' | 'Charts' | 'News' | 'Fundamentals' | 'Portfolio' | 'AI' | 'Utility';
  defaultWidth: number;
  defaultHeight: number;
  minWidth?: number;
  minHeight?: number;
  component: ComponentType<PanelProps>;
}
