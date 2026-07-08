"use client";

import { useEffect, useState } from "react";
import { checkApiHealth, loadBoardData, loadTrips, solveHand } from "@/lib/api";
import {
  addTripToHand,
  clearEdgeClaims,
  countEdgeClaims,
  edgeClaimsToPayload,
  loadEdgeClaims,
  loadTripHand,
  removeTripFromHand,
  saveEdgeClaims,
  saveTripHand,
} from "@/lib/gameState";
import type { BoardData, EdgeClaims, SolveResponse, Trip } from "@/lib/types";
import { MapBoard } from "./MapBoard";
import { Sidebar } from "./Sidebar";

const SOLVE_DEBOUNCE_MS = 300;

export function GameShell() {
  const [board, setBoard] = useState<BoardData | null>(null);
  const [trips, setTrips] = useState<Trip[]>([]);
  const [dataSource, setDataSource] = useState<"api" | "static">("static");
  const [apiOnline, setApiOnline] = useState(false);
  const [loading, setLoading] = useState(true);
  const [edgeClaims, setEdgeClaims] = useState<EdgeClaims>({});
  const [selectedTripIds, setSelectedTripIds] = useState<number[]>([]);
  const [solveResult, setSolveResult] = useState<SolveResponse | null>(null);
  const [solving, setSolving] = useState(false);
  const [solveError, setSolveError] = useState<string | null>(null);

  useEffect(() => {
    setEdgeClaims(loadEdgeClaims());
    setSelectedTripIds(loadTripHand());
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function init() {
      const [health, boardResult, tripsResult] = await Promise.all([
        checkApiHealth(),
        loadBoardData(),
        loadTrips(),
      ]);
      if (cancelled) return;
      setApiOnline(health);
      setBoard(boardResult.data);
      setTrips(tripsResult.trips);
      setDataSource(boardResult.source === "api" && tripsResult.source === "api" ? "api" : "static");
      setLoading(false);
    }

    init();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (selectedTripIds.length === 0) {
      setSolveResult(null);
      setSolveError(null);
      setSolving(false);
      return;
    }

    const controller = new AbortController();
    setSolving(true);
    const timer = setTimeout(() => {
      solveHand(selectedTripIds, edgeClaimsToPayload(edgeClaims), controller.signal)
        .then((result) => {
          setSolveResult(result);
          setSolveError(null);
        })
        .catch((err: unknown) => {
          if (err instanceof DOMException && err.name === "AbortError") return;
          setSolveResult(null);
          setSolveError(err instanceof Error ? err.message : "Solve failed");
        })
        .finally(() => setSolving(false));
    }, SOLVE_DEBOUNCE_MS);

    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [selectedTripIds, edgeClaims]);

  function handleEdgeClaimsChange(claims: EdgeClaims) {
    setEdgeClaims(claims);
    saveEdgeClaims(claims);
  }

  function handleClearClaims() {
    handleEdgeClaimsChange(clearEdgeClaims());
  }

  function handleAddTrip(tripId: number) {
    setSelectedTripIds((prev) => {
      const next = addTripToHand(prev, tripId);
      saveTripHand(next);
      return next;
    });
  }

  function handleRemoveTrip(tripId: number) {
    setSelectedTripIds((prev) => {
      const next = removeTripFromHand(prev, tripId);
      saveTripHand(next);
      return next;
    });
  }

  const claimCounts = countEdgeClaims(edgeClaims);

  if (loading) {
    return (
      <div className="flex flex-1 items-center justify-center bg-slate-950 text-slate-400">
        Loading board…
      </div>
    );
  }

  if (!board) {
    return (
      <div className="flex flex-1 items-center justify-center bg-slate-950 text-red-400">
        Failed to load board data.
      </div>
    );
  }

  return (
    <div className="flex h-screen min-h-0 flex-col bg-slate-950 lg:flex-row">
      <main className="min-h-0 flex-1 p-4">
        <MapBoard
          cities={board.cities}
          tracks={board.tracks}
          edgeClaims={edgeClaims}
          onEdgeClaimsChange={handleEdgeClaimsChange}
          routes={solveResult?.routes ?? []}
        />
      </main>
      <Sidebar
        apiOnline={apiOnline}
        dataSource={dataSource}
        cityCount={board.cities.length}
        trackCount={board.tracks.length}
        selfClaimCount={claimCounts.self}
        opponentClaimCount={claimCounts.opponent}
        onClearClaims={handleClearClaims}
        trips={trips}
        selectedTripIds={selectedTripIds}
        onAddTrip={handleAddTrip}
        onRemoveTrip={handleRemoveTrip}
        solveResult={solveResult}
        solving={solving}
        solveError={solveError}
      />
    </div>
  );
}
