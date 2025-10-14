export interface ExcelData {
  [key: string]: string | number | Date | null | undefined;
}

export interface ColumnSchema {
  dateColumn: string;
  categoricalColumns: string[];
  textualColumn: string;
}

export interface KPIComponent {
  component_type: 'kpi';
  title: string;
  source_column: string;
  icon: string;
  color: string;
  data: {
    value: number;
    unit: string;
    subtitle: string;
  };
}

export interface BarChartComponent {
  component_type: 'bar_chart';
  title: string;
  source_column: string;
  icon: string;
  color: string;
  data: Array<{
    name: string;
    count: number;
  }>;
}

export interface ComparisonKPIComponent {
  component_type: 'comparison_kpi';
  title: string;
  source_column: string;
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

export interface ComparisonBarChartComponent {
  component_type: 'comparison_bar_chart';
  title: string;
  source_column: string;
  icon: string;
  color: string;
  data: {
    comparison: Array<{
      name: string;
      current_count: number;
      prev_count: number;
    }>;
    current_label?: string;
    previous_label?: string;
    current_color?: string;
    previous_color?: string;
  } | Array<{
    name: string;
    current_count: number;
    prev_count: number;
  }>;
}

export interface DailyBreakdownComponent {
  component_type: 'daily_breakdown';
  title: string;
  source_column: string;
  icon: string;
  color: string;
  data: Array<{
    date: string;
    count: number;
  }>;
}

export interface SummaryComponent {
  component_type: 'summary';
  title: string;
  source_column: string;
  icon: string;
  color: string;
  data: {
    items: string[];
  };
}

export interface CumulativeChartComponent {
  component_type: 'cumulative_chart';
  title: string;
  source_column: string;
  icon: string;
  color: string;
  data:
    | Array<{
        name: string; // YYYY-MM
        count: number; // 월별 값
        cumulative: number; // 누적 합계
      }>
    | {
        labels: string[]; // YYYY-MM
        bars: Array<{ label: string; values: number[]; color?: string }>;
        lines: Array<{ label: string; values: number[]; color?: string }>;
        lineCumulative?: boolean;
      };
}

export interface CumulativeColumnComponent {
  component_type: 'cumulative_column';
  title: string;
  source_column: string;
  icon: string;
  color: string;
  data: {
    column_name: string;
    labels: string[]; // YYYY-MM
    values: number[];
    chart_type: 'bar' | 'line';
  };
}

export type InfographicComponent = 
  | KPIComponent 
  | BarChartComponent 
  | ComparisonKPIComponent 
  | ComparisonBarChartComponent
  | DailyBreakdownComponent
  | SummaryComponent
  | CumulativeChartComponent
  | CumulativeColumnComponent;

export type CumulativeData = 
  | Array<{ name: string; count: number; cumulative: number }>
  | { labels: string[]; bars: Array<{ label: string; values: number[]; color?: string }>; lines: Array<{ label: string; values: number[]; color?: string }>; lineCumulative?: boolean };

export function isCumulativeColumnComponent(component: InfographicComponent): component is CumulativeColumnComponent {
  return component.component_type === 'cumulative_column';
}

export function hasMultipleDatasets(data: CumulativeData): data is { labels: string[]; bars: Array<{ label: string; values: number[]; color?: string }>; lines: Array<{ label: string; values: number[]; color?: string }>; lineCumulative?: boolean } {
  return !Array.isArray(data) && 'labels' in data;
}

export interface MonthStats {
  total_count: number;
  peak_day: {
    date: string;
    count: number;
  };
  distributions: Record<string, Array<{ name: string; count: number }>>;
}

export interface TextCategorizationItem {
  index: number;
  ai_category: string;
}
