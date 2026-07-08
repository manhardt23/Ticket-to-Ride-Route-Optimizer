type SidebarProps = {
  apiOnline: boolean;
  dataSource: "api" | "static";
  cityCount: number;
  trackCount: number;
};

export function Sidebar({
  apiOnline,
  dataSource,
  cityCount,
  trackCount,
}: SidebarProps) {
  return (
    <aside className="flex w-80 shrink-0 flex-col gap-6 border-l border-slate-800 bg-slate-950 p-5">
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
      </section>

      <section className="rounded-lg border border-slate-800 bg-slate-900/50 p-4">
        <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
          Legend
        </h2>
        <ul className="mt-3 space-y-2 text-sm text-slate-300">
          <li className="flex items-center gap-2">
            <span className="h-0.5 w-8 rounded bg-slate-500" />
            Unclaimed route
          </li>
          <li className="flex items-center gap-2">
            <span className="h-1 w-8 rounded bg-sky-400" />
            Hover / highlight
          </li>
        </ul>
        <p className="mt-4 text-xs text-slate-500">
          Click-to-claim edges and trip hand coming in the next phase.
        </p>
        {!apiOnline && (
          <p className="mt-3 text-xs text-amber-500/90">
            API unreachable on this domain. Redeploy from repo root (blank Root
            Directory) so FastAPI and the static map share one URL.
          </p>
        )}
      </section>

      <section className="mt-auto rounded-lg border border-dashed border-slate-700 p-4">
        <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
          Your tickets
        </h2>
        <p className="mt-2 text-sm text-slate-500">No tickets yet.</p>
      </section>
    </aside>
  );
}
