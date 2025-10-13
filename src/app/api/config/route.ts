import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    analyzeApiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/analyze'
  });
}
