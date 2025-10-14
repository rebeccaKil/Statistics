'use client';

import { useEffect, useRef } from 'react';
import { getIconComponent } from '@/lib/iconUtils';
import { getShades } from '@/lib/colorUtils';
import { CumulativeData, hasMultipleDatasets } from '@/types';

interface CumulativeChartProps {
  title: string;
  icon: string;
  color: string;
  data: CumulativeData;
}

type ChartInstance = {
  destroy: () => void;
};

export function CumulativeChart({ title, icon, color, data }: CumulativeChartProps) {
  const IconComponent = getIconComponent(icon);
  const shades = getShades(color);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef = useRef<ChartInstance | null>(null);

  const isMulti = hasMultipleDatasets(data);

  useEffect(() => {
    if (!canvasRef.current || !data) return;
    const load = async () => {
      const Chart = (await import('chart.js/auto')).default;
      const ChartDataLabels = (await import('chartjs-plugin-datalabels')).default;
      const { getShades } = await import('@/lib/colorUtils');
      if (chartRef.current) chartRef.current.destroy();
      const ctx = canvasRef.current!.getContext('2d')!;

      // 색상 팔레트 (다양한 색상)
      const colorPalette = ['indigo', 'blue', 'green', 'yellow', 'orange', 'red', 'pink', 'purple', 'cyan', 'teal'];

      const datasets = isMulti
        ? [
            ...(data.bars || []).map((b, i) => {
              const itemColor = b.color || colorPalette[i % colorPalette.length];
              const itemShades = getShades(itemColor);
              return {
                type: 'bar' as const,
                label: b.label,
                data: b.values,
                backgroundColor: itemShades.bar400,
                borderRadius: 4,
                yAxisID: 'y',
                datalabels: {
                  anchor: 'center' as const,
                  align: 'center' as const,
                  color: '#ffffff',
                  font: { size: 11, weight: 'bold' as const },
                  formatter: (v: number) => v ? v : ''
                }
              };
            }),
            ...(data.lines || []).map((l, i) => {
              const itemColor = l.color || colorPalette[((data.bars?.length || 0) + i) % colorPalette.length];
              const itemShades = getShades(itemColor);
              return {
                type: 'line' as const,
                label: l.label,
                data: l.values,
                borderColor: itemShades.text600,
                backgroundColor: 'transparent',
                tension: 0.3,
                pointRadius: 4,
                pointBackgroundColor: itemShades.text600,
                yAxisID: 'y1',
                datalabels: {
                  anchor: 'end' as const,
                  align: 'top' as const,
                  offset: 4,
                  color: itemShades.text600,
                  font: { size: 11, weight: 'bold' as const },
                  formatter: (v: number) => v ? v : ''
                }
              };
            })
          ]
        : [
            {
              type: 'bar' as const,
              label: '월별 값',
              data: data.map(d => d.count),
              backgroundColor: shades.bar400,
              borderRadius: 4,
              yAxisID: 'y',
              datalabels: {
                anchor: 'center' as const,
                align: 'center' as const,
                color: '#ffffff',
                font: { size: 11, weight: 'bold' as const },
                formatter: (v: number) => v ? v : ''
              }
            },
            {
              type: 'line' as const,
              label: '누적 합계',
              data: data.map(d => d.cumulative),
              borderColor: shades.text600,
              backgroundColor: 'transparent',
              tension: 0.3,
              pointRadius: 4,
              pointBackgroundColor: shades.text600,
              yAxisID: 'y1',
              datalabels: {
                anchor: 'end' as const,
                align: 'top' as const,
                offset: 4,
                color: shades.text600,
                font: { size: 11, weight: 'bold' as const },
                formatter: (v: number) => v ? v : ''
              }
            }
          ];

      chartRef.current = new Chart(ctx, {
        type: 'bar',
        plugins: [ChartDataLabels],
        data: {
          labels: isMulti ? data.labels : data.map(d => d.name),
          datasets
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: { mode: 'index', intersect: false },
          plugins: {
            legend: { position: 'top' },
            datalabels: {
              display: true
            }
          },
          scales: {
            y: { beginAtZero: true, grid: { color: '#e2e8f0' } },
            y1: { beginAtZero: true, position: 'right', grid: { drawOnChartArea: false } }
          }
        }
      }) as ChartInstance;
    };
    load();
    return () => { if (chartRef.current) chartRef.current.destroy(); };
  }, [data, isMulti, shades.bar400, shades.text600]);

  if (!data || (!isMulti && data.length === 0)) {
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


