import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  experimental: {
    // Suppress "Cross origin request detected" warning for this specific IP
    allowedDevOrigins: ["localhost:3000", "26.26.26.1:3000"],
  },
};
export default nextConfig;
