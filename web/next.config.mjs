/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // ESLint nitpicks must never block a hackathon demo build. Type checking
  // stays ON (correctness), only lint is skipped during `next build`.
  eslint: {
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;
