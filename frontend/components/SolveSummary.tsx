import { formatCity } from "@/lib/coords";
import type { SolveResponse } from "@/lib/types";

const TOTAL_TRAINS = 45;

type SolveSummaryProps = {
  hasTrips: boolean;
  solveResult: SolveResponse | null;
  solving: boolean;
  solveError: string | null;
};

export function SolveSummary({ hasTrips, solveResult, solving, solveError }: SolveSummaryProps) {
  if (!hasTrips) return null;

  const overTrainLimit = (solveResult?.trains_used ?? 0) > TOTAL_TRAINS;
  const hasWarnings =
    solveResult != null &&
    (overTrainLimit || solveResult.unreachable.length > 0 || solveResult.unused_mandatory.length > 0);

  return (
    <section className="rounded-lg border border-slate-800 bg-slate-900/50 p-4">
      <div className="flex items-center justify-between gap-2">
        <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
          Solve results
        </h2>
        {solving && <span className="text-xs text-slate-500">Solving…</span>}
      </div>

      {solveError && <p className="mt-2 text-sm text-red-400">{solveError}</p>}

      {solveResult && !solveError && (
        <>
          <dl className="mt-3 space-y-2 text-sm">
            <div className="flex justify-between">
              <dt className="text-slate-400">Total points</dt>
              <dd className="font-medium text-slate-100">{solveResult.points}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-slate-400">Trains used</dt>
              <dd className={overTrainLimit ? "font-medium text-red-400" : "text-slate-200"}>
                {solveResult.trains_used}/{TOTAL_TRAINS}
              </dd>
            </div>
          </dl>

          {hasWarnings && (
            <ul className="mt-3 space-y-1.5 text-xs text-amber-400">
              {overTrainLimit && <li>⚠ Over the {TOTAL_TRAINS}-train limit.</li>}
              {solveResult.unreachable.length > 0 && (
                <li>
                  ⚠ {solveResult.unreachable.length} ticket
                  {solveResult.unreachable.length === 1 ? "" : "s"} unreachable due to opponent
                  blocks.
                </li>
              )}
              {solveResult.unused_mandatory.map(([a, b]) => (
                <li key={`${a}-${b}`}>
                  ⚠ {formatCity(a)} ↔ {formatCity(b)} claimed but unused by any route.
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </section>
  );
}
