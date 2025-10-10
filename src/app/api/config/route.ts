import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    analyzeApiUrl: process.env.NEXT_PUBLIC_ANALYZE_API_URL || ''
  });
}
