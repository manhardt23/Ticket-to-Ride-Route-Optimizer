import { EdgeLegend } from "./EdgeLegend";
import { TripHand } from "./TripHand";
import { TripPicker } from "./TripPicker";
import type { Trip } from "@/lib/types";

type SidebarProps = {
  apiOnline: boolean;
  dataSource: "api" | "static";
  cityCount: number;
  trackCount: number;
  selfClaimCount: number;
  opponentClaimCount: number;
  onClearClaims: () => void;
  trips: Trip[];
  selectedTripIds: number[];
  onAddTrip: (tripId: number) => void;
  onRemoveTrip: (tripId: number) => void;
};

export function Sidebar({
  apiOnline,
  dataSource,
  cityCount,
  trackCount,
  selfClaimCount,
  opponentClaimCount,
  onClearClaims,
  trips,
  selectedTripIds,
  onAddTrip,
  onRemoveTrip,
}: SidebarProps) {
  return (
    <aside className="flex w-80 shrink-0 flex-col gap-4 overflow-y-auto border-l border-slate-800 bg-slate-950 p-5 min-h-0">
      <header>
        <h1 className="text-lg font-semibold text-slate-100">Route Planner</h1>
        <p className="mt-1 text-sm text-slate-400">
          Plan routes around claimed track and your tickets.
        </p>
      </header>

      <section className="rounded-lg border border-slate-800 bg-slate-900/50 p-4">
        <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
          Status
        </h2>
        <dl className="mt-3 space-y-2 text-sm">
          <div className="flex justify-between">
            <dt className="text-slate-400">API</dt>
            <dd className={apiOnline ? "text-emerald-400" : "text-amber-400"}>
              {apiOnline ? "Online" : "Offline (static data)"}
            </dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-slate-400">Board data</dt>
            <dd className="text-slate-200">{dataSource}</dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-slate-400">Cities</dt>
            <dd className="text-slate-200">{cityCount}</dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-slate-400">Routes</dt>
            <dd className="text-slate-200">{trackCount}</dd>
          </div>
        </dl>
        {!apiOnline && (
          <p className="mt-3 text-xs text-amber-500/90">
            API unreachable on this domain. Redeploy from repo root (blank Root
            Directory) so FastAPI and the static map share one URL.
          </p>
        )}
      </section>

      <EdgeLegend
        selfCount={selfClaimCount}
        opponentCount={opponentClaimCount}
        onClearAll={onClearClaims}
      />

      <TripHand trips={trips} selectedIds={selectedTripIds} onRemove={onRemoveTrip} />

      <TripPicker trips={trips} selectedIds={selectedTripIds} onAdd={onAddTrip} />
    </aside>
  );
}
