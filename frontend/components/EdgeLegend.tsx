type EdgeLegendProps = {
  selfCount: number;
  opponentCount: number;
  onClearAll: () => void;
};

export function EdgeLegend({ selfCount, opponentCount, onClearAll }: EdgeLegendProps) {
  const hasClaims = selfCount > 0 || opponentCount > 0;

  return (
    <section className="rounded-lg border border-slate-800 bg-slate-900/50 p-4">
      <div className="flex items-center justify-between gap-2">
        <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
          Edge claims
        </h2>
        {hasClaims && (
          <button
            type="button"
            onClick={onClearAll}
            className="text-xs text-slate-400 underline-offset-2 hover:text-slate-200 hover:underline"
          >
            Clear all
          </button>
        )}
      </div>

      <ul className="mt-3 space-y-2 text-sm text-slate-300">
        <li className="flex items-center gap-2">
          <span className="h-0.5 w-8 rounded bg-slate-500" />
          Unclaimed
        </li>
        <li className="flex items-center gap-2">
          <span className="h-1 w-8 rounded bg-blue-500" />
          Yours (mandatory)
        </li>
        <li className="flex items-center gap-2">
          <span className="h-1 w-8 rounded bg-red-500" />
          Opponent (blocked)
        </li>
      </ul>

      <p className="mt-3 text-xs text-slate-500">Click a route to cycle ownership.</p>

      {hasClaims && (
        <dl className="mt-3 space-y-1 text-xs text-slate-400">
          <div className="flex justify-between">
            <dt>Yours</dt>
            <dd className="text-blue-400">{selfCount}</dd>
          </div>
          <div className="flex justify-between">
            <dt>Opponent</dt>
            <dd className="text-red-400">{opponentCount}</dd>
          </div>
        </dl>
      )}
    </section>
  );
}
