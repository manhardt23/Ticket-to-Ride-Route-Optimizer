"use client";

import { useMemo, useState } from "react";
import type { City, Track } from "@/lib/types";
import { edgeKey, getViewBox, layoutCities } from "@/lib/coords";

type HoverEdge = Track & { key: string };
type HoverCity = City;

type MapBoardProps = {
  cities: City[];
  tracks: Track[];
};

export function MapBoard({ cities, tracks }: MapBoardProps) {
  const positions = useMemo(() => layoutCities(cities), [cities]);
  const [hoverEdge, setHoverEdge] = useState<HoverEdge | null>(null);
  const [hoverCity, setHoverCity] = useState<HoverCity | null>(null);

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
          const active = hoverEdge?.key === key;

          return (
            <g key={key}>
              <line
                x1={a.x}
                y1={a.y}
                x2={b.x}
                y2={b.y}
                stroke="transparent"
                strokeWidth={16}
                onMouseEnter={() => setHoverEdge({ ...track, key })}
                onMouseLeave={() => setHoverEdge((h) => (h?.key === key ? null : h))}
              />
              <line
                x1={a.x}
                y1={a.y}
                x2={b.x}
                y2={b.y}
                stroke={active ? "#38bdf8" : "#3d4f5f"}
                strokeWidth={active ? 4 : 2.5}
                strokeLinecap="round"
                pointerEvents="none"
              />
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
