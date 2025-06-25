import { TideStorage } from "./tide-storage.ts";

// Get data directory - lazily evaluated to respect test overrides
function getDataDir(): string {
  return Deno.env.get("TIDES_DATA_DIR") || "/app/data/tides";
}

// Create storage instance that respects env changes
class TideStorageManager {
  private storage: TideStorage | null = null;
  private lastDir: string | null = null;

  getStorage(): TideStorage {
    const currentDir = getDataDir();
    if (!this.storage || this.lastDir !== currentDir) {
      this.storage = new TideStorage(currentDir);
      this.lastDir = currentDir;
    }
    return this.storage;
  }
}

const manager = new TideStorageManager();

// Export a proxy that always uses the current storage
export const tideStorage = new Proxy({} as TideStorage, {
  get(_target, prop, receiver) {
    const storage = manager.getStorage();
    return Reflect.get(storage, prop, receiver);
  }
});

// Re-export types
export type { TideData, CreateTideInput, ListTidesFilter } from "./tide-storage.ts";