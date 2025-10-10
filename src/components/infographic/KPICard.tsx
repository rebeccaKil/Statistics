'use client';

import { getIconComponent } from '@/lib/iconUtils';
import { getShades } from '@/lib/colorUtils';

interface KPICardProps {
  title: string;
  icon: string;
  color: string;
  data: {
    value: number;
    unit: string;
    subtitle: string;
  };
}

export function KPICard({ title, icon, color, data }: KPICardProps) {
  const IconComponent = getIconComponent(icon);
  const shades = getShades(color);

  return (
    <section className="bg-white rounded-2xl shadow-lg p-6 flex flex-col justify-center items-center text-center h-64">
      <div className="flex items-center mb-4">
        <div className="p-3 rounded-full" style={{ backgroundColor: shades.bg100 }}>
          <IconComponent className="h-6 w-6" style={{ color: shades.text600 }} />
        </div>
        <h2 className="text-xl font-bold text-slate-800 ml-4">{title}</h2>
      </div>
      
      <div className="flex flex-col justify-center items-center flex-1">
        {data.subtitle && (
          <p className="text-2xl font-bold text-slate-700 mb-4">{data.subtitle}</p>
        )}
        <p className="text-6xl font-extrabold flex justify-center items-baseline" style={{ color: shades.text500 }}>
          <span>{data.value || 0}</span>
          <span className="text-2xl font-semibold ml-1">{data.unit || ''}</span>
        </p>
      </div>
    </section>
  );
}
