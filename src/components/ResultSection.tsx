'use client';

import { Loader2 } from 'lucide-react';
import { KPICard } from './infographic/KPICard';
import { BarChart } from './infographic/BarChart';
import { ComparisonKPI } from './infographic/ComparisonKPI';
import { ComparisonBarChart } from './infographic/ComparisonBarChart';
import { DailyBreakdown } from './infographic/DailyBreakdown';
import { Summary } from './infographic/Summary';
import { CumulativeChart } from './infographic/CumulativeChart';
import { InfographicComponent } from '@/types';

interface ResultSectionProps {
  isLoading: boolean;
  loadingMessage: string;
  components: InfographicComponent[];
}

export function ResultSection({ isLoading, loadingMessage, components }: ResultSectionProps) {
  if (isLoading) {
    return (
      <div className="min-h-[300px] flex justify-center items-center">
        <div className="flex flex-col items-center text-slate-500">
          <Loader2 className="h-10 w-10 animate-spin text-indigo-600" />
          <p className="mt-4 font-semibold">{loadingMessage}</p>
        </div>
      </div>
    );
  }

  if (components.length === 0) {
    return (
      <div className="min-h-[300px] flex justify-center items-center">
        <p className="text-slate-500">데이터를 가져온 후 리포트를 생성해 주세요.</p>
      </div>
    );
  }

  const gridItems = components.filter(comp => 
    ['kpi', 'comparison_kpi'].includes(comp.component_type)
  );
  const cumulativeColumns = components.filter(comp => 
    comp.component_type === 'cumulative_column'
  );
  const otherItems = components.filter(comp => 
    !['kpi', 'comparison_kpi', 'cumulative_column'].includes(comp.component_type)
  );

  // 누적 컬럼들을 하나의 CumulativeChart로 통합
  const cumulativeChart = cumulativeColumns.length > 0 ? {
    component_type: 'cumulative_chart',
    title: '누적 리포트',
    icon: 'trending-up',
    color: 'indigo',
    source_column: 'cumulative',
    data: {
      labels: (cumulativeColumns[0].data as any)?.labels || [],
      bars: cumulativeColumns
        .filter(c => (c.data as any)?.chart_type === 'bar')
        .map(c => ({
          label: c.title,
          values: (c.data as any)?.values || [],
          color: c.color || 'indigo'
        })),
      lines: cumulativeColumns
        .filter(c => (c.data as any)?.chart_type === 'line')
        .map(c => ({
          label: c.title,
          values: (c.data as any)?.values || [],
          color: c.color || 'indigo'
        })),
      lineCumulative: false
    }
  } as InfographicComponent : null;

  return (
    <div className="space-y-6">
      {/* KPI 카드들을 먼저 표시 */}
      {gridItems.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {gridItems.map((component, index) => (
            <div key={index}>
              {renderComponent(component)}
            </div>
          ))}
        </div>
      )}
      
      {/* 누적 차트 표시 */}
      {cumulativeChart && (
        <div>
          {renderComponent(cumulativeChart)}
        </div>
      )}
      
      {/* 나머지 컴포넌트들 표시 */}
      {otherItems.map((component, index) => (
        <div key={index}>
          {renderComponent(component)}
        </div>
      ))}
    </div>
  );
}

function renderComponent(component: InfographicComponent) {
  switch (component.component_type) {
    case 'kpi':
      return <KPICard {...component} />;
    case 'bar_chart':
      return <BarChart {...component} />;
    case 'comparison_kpi':
      return <ComparisonKPI {...component} />;
    case 'comparison_bar_chart':
      return <ComparisonBarChart {...component} />;
    case 'daily_breakdown':
      return <DailyBreakdown {...component} />;
    case 'summary':
      return <Summary {...component} />;
    case 'cumulative_chart':
      return <CumulativeChart {...component} />;
    case 'cumulative_column':
      // cumulative_column은 ResultSection에서 통합 처리하므로 개별 렌더링 안 함
      return null;
    default:
      return <div>Unknown component type</div>;
  }
}
