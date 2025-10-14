'use client';

import { useEffect, useRef } from 'react';
import { getIconComponent } from '@/lib/iconUtils';
import { getShades } from '@/lib/colorUtils';

interface CumulativeChartProps {
  title: string;
  icon: string;
  color: string;
  data:
    | Array<{ name: string; count: number; cumulative: number }>
    | { labels: string[]; bars: Array<{ label: string; values: number[] }>; lines: Array<{ label: string; values: number[] }>; lineCumulative?: boolean };
}

export function CumulativeChart({ title, icon, color, data }: CumulativeChartProps) {
  const IconComponent = getIconComponent(icon);
  const shades = getShades(color);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef = useRef<{ destroy: () => void } | null>(null);

  const isMulti = !!(data as any)?.labels;

  useEffect(() => {
    if (!canvasRef.current || !data) return;
    const load = async () => {
      const Chart = (await import('chart.js/auto')).default;
      const ChartDataLabels = (await import('chartjs-plugin-datalabels')).default;
      if (chartRef.current) chartRef.current.destroy();
      const ctx = canvasRef.current!.getContext('2d')!;

      const datasets = isMulti
        ? [
            ...((data as any).bars || []).map((b: any, i: number) => ({
              type: 'bar' as const,
              label: b.label,
              data: b.values,
              backgroundColor: shades.bar400,
              borderRadius: 4,
              yAxisID: 'y'
            })),
            ...((data as any).lines || []).map((l: any, i: number) => ({
              type: 'line' as const,
              label: l.label,
              data: l.values,
              borderColor: shades.text600,
              backgroundColor: 'transparent',
              tension: 0.3,
              pointRadius: 3,
              yAxisID: 'y1'
            }))
          ]
        : [
            {
              type: 'bar' as const,
              label: '월별 값',
              data: (data as any).map((d: any) => d.count),
              backgroundColor: shades.bar400,
              borderRadius: 4,
              yAxisID: 'y',
            },
            {
              type: 'line' as const,
              label: '누적 합계',
              data: (data as any).map((d: any) => d.cumulative),
              borderColor: shades.text600,
              backgroundColor: 'transparent',
              tension: 0.3,
              pointRadius: 3,
              yAxisID: 'y1',
            }
          ];

      chartRef.current = new Chart(ctx, {
        type: 'bar',
        plugins: [ChartDataLabels],
        data: {
          labels: isMulti ? (data as any).labels : (data as any).map((d: any) => d.name),
          datasets
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: { mode: 'index', intersect: false },
          plugins: {
            legend: { position: 'top' },
            datalabels: {
              anchor: 'end', align: 'top', color: '#475569', font: { size: 10, weight: 'bold' },
              formatter: (v) => v ? v : ''
            }
          },
          scales: {
            y: { beginAtZero: true, grid: { color: '#e2e8f0' } },
            y1: { beginAtZero: true, position: 'right', grid: { drawOnChartArea: false } }
          }
        }
      });
    };
    load();
    return () => { if (chartRef.current) chartRef.current.destroy(); };
  }, [data, color, isMulti]);

  if (!data || (!isMulti && (data as any).length === 0)) {
    return (
      <section className="bg-white rounded-2xl shadow-lg p-6">
        <div className="flex items-center mb-4">
          <div className="p-3 rounded-full" style={{ backgroundColor: shades.bg100 }}>
            <IconComponent className="h-6 w-6" style={{ color: shades.text600 }} />
          </div>
          <h2 className="text-xl font-bold text-slate-800 ml-4">{title}</h2>
        </div>
        <p className="text-slate-500">데이터가 없습니다.</p>
      </section>
    );
  }

  return (
    <section className="bg-white rounded-2xl shadow-lg p-6">
      <div className="flex items-center mb-6">
        <div className="p-3 rounded-full" style={{ backgroundColor: shades.bg100 }}>
          <IconComponent className="h-6 w-6" style={{ color: shades.text600 }} />
        </div>
        <h2 className="text-xl font-bold text-slate-800 ml-4">{title}</h2>
      </div>
      <div style={{ height: '360px' }}>
        <canvas ref={canvasRef}></canvas>
      </div>
    </section>
  );
}


