import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 정적 사이트 빌드를 위한 설정
  output: 'export',
  trailingSlash: true,
  distDir: 'out',
  
  // 이미지 최적화 설정
  images: {
    unoptimized: true, // 정적 빌드에서 이미지 최적화 비활성화
  },
};

export default nextConfig;
