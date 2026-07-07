export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 bg-zinc-950 px-6 text-zinc-50">
      <h1 className="text-3xl font-semibold">Ticket to Ride Route Planner</h1>
      <p className="max-w-lg text-center text-zinc-400">
        Interactive map coming soon. API is live — try{" "}
        <a className="text-sky-400 underline" href="/docs">
          /docs
        </a>{" "}
        or{" "}
        <a className="text-sky-400 underline" href="/health">
          /health
        </a>
        .
      </p>
    </main>
  );
}
