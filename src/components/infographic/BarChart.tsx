'use client';

import { getIconComponent } from '@/lib/iconUtils';
import { getShades } from '@/lib/colorUtils';

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
  const IconComponent = getIconComponent(icon);
  const shades = getShades(color);

  if (!data || data.length === 0) {
    return (
      <section className="bg-white rounded-2xl shadow-lg p-6">
        <div className="flex items-center mb-4">
          <div className={`bg-${color}-100 p-3 rounded-full`}>
            <IconComponent className={`text-${color}-600 h-6 w-6`} />
          </div>
          <h2 className="text-xl font-bold text-slate-800 ml-4">{title}</h2>
        </div>
        <p className="text-slate-500">데이터가 없습니다.</p>
      </section>
    );
  }

  const maxVal = Math.max(...data.map(item => item.count), 1);

  return (
    <section className="bg-white rounded-2xl shadow-lg p-6">
      <div className="flex items-center mb-4">
        <div className="p-3 rounded-full" style={{ backgroundColor: shades.bg100 }}>
          <IconComponent className="h-6 w-6" style={{ color: shades.text600 }} />
        </div>
        <h2 className="text-xl font-bold text-slate-800 ml-4">{title}</h2>
      </div>
      
      <div className="space-y-4 mt-6">
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
    </section>
  );
}
