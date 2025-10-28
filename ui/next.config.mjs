/** @type {import('next').NextConfig} */
const nextConfig = {
  devIndicators: false,
  // Proxy /chat requests to the backend server
  async rewrites() {
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000";
    return [
      {
        source: "/chat",
        destination: `${backendUrl}/chat`,
      },
    ];
  },
};

export default nextConfig;
