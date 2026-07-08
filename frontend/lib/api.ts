import type { BoardData, City, Track, Trip } from "./types";
import { STATIC_BOARD } from "./staticBoard";
import { STATIC_TRIPS } from "./staticTrips";

/** Empty = same-origin (via Next.js rewrites). Set NEXT_PUBLIC_API_URL for direct calls. */
const API_BASE = (process.env.NEXT_PUBLIC_API_URL ?? "").replace(/\/$/, "");

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`${path} returned ${res.status}`);
  return res.json() as Promise<T>;
}

export async function loadBoardData(): Promise<{
  data: BoardData;
  source: "api" | "static";
}> {
  try {
    const [cities, tracks] = await Promise.all([
      fetchJson<City[]>("/cities"),
      fetchJson<Track[]>("/tracks"),
    ]);
    return { data: { cities, tracks }, source: "api" };
  } catch {
    return { data: STATIC_BOARD, source: "static" };
  }
}

export async function checkApiHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/health`, { cache: "no-store" });
    return res.ok;
  } catch {
    return false;
  }
}

export async function loadTrips(): Promise<{
  trips: Trip[];
  source: "api" | "static";
}> {
  try {
    const trips = await fetchJson<Trip[]>("/trips");
    return { trips, source: "api" };
  } catch {
    return { trips: STATIC_TRIPS, source: "static" };
  }
}
