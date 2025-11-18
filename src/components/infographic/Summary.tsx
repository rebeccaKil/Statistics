'use client';

import { getIconComponent } from '@/lib/iconUtils';
import { getShades } from '@/lib/colorUtils';

interface SummaryProps {
  title: string;
  icon: string;
  color: string;
  data: {
    items: string[];
  };
}

export function Summary({ title, icon, color, data }: SummaryProps) {
  const IconComponent = getIconComponent(icon);
  const shades = getShades(color);

  // 데이터 유효성 검사 강화
  const items = data?.items || [];
  const hasValidData = Array.isArray(items) && items.length > 0;

  if (!hasValidData) {
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

  return (
    <section className="bg-white rounded-2xl shadow-lg p-6">
      <div className="flex items-center mb-6">
        <div className="p-3 rounded-full" style={{ backgroundColor: shades.bg100 }}>
          <IconComponent className="h-6 w-6" style={{ color: shades.text600 }} />
        </div>
        <h2 className="text-xl font-bold text-slate-800 ml-4">{title}</h2>
      </div>
      
      <ul className="space-y-3">
        {items.map((item, index) => {
          // item이 문자열인지 확인
          const itemText = typeof item === 'string' ? item : String(item || '');
          return (
            <li key={index} className="flex items-start">
              <span 
                className="inline-flex items-center justify-center w-6 h-6 rounded-full font-bold text-sm mr-3 flex-shrink-0 mt-0.5 text-white"
                style={{ backgroundColor: shades.text500 }}
              >
                •
              </span>
              <span className="text-slate-700 text-base">{itemText}</span>
            </li>
          );
        })}
      </ul>
    </section>
  );
}

