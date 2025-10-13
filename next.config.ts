import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 정적 사이트 빌드를 위한 설정
  output: 'export',
  trailingSlash: true,
  distDir: 'out',
  
  // 이미지 최적화 설정
  images: {
    unoptimized: true, // Vercel에서 이미지 최적화 비활성화 (필요시)
  },
  
  // 환경변수 설정 제거 (Gemini 미사용)
  
  // 보안 헤더 설정
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ];
  },
};

export default nextConfig;
