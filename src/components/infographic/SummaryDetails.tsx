'use client';

import { getIconComponent } from '@/lib/iconUtils';
import { getShades } from '@/lib/colorUtils';

interface SummaryDetailsProps {
  title: string;
  icon: string;
  color: string;
  data: {
    items: Array<{
      name: string;
      count: number;
      sources: string[];
    }>;
  };
}

export function SummaryDetails({ title, icon, color, data }: SummaryDetailsProps) {
  const IconComponent = getIconComponent(icon);
  const shades = getShades(color);

  const items = data?.items || [];
  const hasValidData = Array.isArray(items) && items.length > 0;

  if (!hasValidData) {
    return null;
  }

  return (
    <section className="bg-white rounded-2xl shadow-lg p-6">
      <div className="flex items-center mb-6">
        <div className="p-3 rounded-full" style={{ backgroundColor: shades.bg100 }}>
          <IconComponent className="h-6 w-6" style={{ color: shades.text600 }} />
        </div>
        <h2 className="text-xl font-bold text-slate-800 ml-4">{title}</h2>
      </div>

      <div className="space-y-6">
        {items.map((item, index) => (
          <div key={index} className="border border-slate-200 rounded-xl p-4">
            <div className="flex justify-between items-center mb-2">
              <span className="text-slate-800 font-semibold">{item.name}</span>
              <span className="text-slate-500 text-sm">{item.count}건</span>
            </div>
            <div className="mt-2">
              <p className="text-xs text-slate-500 mb-2">
                {item.name === '기타' ? '기타 원문' : '병합된 원문'}
              </p>
              <ul className="space-y-1">
                {item.sources.map((source, sourceIndex) => (
                  <li key={sourceIndex} className="text-sm text-slate-600">
                    • {source}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

