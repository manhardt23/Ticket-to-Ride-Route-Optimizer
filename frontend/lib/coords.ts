import type { City } from "./types";

const VIEW_WIDTH = 1000;
const VIEW_HEIGHT = 700;
const PADDING = 48;

export function getViewBox() {
  return `0 0 ${VIEW_WIDTH} ${VIEW_HEIGHT}`;
}

/** Map geographic coords to SVG space (north = up). */
export function layoutCities(cities: City[]): Map<string, { x: number; y: number }> {
  const positioned = cities.filter((c) => c.x != null && c.y != null) as Array<
    City & { x: number; y: number }
  >;

  const xs = positioned.map((c) => c.x);
  const ys = positioned.map((c) => c.y);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  const spanX = maxX - minX || 1;
  const spanY = maxY - minY || 1;

  const innerW = VIEW_WIDTH - PADDING * 2;
  const innerH = VIEW_HEIGHT - PADDING * 2;

  const positions = new Map<string, { x: number; y: number }>();
  for (const city of positioned) {
    positions.set(city.name, {
      x: PADDING + ((city.x - minX) / spanX) * innerW,
      y: PADDING + (1 - (city.y - minY) / spanY) * innerH,
    });
  }
  return positions;
}

export function edgeKey(a: string, b: string): string {
  return [a, b].sort().join("|");
}

export function formatCity(name: string): string {
  return name.replace(/-/g, " ");
}
