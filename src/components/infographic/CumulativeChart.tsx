'use client';

import { useMemo } from 'react';
import { getShades } from '@/lib/colorUtils';
import { CumulativeData, hasMultipleDatasets } from '@/types';
import { InfographicCard } from '../common/InfographicCard';
import { useChart } from '@/hooks/useChart';
import type { ChartConfiguration } from 'chart.js';

interface CumulativeChartProps {
  title: string;
  icon: string;
  color: string;
  data: CumulativeData;
}

export function CumulativeChart({ title, icon, color, data }: CumulativeChartProps) {
  const shades = getShades(color);
  const isMulti = hasMultipleDatasets(data);
  const isEmpty = !data || (!isMulti && data.length === 0);

  const chartConfig: ChartConfiguration = useMemo(() => {
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

    return {
      type: 'bar',
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
          datalabels: { display: true }
        },
        scales: {
          y: { beginAtZero: true, grid: { color: '#e2e8f0' } },
          y1: { beginAtZero: true, position: 'right', grid: { drawOnChartArea: false } }
        }
      }
    };
  }, [data, isMulti, shades]);

  const canvasRef = useChart(chartConfig, [chartConfig]);

  if (isEmpty) {
    return <InfographicCard title={title} icon={icon} color={color} isEmpty />;
  }

  return (
    <InfographicCard title={title} icon={icon} color={color}>
      <div style={{ height: '360px' }}>
        <canvas ref={canvasRef}></canvas>
      </div>
    </InfographicCard>
  );
}
