import { join } from "https://deno.land/std@0.208.0/path/mod.ts";
import { ensureDir } from "https://deno.land/std@0.208.0/fs/mod.ts";

export interface TideData {
  id: string;
  name: string;
  flow_type: "daily" | "weekly" | "project" | "seasonal";
  status: "active" | "paused" | "completed";
  created_at: string;
  last_flow?: string;
  next_flow?: string;
  description?: string;
  flow_history: Array<{
    timestamp: string;
    intensity: "gentle" | "moderate" | "strong";
    duration: number;
    notes?: string;
  }>;
}

export interface CreateTideInput {
  name: string;
  flow_type: "daily" | "weekly" | "project" | "seasonal";
  description?: string;
}

export interface ListTidesFilter {
  flow_type?: string;
  active_only?: boolean;
}

export class TideStorage {
  private dataDir: string;

  constructor(dataDir: string) {
    this.dataDir = dataDir;
  }

  async createTide(input: CreateTideInput): Promise<TideData> {
    await ensureDir(this.dataDir);

    const now = new Date();
    const id = `tide_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    // Calculate next flow based on type
    let next_flow: string | undefined;
    switch (input.flow_type) {
      case "daily":
        next_flow = new Date(now.getTime() + 24 * 60 * 60 * 1000).toISOString();
        break;
      case "weekly":
        next_flow = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000).toISOString();
        break;
      case "seasonal":
        next_flow = new Date(now.getTime() + 90 * 24 * 60 * 60 * 1000).toISOString();
        break;
      // project type has no automatic next flow
    }

    const tide: TideData = {
      id,
      name: input.name,
      flow_type: input.flow_type,
      status: "active",
      created_at: now.toISOString(),
      next_flow,
      description: input.description,
      flow_history: []
    };

    await this.saveTide(tide);
    return tide;
  }

  async getTide(id: string): Promise<TideData | null> {
    const filePath = join(this.dataDir, `${id}.json`);
    
    try {
      const content = await Deno.readTextFile(filePath);
      return JSON.parse(content);
    } catch {
      return null;
    }
  }

  async listTides(filter?: ListTidesFilter): Promise<TideData[]> {
    try {
      await ensureDir(this.dataDir);
      const entries = [];
      
      for await (const entry of Deno.readDir(this.dataDir)) {
        if (entry.isFile && entry.name.endsWith('.json')) {
          const content = await Deno.readTextFile(join(this.dataDir, entry.name));
          const tide = JSON.parse(content) as TideData;
          
          // Apply filters
          if (filter?.flow_type && tide.flow_type !== filter.flow_type) {
            continue;
          }
          
          if (filter?.active_only && tide.status !== "active") {
            continue;
          }
          
          entries.push(tide);
        }
      }
      
      // Sort by created_at descending
      return entries.sort((a, b) => 
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
    } catch {
      return [];
    }
  }

  async updateTide(id: string, updates: Partial<TideData>): Promise<TideData | null> {
    const tide = await this.getTide(id);
    if (!tide) return null;

    const updated = { ...tide, ...updates, id: tide.id }; // Ensure ID can't be changed
    await this.saveTide(updated);
    return updated;
  }

  async addFlowToTide(
    id: string, 
    flow: {
      timestamp: string;
      intensity: "gentle" | "moderate" | "strong";
      duration: number;
      notes?: string;
    }
  ): Promise<TideData | null> {
    const tide = await this.getTide(id);
    if (!tide) return null;

    tide.flow_history.push(flow);
    tide.last_flow = flow.timestamp;

    // Update next_flow for recurring types
    const now = new Date(flow.timestamp);
    switch (tide.flow_type) {
      case "daily":
        tide.next_flow = new Date(now.getTime() + 24 * 60 * 60 * 1000).toISOString();
        break;
      case "weekly":
        tide.next_flow = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000).toISOString();
        break;
      case "seasonal":
        tide.next_flow = new Date(now.getTime() + 90 * 24 * 60 * 60 * 1000).toISOString();
        break;
    }

    await this.saveTide(tide);
    return tide;
  }

  private async saveTide(tide: TideData): Promise<void> {
    const filePath = join(this.dataDir, `${tide.id}.json`);
    await Deno.writeTextFile(filePath, JSON.stringify(tide, null, 2));
  }
}