"use client";

import { useMemo, useState } from "react";
import { formatCity } from "@/lib/coords";
import { MAX_TRIP_HAND } from "@/lib/gameState";
import type { Trip } from "@/lib/types";

type TripPickerProps = {
  trips: Trip[];
  selectedIds: number[];
  onAdd: (tripId: number) => void;
};

function formatTripLabel(trip: Trip): string {
  return `${formatCity(trip.start)} → ${formatCity(trip.end)}`;
}

function tripMatchesSearch(trip: Trip, query: string): boolean {
  const q = query.trim().toLowerCase();
  if (!q) return true;
  const haystack = `${formatTripLabel(trip)} ${trip.points}`.toLowerCase();
  return haystack.includes(q);
}

export function TripPicker({ trips, selectedIds, onAdd }: TripPickerProps) {
  const [search, setSearch] = useState("");
  const handFull = selectedIds.length >= MAX_TRIP_HAND;
  const selectedSet = useMemo(() => new Set(selectedIds), [selectedIds]);

  const available = useMemo(() => {
    return trips
      .filter((trip) => !selectedSet.has(trip.id))
      .filter((trip) => tripMatchesSearch(trip, search))
      .sort((a, b) => b.points - a.points || formatTripLabel(a).localeCompare(formatTripLabel(b)));
  }, [trips, selectedSet, search]);

  return (
    <section className="rounded-lg border border-slate-800 bg-slate-900/50 p-4">
      <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
        Add ticket
      </h2>

      <input
        type="search"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Search cities or points…"
        className="mt-3 w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
      />

      {handFull && (
        <p className="mt-2 text-xs text-amber-400">Hand full ({MAX_TRIP_HAND} max).</p>
      )}

      <ul className="mt-3 max-h-52 space-y-1 overflow-y-auto pr-1">
        {available.length === 0 ? (
          <li className="py-2 text-sm text-slate-500">
            {search.trim() ? "No tickets match your search." : "All tickets are in your hand."}
          </li>
        ) : (
          available.map((trip) => (
            <li key={trip.id}>
              <button
                type="button"
                disabled={handFull}
                onClick={() => onAdd(trip.id)}
                className="flex w-full items-center justify-between gap-2 rounded-md px-2 py-1.5 text-left text-sm text-slate-200 hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <span className="min-w-0 truncate">{formatTripLabel(trip)}</span>
                <span className="shrink-0 text-xs font-medium text-sky-400">
                  {trip.points} pts
                </span>
              </button>
            </li>
          ))
        )}
      </ul>
    </section>
  );
}
