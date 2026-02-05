import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  experimental: {
    serverActions: {
      allowedOrigins: ["localhost:3000", "26.26.26.1:3000"],
    },
  },
};
export default nextConfig;
