import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Monorepo: Next.js lives in frontend/, deployed from repo root on Vercel.
  distDir: ".next",
};

export default nextConfig;
