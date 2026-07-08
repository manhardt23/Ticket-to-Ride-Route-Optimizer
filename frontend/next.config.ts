import type { NextConfig } from "next";

const API_DEV = "http://127.0.0.1:8000";

const API_PATHS = [
  "/health",
  "/cities",
  "/tracks",
  "/trips",
  "/solve",
  "/solve/best",
  "/docs",
  "/openapi.json",
];

function resolveApiBase(): string | null {
  const configured =
    process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? null;
  if (configured) return configured.replace(/\/$/, "");
  if (process.env.NODE_ENV === "development") return API_DEV;
  return null;
}

const nextConfig: NextConfig = {
  async rewrites() {
    const apiBase = resolveApiBase();
    if (!apiBase) return [];
    return API_PATHS.map((path) => ({
      source: path,
      destination: `${apiBase}${path}`,
    }));
  },
};

export default nextConfig;
