"use client";

import { useMemo, useState } from "react";
import { edgeKey, getViewBox, layoutCities } from "@/lib/coords";
import { cycleEdgeOwner } from "@/lib/gameState";
import type { City, EdgeClaims, EdgeOwner, RouteResult, Track } from "@/lib/types";

type HoverEdge = Track & { key: string };
type HoverCity = City;

type MapBoardProps = {
  cities: City[];
  tracks: Track[];
  edgeClaims: EdgeClaims;
  onEdgeClaimsChange: (claims: EdgeClaims) => void;
  routes: RouteResult[];
};

const EDGE_COLORS = {
  unclaimed: "#3d4f5f",
  self: "#3b82f6",
  opponent: "#ef4444",
  hover: "#38bdf8",
} as const;

const ROUTE_COLORS = [
  "#facc15",
  "#34d399",
  "#c084fc",
  "#f472b6",
  "#22d3ee",
  "#fb923c",
  "#a3e635",
  "#f87171",
  "#818cf8",
  "#2dd4bf",
];

function edgeStroke(
  owner: EdgeOwner | undefined,
  hovered: boolean,
): { color: string; width: number } {
  if (owner === "self") return { color: EDGE_COLORS.self, width: 4 };
  if (owner === "opponent") return { color: EDGE_COLORS.opponent, width: 4 };
  if (hovered) return { color: EDGE_COLORS.hover, width: 4 };
  return { color: EDGE_COLORS.unclaimed, width: 2.5 };
}

function ownerLabel(owner: EdgeOwner | undefined): string {
  if (owner === "self") return "Yours";
  if (owner === "opponent") return "Opponent";
  return "Unclaimed";
}

export function MapBoard({
  cities,
  tracks,
  edgeClaims,
  onEdgeClaimsChange,
  routes,
}: MapBoardProps) {
  const positions = useMemo(() => layoutCities(cities), [cities]);
  const [hoverEdge, setHoverEdge] = useState<HoverEdge | null>(null);
  const [hoverCity, setHoverCity] = useState<HoverCity | null>(null);

  function handleEdgeClick(track: Track) {
    const key = edgeKey(track.city_a, track.city_b);
    const nextOwner = cycleEdgeOwner(edgeClaims[key]);
    const next = { ...edgeClaims };
    if (nextOwner) {
      next[key] = nextOwner;
    } else {
      delete next[key];
    }
    onEdgeClaimsChange(next);
  }

  return (
    <div className="relative h-full w-full">
      <svg
        viewBox={getViewBox()}
        className="h-full w-full select-none"
        role="img"
        aria-label="Ticket to Ride board map"
      >
        <rect width="100%" height="100%" fill="#0f1419" rx="8" />

        {tracks.map((track) => {
          const a = positions.get(track.city_a);
          const b = positions.get(track.city_b);
          if (!a || !b) return null;
          const key = edgeKey(track.city_a, track.city_b);
          const owner = edgeClaims[key];
          const hovered = hoverEdge?.key === key;
          const { color, width } = edgeStroke(owner, hovered);

          return (
            <g key={key}>
              <line
                x1={a.x}
                y1={a.y}
                x2={b.x}
                y2={b.y}
                stroke="transparent"
                strokeWidth={16}
                className="cursor-pointer"
                onMouseEnter={() => setHoverEdge({ ...track, key })}
                onMouseLeave={() => setHoverEdge((h) => (h?.key === key ? null : h))}
                onClick={() => handleEdgeClick(track)}
              />
              <line
                x1={a.x}
                y1={a.y}
                x2={b.x}
                y2={b.y}
                stroke={color}
                strokeWidth={width}
                strokeLinecap="round"
                pointerEvents="none"
              />
            </g>
          );
        })}

        {routes.map((route, routeIndex) => {
          if (route.path.length < 2) return null;
          const color = ROUTE_COLORS[routeIndex % ROUTE_COLORS.length];
          return (
            <g key={`route-${routeIndex}`} opacity={0.85}>
              {route.path.slice(0, -1).map((city, segmentIndex) => {
                const next = route.path[segmentIndex + 1];
                const a = positions.get(city);
                const b = positions.get(next);
                if (!a || !b) return null;
                return (
                  <line
                    key={`${city}-${next}`}
                    x1={a.x}
                    y1={a.y}
                    x2={b.x}
                    y2={b.y}
                    stroke={color}
                    strokeWidth={5}
                    strokeLinecap="round"
                    pointerEvents="none"
                  />
                );
              })}
            </g>
          );
        })}

        {cities.map((city) => {
          const pos = positions.get(city.name);
          if (!pos) return null;
          const active = hoverCity?.name === city.name;

          return (
            <g
              key={city.name}
              onMouseEnter={() => setHoverCity(city)}
              onMouseLeave={() => setHoverCity((h) => (h?.name === city.name ? null : h))}
            >
              <circle
                cx={pos.x}
                cy={pos.y}
                r={active ? 11 : 8}
                fill={active ? "#38bdf8" : "#1e293b"}
                stroke={active ? "#7dd3fc" : "#64748b"}
                strokeWidth={2}
              />
              <text
                x={pos.x}
                y={pos.y - 14}
                textAnchor="middle"
                fill={active ? "#f1f5f9" : "#94a3b8"}
                fontSize={11}
                fontWeight={active ? 600 : 500}
                pointerEvents="none"
              >
                {city.name.replace(/-/g, " ")}
              </text>
            </g>
          );
        })}
      </svg>

      {(hoverEdge || hoverCity) && (
        <div className="pointer-events-none absolute bottom-4 left-4 max-w-xs rounded-lg border border-slate-700 bg-slate-900/95 px-3 py-2 text-sm text-slate-200 shadow-lg backdrop-blur">
          {hoverEdge && (
            <>
              <p className="font-medium text-sky-300">
                {hoverEdge.city_a.replace(/-/g, " ")} ↔{" "}
                {hoverEdge.city_b.replace(/-/g, " ")}
              </p>
              <p className="text-slate-400">
                {hoverEdge.train_cost} trains · {hoverEdge.route_points} route pts
              </p>
              <p className="text-slate-500">{ownerLabel(edgeClaims[hoverEdge.key])}</p>
            </>
          )}
          {hoverCity && !hoverEdge && (
            <>
              <p className="font-medium text-sky-300">
                {hoverCity.name.replace(/-/g, " ")}
              </p>
              <p className="text-slate-400">City</p>
            </>
          )}
        </div>
      )}
    </div>
  );
}
