'use client';

import { getIconComponent } from '@/lib/iconUtils';
import { getShades } from '@/lib/colorUtils';

interface DailyBreakdownProps {
  title: string;
  icon: string;
  color: string;
  data: Array<{
    date: string;
    count: number;
  }>;
}

export function DailyBreakdown({ title, icon, color, data }: DailyBreakdownProps) {
  const IconComponent = getIconComponent(icon);
  const shades = getShades(color);

  if (!data || data.length === 0) {
    return (
      <section className="bg-white rounded-2xl shadow-lg p-6">
        <div className="flex items-center mb-6">
          <div className="p-3 rounded-full" style={{ backgroundColor: shades.bg100 }}>
            <IconComponent className="h-6 w-6" style={{ color: shades.text600 }} />
          </div>
          <h2 className="text-xl font-bold text-slate-800 ml-4">{title}</h2>
        </div>
        <p className="text-slate-500">데이터가 없습니다.</p>
      </section>
    );
  }

  const maxCount = Math.max(...data.map(item => item.count));

  return (
    <section className="bg-white rounded-2xl shadow-lg p-6">
      <div className="flex items-center mb-6">
        <div className="p-3 rounded-full" style={{ backgroundColor: shades.bg100 }}>
          <IconComponent className="h-6 w-6" style={{ color: shades.text600 }} />
        </div>
        <h2 className="text-xl font-bold text-slate-800 ml-4">{title}</h2>
      </div>
      
      <div className="space-y-3">
        {data.map((item, index) => (
          <div key={index} className="flex items-center">
            <p className="w-32 text-slate-700 font-semibold">{item.date}</p>
            <div className="flex-1 bg-slate-200 rounded-full h-6 overflow-hidden">
              <div
                className="h-6 rounded-full flex items-center justify-end px-3 transition-all duration-500"
                style={{
                  width: `${(item.count / maxCount) * 100}%`,
                  minWidth: item.count > 0 ? '3rem' : '0',
                  background: `linear-gradient(to right, ${shades.bar400}, ${shades.text500})`,
                }}
              >
                <span className="text-white font-bold text-sm">{item.count}건</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

