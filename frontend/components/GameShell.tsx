"use client";

import { useEffect, useState } from "react";
import { checkApiHealth, loadBoardData } from "@/lib/api";
import type { BoardData } from "@/lib/types";
import { MapBoard } from "./MapBoard";
import { Sidebar } from "./Sidebar";

export function GameShell() {
  const [board, setBoard] = useState<BoardData | null>(null);
  const [dataSource, setDataSource] = useState<"api" | "static">("static");
  const [apiOnline, setApiOnline] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function init() {
      const [health, boardResult] = await Promise.all([
        checkApiHealth(),
        loadBoardData(),
      ]);
      if (cancelled) return;
      setApiOnline(health);
      setBoard(boardResult.data);
      setDataSource(boardResult.source);
      setLoading(false);
    }

    init();
    return () => {
      cancelled = true;
    };
  }, []);

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
        <MapBoard cities={board.cities} tracks={board.tracks} />
      </main>
      <Sidebar
        apiOnline={apiOnline}
        dataSource={dataSource}
        cityCount={board.cities.length}
        trackCount={board.tracks.length}
      />
    </div>
  );
}
