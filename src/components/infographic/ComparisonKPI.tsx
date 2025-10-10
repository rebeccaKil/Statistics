'use client';

import { ArrowRight, ArrowUp, ArrowDown } from 'lucide-react';
import { getIconComponent } from '@/lib/iconUtils';
import { getShades } from '@/lib/colorUtils';

interface ComparisonKPIProps {
  title: string;
  icon: string;
  color: string;
  data: {
    current_value: number;
    previous_value: number;
    unit: string;
    change_text: string;
    change_status: 'increase' | 'decrease' | 'neutral';
    current_label?: string;
    previous_label?: string;
    current_color?: string;
    previous_color?: string;
  };
}

export function ComparisonKPI({ title, icon, color, data }: ComparisonKPIProps) {
  const IconComponent = getIconComponent(icon);
  const shades = getShades(color);

  const getChangeIcon = () => {
    switch (data.change_status) {
      case 'increase':
        return <ArrowUp className="w-5 h-5 mr-1" />;
      case 'decrease':
        return <ArrowDown className="w-5 h-5 mr-1" />;
      default:
        return null;
    }
  };

  const getChangeColor = () => {
    switch (data.change_status) {
      case 'increase':
        return 'text-green-500';
      case 'decrease':
        return 'text-blue-500';
      default:
        return 'text-gray-500';
    }
  };

  // 색상 설정 (data에 지정된 색상 우선, 없으면 기본 색상 사용)
  const colors = {
    icon: shades.text600,
    previous: data.previous_color || '#a78bfa',
    current: data.current_color || shades.text500,
  };

  return (
    <section className="bg-white rounded-2xl shadow-lg p-6 flex flex-col justify-center items-center text-center">
      <h2 className="text-xl font-bold text-slate-800 mb-6 flex items-center">
        <IconComponent className="w-6 h-6 mr-2" style={{ color: colors.icon }} />
        {title}
      </h2>
      
      <div className="flex items-baseline space-x-6 mb-4">
        <div>
          <p className="text-slate-500 font-semibold mb-2">{data.previous_label || '이전월'}</p>
          <p className="text-6xl font-black flex justify-center items-baseline" style={{ color: colors.previous }}>
            <span>{data.previous_value || 0}</span>
            <span className="text-xl font-semibold ml-1">{data.unit}</span>
          </p>
        </div>
        
        <ArrowRight className="w-8 h-8 text-slate-400" />
        
        <div>
          <p className="text-slate-500 font-semibold mb-2">{data.current_label || '현재월'}</p>
          <p className="text-6xl font-black flex justify-center items-baseline" style={{ color: colors.current }}>
            <span>{data.current_value || 0}</span>
            <span className="text-xl font-semibold ml-1">{data.unit}</span>
          </p>
        </div>
      </div>
      
      <p className={`text-lg font-bold ${getChangeColor()} mt-4 flex items-center`}>
        {getChangeIcon()}
        {data.change_text}
      </p>
    </section>
  );
}
