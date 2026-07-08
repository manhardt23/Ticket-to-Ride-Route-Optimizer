import { formatCity } from "@/lib/coords";
import { MAX_TRIP_HAND } from "@/lib/gameState";
import type { Trip } from "@/lib/types";

type TripHandProps = {
  trips: Trip[];
  selectedIds: number[];
  onRemove: (tripId: number) => void;
};

function formatTripLabel(trip: Trip): string {
  return `${formatCity(trip.start)} → ${formatCity(trip.end)}`;
}

export function TripHand({ trips, selectedIds, onRemove }: TripHandProps) {
  const byId = new Map(trips.map((trip) => [trip.id, trip]));
  const hand = selectedIds
    .map((id) => byId.get(id))
    .filter((trip): trip is Trip => trip != null);
  const totalPoints = hand.reduce((sum, trip) => sum + trip.points, 0);

  return (
    <section className="rounded-lg border border-slate-800 bg-slate-900/50 p-4">
      <div className="flex items-center justify-between gap-2">
        <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
          Your tickets
        </h2>
        <span className="text-xs text-slate-500">
          {hand.length}/{MAX_TRIP_HAND}
        </span>
      </div>

      {hand.length === 0 ? (
        <p className="mt-2 text-sm text-slate-500">No tickets yet. Add from the list below.</p>
      ) : (
        <>
          <ul className="mt-3 space-y-1">
            {hand.map((trip) => (
              <li
                key={trip.id}
                className="flex items-center justify-between gap-2 rounded-md bg-slate-950/60 px-2 py-1.5 text-sm"
              >
                <span className="min-w-0 truncate text-slate-200">{formatTripLabel(trip)}</span>
                <div className="flex shrink-0 items-center gap-2">
                  <span className="text-xs font-medium text-sky-400">{trip.points} pts</span>
                  <button
                    type="button"
                    onClick={() => onRemove(trip.id)}
                    className="rounded px-1 text-slate-500 hover:bg-slate-800 hover:text-slate-200"
                    aria-label={`Remove ${formatTripLabel(trip)}`}
                  >
                    ✕
                  </button>
                </div>
              </li>
            ))}
          </ul>
          <p className="mt-3 text-xs text-slate-400">
            Ticket points: <span className="font-medium text-slate-200">{totalPoints}</span>
          </p>
        </>
      )}
    </section>
  );
}
