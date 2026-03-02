const BASE_URL = "/api";

async function fetchJSON<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers: {
      ...(!init?.body || init.body instanceof FormData
        ? {}
        : { "Content-Type": "application/json" }),
      ...init?.headers,
    },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(text);
  }
  return res.json();
}

// ── Types ─────────────────────────────────────────────────────

export interface Player {
  id: string;
  name: string;
  alliance: string;
  server: number;
  is_enemy: boolean;
  tags: string[];
  notes: string;
  active: boolean;
}

export interface PowerReading {
  date: string;
  player_id: string;
  total_power: number;
  building_power: number;
  tech_power: number;
  troop_power: number;
  hero_power: number;
  vehicle_power: number;
  kill_count: number;
  source: string;
}

export interface ScanResult {
  status: string;
  saved: boolean;
  filename: string;
  player_name_ocr?: string;
  reading?: PowerReading;
  confidence?: Record<string, number>;
  warnings?: string[];
  error?: string;
}

// ── Player API ────────────────────────────────────────────────

export const getPlayers = () => fetchJSON<Player[]>("/players");

export const getPlayer = (id: string) => fetchJSON<Player>(`/players/${id}`);

export const createPlayer = (data: Partial<Player>) =>
  fetchJSON<Player>("/players", {
    method: "POST",
    body: JSON.stringify(data),
  });

// ── Power API ─────────────────────────────────────────────────

export const getPowerRanking = (top = 20) =>
  fetchJSON<PowerReading[]>(`/power/rank?top=${top}`);

export const getPowerHistory = (playerId: string) =>
  fetchJSON<PowerReading[]>(`/power/history/${playerId}`);

export const addPower = (data: Partial<PowerReading>) =>
  fetchJSON<PowerReading>("/power", {
    method: "POST",
    body: JSON.stringify(data),
  });

// ── Scan API ──────────────────────────────────────────────────

export const scanScreenshot = (file: File, playerId?: string) => {
  const formData = new FormData();
  formData.append("file", file);
  const params = playerId ? `?player_id=${playerId}` : "";
  return fetchJSON<ScanResult>(`/scan${params}`, {
    method: "POST",
    body: formData,
  });
};

// ── Events API ────────────────────────────────────────────────

export const getEvents = () => fetchJSON<unknown[]>("/events");

// ── Reports API ───────────────────────────────────────────────

export const generateReport = () =>
  fetchJSON<{ status: string; message?: string }>("/reports/generate", {
    method: "POST",
  });

// ── Utility ───────────────────────────────────────────────────

export function formatPower(value: number): string {
  if (value >= 100_000_000) {
    const eok = Math.floor(value / 100_000_000);
    const man = Math.floor((value % 100_000_000) / 10_000);
    return man > 0 ? `${eok}억 ${man.toLocaleString()}만` : `${eok}억`;
  }
  if (value >= 10_000) {
    return `${Math.floor(value / 10_000).toLocaleString()}만`;
  }
  return value.toLocaleString();
}
