'use client';

import { useEffect, useRef } from 'react';
import { getIconComponent } from '@/lib/iconUtils';
import { getShades } from '@/lib/colorUtils';

interface ComparisonBarChartProps {
  title: string;
  icon: string;
  color: string;
  data: {
    comparison: Array<{
      name: string;
      current_count: number;
      prev_count: number;
    }>;
    current_label?: string;
    previous_label?: string;
    current_color?: string;
    previous_color?: string;
  } | Array<{
    name: string;
    current_count: number;
    prev_count: number;
  }>;
}

export function ComparisonBarChart({ title, icon, color, data }: ComparisonBarChartProps) {
  const IconComponent = getIconComponent(icon);
  const shades = getShades(color);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef = useRef<{ destroy: () => void } | null>(null);

  // 데이터 정규화: 배열 또는 객체 형식 모두 지원
  const isNewFormat = data && !Array.isArray(data) && 'comparison' in data;
  
  type ComparisonItem = { name: string; current_count: number; prev_count: number };
  type NewDataFormat = {
    comparison: ComparisonItem[];
    current_label?: string;
    previous_label?: string;
    current_color?: string;
    previous_color?: string;
  };
  
  const comparisonData = isNewFormat ? (data as NewDataFormat).comparison : (data as ComparisonItem[]);
  const currentLabel = isNewFormat ? (data as NewDataFormat).current_label || '현재월' : '현재월';
  const previousLabel = isNewFormat ? (data as NewDataFormat).previous_label || '이전월' : '이전월';
  // 색상은 항상 컴포넌트의 color 팔레트에서 파생 (아이콘과 동일 기준)
  // 백엔드가 내려준 색상 힌트가 있더라도, 사용자가 카드 색을 바꾸면 그 팔레트로 즉시 반영되어야 함
  const currentColor = shades.text500;   // 진한 색 (현재월)
  const previousColor = shades.bar400;   // 연한 색 (이전월)

  useEffect(() => {
    if (!canvasRef.current || !comparisonData || comparisonData.length === 0) return;

    // Chart.js 동적 로드
    const loadChart = async () => {
      const Chart = (await import('chart.js/auto')).default;
      const ChartDataLabels = (await import('chartjs-plugin-datalabels')).default;

      // 기존 차트 제거
      if (chartRef.current) {
        chartRef.current.destroy();
      }

      const ctx = canvasRef.current!.getContext('2d')!;
      
      // 최대값 계산 (여백 추가)
      const maxValue = Math.max(
        ...comparisonData.map(item => Math.max(item.current_count, item.prev_count))
      );
      const chartMax = Math.ceil(maxValue * 1.15); // 15% 여백

      chartRef.current = new Chart(ctx, {
        type: 'bar',
        plugins: [ChartDataLabels],
        data: {
          labels: comparisonData.map(item => item.name),
          datasets: [
            {
              label: previousLabel,
              data: comparisonData.map(item => item.prev_count),
              backgroundColor: previousColor,
              borderRadius: 4,
              datalabels: {
                anchor: 'center' as const,
                align: 'center' as const,
                color: '#ffffff',
                font: { size: 11, weight: 'bold' },
                formatter: (value: number) => value > 0 ? value + '건' : ''
              }
            },
            {
              label: currentLabel,
              data: comparisonData.map(item => item.current_count),
              backgroundColor: currentColor,
              borderRadius: 4,
              datalabels: {
                anchor: 'center' as const,
                align: 'center' as const,
                color: '#ffffff',
                font: { size: 11, weight: 'bold' },
                formatter: (value: number) => value > 0 ? value + '건' : ''
              }
            }
          ]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { 
              position: 'top',
              labels: {
                font: { size: 12, weight: 'bold' },
                padding: 15,
              }
            },
            datalabels: {
              display: true
            },
            tooltip: {
              callbacks: {
                label: (context) => `${context.dataset.label}: ${context.parsed.x}건`
              }
            }
          },
          scales: {
            x: { 
              beginAtZero: true,
              max: chartMax,
              ticks: {
                stepSize: Math.ceil(chartMax / 5),
                font: { size: 11 }
              },
              grid: {
                color: '#e2e8f0'
              }
            },
            y: {
              ticks: {
                font: { size: 12, weight: 'bold' },
                color: '#334155'
              },
              grid: {
                display: false
              }
            }
          }
        }
      });
    };

    loadChart();

    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
      }
    };
  }, [comparisonData, currentLabel, previousLabel, currentColor, previousColor, color]);

  if (!comparisonData || comparisonData.length === 0) {
    return (
      <section className="bg-white rounded-2xl shadow-lg p-6">
        <div className="flex items-center mb-6">
          <div className="p-3 rounded-full" style={{ backgroundColor: shades.bg100 }}>
            <IconComponent className="h-6 w-6" style={{ color: shades.text600 }} />
          </div>
          <h2 className="text-xl font-bold text-slate-800 ml-4">{title}</h2>
        </div>
        <p className="text-slate-500">비교할 데이터가 없습니다.</p>
      </section>
    );
  }

  // 차트 높이 동적 계산 (항목당 60px + 여백)
  const chartHeight = Math.max(300, comparisonData.length * 60 + 80);

  return (
    <section className="bg-white rounded-2xl shadow-lg p-6">
      <div className="flex items-center mb-6">
        <div className="p-3 rounded-full" style={{ backgroundColor: shades.bg100 }}>
          <IconComponent className="h-6 w-6" style={{ color: shades.text600 }} />
        </div>
        <h2 className="text-xl font-bold text-slate-800 ml-4">{title}</h2>
      </div>
      
      <div style={{ height: `${chartHeight}px` }}>
        <canvas ref={canvasRef}></canvas>
      </div>
    </section>
  );
}
