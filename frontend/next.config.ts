import type { NextConfig } from "next";

const API_DEV = "http://127.0.0.1:8000";

const apiPaths = ["/health", "/cities", "/tracks", "/trips", "/solve", "/docs", "/openapi.json"];

const nextConfig: NextConfig = {
  async rewrites() {
    if (process.env.NODE_ENV !== "development") return [];
    return apiPaths.map((path) => ({
      source: path,
      destination: `${API_DEV}${path}`,
    }));
  },
};

export default nextConfig;
