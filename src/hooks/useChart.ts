import { useEffect, useRef } from 'react';
import type { Chart as ChartType, ChartConfiguration } from 'chart.js';

export function useChart<T = unknown>(
  config: ChartConfiguration,
  dependencies: T[] = []
) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef = useRef<ChartType | null>(null);

  useEffect(() => {
    if (!canvasRef.current) return;

    const loadChart = async () => {
      const { Chart } = await import('chart.js/auto');
      const ChartDataLabels = (await import('chartjs-plugin-datalabels')).default;

      if (chartRef.current) {
        chartRef.current.destroy();
      }

      const ctx = canvasRef.current!.getContext('2d')!;
      chartRef.current = new Chart(ctx, {
        ...config,
        plugins: [...(config.plugins || []), ChartDataLabels]
      });
    };

    loadChart();

    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
      }
    };
  }, dependencies);

  return canvasRef;
}

