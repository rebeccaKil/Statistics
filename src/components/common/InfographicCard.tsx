import { ReactNode } from 'react';
import { getIconComponent } from '@/lib/iconUtils';
import { getShades } from '@/lib/colorUtils';

interface InfographicCardProps {
  title: string;
  icon: string;
  color: string;
  children?: ReactNode;
  isEmpty?: boolean;
  emptyMessage?: string;
}

export function InfographicCard({ 
  title, 
  icon, 
  color, 
  children, 
  isEmpty = false,
  emptyMessage = '데이터가 없습니다.'
}: InfographicCardProps) {
  const IconComponent = getIconComponent(icon);
  const shades = getShades(color);

  return (
    <section className="bg-white rounded-2xl shadow-lg p-6">
      <div className="flex items-center mb-6">
        <div className="p-3 rounded-full" style={{ backgroundColor: shades.bg100 }}>
          <IconComponent className="h-6 w-6" style={{ color: shades.text600 }} />
        </div>
        <h2 className="text-xl font-bold text-slate-800 ml-4">{title}</h2>
      </div>
      
      {isEmpty ? (
        <p className="text-slate-500">{emptyMessage}</p>
      ) : (
        children
      )}
    </section>
  );
}

