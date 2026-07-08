import { edgeKey } from "./coords";
import type { EdgeClaims, EdgeOwner } from "./types";

const STORAGE_KEY = "ttro-edge-claims";
const TRIP_HAND_KEY = "ttro-trip-hand";

export const MAX_TRIP_HAND = 10;

export function loadEdgeClaims(): EdgeClaims {
  if (typeof window === "undefined") return {};
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw) as unknown;
    if (!parsed || typeof parsed !== "object") return {};
    const claims: EdgeClaims = {};
    for (const [key, owner] of Object.entries(parsed)) {
      if (owner === "self" || owner === "opponent") {
        claims[key] = owner;
      }
    }
    return claims;
  } catch {
    return {};
  }
}

export function saveEdgeClaims(claims: EdgeClaims): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(claims));
}

export function clearEdgeClaims(): EdgeClaims {
  if (typeof window !== "undefined") {
    localStorage.removeItem(STORAGE_KEY);
  }
  return {};
}

export function cycleEdgeOwner(current: EdgeOwner | undefined): EdgeOwner | undefined {
  if (!current) return "self";
  if (current === "self") return "opponent";
  return undefined;
}

export function setEdgeClaim(
  claims: EdgeClaims,
  cityA: string,
  cityB: string,
  owner: EdgeOwner | undefined,
): EdgeClaims {
  const key = edgeKey(cityA, cityB);
  const next = { ...claims };
  if (owner) {
    next[key] = owner;
  } else {
    delete next[key];
  }
  return next;
}

export function countEdgeClaims(claims: EdgeClaims): { self: number; opponent: number } {
  let self = 0;
  let opponent = 0;
  for (const owner of Object.values(claims)) {
    if (owner === "self") self += 1;
    else if (owner === "opponent") opponent += 1;
  }
  return { self, opponent };
}

export function loadTripHand(): number[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(TRIP_HAND_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as unknown;
    if (!Array.isArray(parsed)) return [];
    return parsed.filter((id): id is number => typeof id === "number");
  } catch {
    return [];
  }
}

export function saveTripHand(tripIds: number[]): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(TRIP_HAND_KEY, JSON.stringify(tripIds));
}

export function addTripToHand(tripIds: number[], tripId: number): number[] {
  if (tripIds.includes(tripId) || tripIds.length >= MAX_TRIP_HAND) {
    return tripIds;
  }
  return [...tripIds, tripId];
}

export function removeTripFromHand(tripIds: number[], tripId: number): number[] {
  return tripIds.filter((id) => id !== tripId);
}
