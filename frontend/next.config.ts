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

const nextConfig: NextConfig = {
  async rewrites() {
    // Local dev only — production uses Vercel Services on the same domain.
    if (process.env.NODE_ENV !== "development") return [];
    return API_PATHS.map((path) => ({
      source: path,
      destination: `${API_DEV}${path}`,
    }));
  },
};

export default nextConfig;
