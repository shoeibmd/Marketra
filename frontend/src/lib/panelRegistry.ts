import { PanelDefinition } from '../types/panel';

class PanelRegistry {
  private registry: Map<string, PanelDefinition> = new Map();

  public register(panel: PanelDefinition): void {
    if (this.registry.has(panel.type)) {
      console.warn(`Panel type '${panel.type}' is already registered. Overwriting.`);
    }
    this.registry.set(panel.type, panel);
  }

  public get(type: string): PanelDefinition | undefined {
    return this.registry.get(type);
  }

  public getAll(): PanelDefinition[] {
    return Array.from(this.registry.values());
  }

  public getByCategory(category: PanelDefinition['category']): PanelDefinition[] {
    return this.getAll().filter((p) => p.category === category);
  }
}

export const panelRegistry = new PanelRegistry();
