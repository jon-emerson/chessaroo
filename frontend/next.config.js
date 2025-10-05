/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.API_URL || 'http://localhost:8000/api/:path*',
      },
      {
        source: '/admin/:path*',
        destination: process.env.API_URL
          ? `${process.env.API_URL}/admin/:path*`
          : 'http://localhost:8000/admin/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
