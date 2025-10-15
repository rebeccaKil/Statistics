'use client';

import { getShades } from '@/lib/colorUtils';
import { InfographicCard } from '../common/InfographicCard';

interface BarChartProps {
  title: string;
  icon: string;
  color: string;
  data: Array<{
    name: string;
    count: number;
  }>;
}

export function BarChart({ title, icon, color, data }: BarChartProps) {
  const shades = getShades(color);
  const isEmpty = !data || data.length === 0;

  if (isEmpty) {
    return <InfographicCard title={title} icon={icon} color={color} isEmpty />;
  }

  const maxVal = Math.max(...data.map(item => item.count), 1);

  return (
    <InfographicCard title={title} icon={icon} color={color}>
      <div className="space-y-4">
        {data.map((item, index) => {
          const percentage = maxVal > 0 ? (item.count / maxVal) * 100 : 0;
          return (
            <div key={index} className="flex items-center">
              <p className="font-bold text-slate-700 w-40">
                {index + 1}. {item.name}
              </p>
              <div className="flex-1 bg-slate-200 rounded-full h-6">
                <div
                  className="h-6 rounded-full animate-grow"
                  style={{
                    backgroundColor: shades.bar400,
                    width: `${percentage}%`,
                    animationDelay: `${index * 0.1}s`,
                    transformOrigin: 'left',
                  }}
                />
              </div>
              <p className="font-bold w-16 text-right" style={{ color: shades.text600 }}>
                {item.count}건
              </p>
            </div>
          );
        })}
      </div>
    </InfographicCard>
  );
}
