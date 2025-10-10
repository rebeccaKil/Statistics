import { ExcelData, InfographicComponent, ColumnSchema, MonthStats } from '@/types';

export class DataProcessor {
  generateComponents(
    schema: ColumnSchema, 
    fullData: ExcelData[], 
    year: number, 
    month: number, 
    reportType: string
  ): InfographicComponent[] {
    const getMonthData = (data: ExcelData[], y: number, m: number, dateCol: string) => 
      data.filter(row => {
        if (!row[dateCol]) return false;
        try {
          const d = new Date(row[dateCol]);
          return d.getFullYear() === y && d.getMonth() + 1 === m;
        } catch {
          return false;
        }
      });

    const calculateStatsForMonth = (
      monthData: ExcelData[], 
      dateCol: string, 
      catCols: string[]
    ): MonthStats | null => {
      if (!monthData || monthData.length === 0) return null;
      
      const total_count = monthData.length;
      const dailyCounts = monthData.reduce((acc, row) => {
        try {
          const dateValue = row[dateCol];
          if (dateValue) {
            const dateKey = new Date(dateValue).toISOString().split('T')[0];
            acc[dateKey] = (acc[dateKey] as number || 0) + 1;
          }
        } catch {
          // Ignore invalid dates
        }
        return acc;
      }, {} as Record<string, number>);

      let peak_day_date_iso: string | null = null;
      let peak_day_count = 0;
      if (Object.keys(dailyCounts).length > 0) {
        peak_day_date_iso = Object.keys(dailyCounts).reduce((a, b) => 
          (dailyCounts[a] as number) > (dailyCounts[b] as number) ? a : b
        );
        peak_day_count = dailyCounts[peak_day_date_iso] as number;
      }

      const d = peak_day_date_iso ? new Date(peak_day_date_iso) : null;
      const peak_day = {
        date: d ? `${d.getUTCMonth() + 1}월 ${d.getUTCDate()}일` : 'N/A',
        count: peak_day_count
      };

      const distributions: Record<string, Array<{ name: string; count: number }>> = {};
      catCols.forEach(key => {
        if (!monthData[0] || !monthData[0].hasOwnProperty(key)) {
          distributions[key] = [];
          return;
        }
        const counts = monthData.reduce((acc, row) => {
          if (row[key]) {
            const val = String(row[key]).trim();
            acc[val] = (acc[val] as number || 0) + 1;
          }
          return acc;
        }, {} as Record<string, number>);
        distributions[key] = Object.entries(counts)
          .sort(([, a], [, b]) => (b as number) - (a as number))
          .slice(0, 5)
          .map(([name, count]) => ({ name, count: count as number }));
      });

      return { total_count, peak_day, distributions };
    };

    const currentData = getMonthData(fullData, year, month, schema.dateColumn);
    const currentStats = calculateStatsForMonth(currentData, schema.dateColumn, schema.categoricalColumns);
    
    const components: InfographicComponent[] = [];
    if (!currentStats) return [];

    if (reportType === 'single') {
      components.push({
        component_type: 'kpi',
        title: '총 문의 수',
        source_column: 'total_count',
        icon: 'hash',
        color: 'indigo',
        data: {
          value: currentStats.total_count,
          unit: '건',
          subtitle: `${month}월`
        }
      });

      if (schema.dateColumn) {
        components.push({
          component_type: 'kpi',
          title: '피크 일자',
          source_column: 'peak_day',
          icon: 'trending-up',
          color: 'orange',
          data: {
            value: currentStats.peak_day.count,
            unit: '건',
            subtitle: currentStats.peak_day.date
          }
        });
      }

      schema.categoricalColumns.forEach((col) => {
        const title = col === 'ai_category' ? 'AI-분석 문의 유형' : `${col}별 분포`;
        components.push({
          component_type: 'bar_chart',
          title: title,
          source_column: col,
          icon: 'pie-chart',
          color: 'sky',
          data: currentStats.distributions[col]
        });
      });
    } else { // Comparison
      const prevMonth = month === 1 ? 12 : month - 1;
      const prevYear = month === 1 ? year - 1 : year;
      const previousData = getMonthData(fullData, prevYear, prevMonth, schema.dateColumn);
      const previousStats = calculateStatsForMonth(previousData, schema.dateColumn, schema.categoricalColumns);

      if (previousStats) {
        const currentTotal = currentStats.total_count;
        const previousTotal = previousStats.total_count;
        let change_text = "변동 없음";
        let change_status: 'increase' | 'decrease' | 'neutral' = "neutral";
        
        if (previousTotal > 0) {
          const change = ((currentTotal - previousTotal) / previousTotal) * 100;
          if (change > 0.1) {
            change_text = `${Math.round(change)}% 증가`;
            change_status = "increase";
          } else if (change < -0.1) {
            change_text = `${Math.round(Math.abs(change))}% 감소`;
            change_status = "decrease";
          }
        } else if (currentTotal > 0) {
          change_text = "신규 발생";
          change_status = "increase";
        }

        components.push({
          component_type: 'comparison_kpi',
          title: '총 문의 수 비교',
          source_column: 'total_count',
          icon: 'hash',
          color: 'indigo',
          data: {
            current_value: currentTotal,
            previous_value: previousTotal,
            unit: '건',
            change_text,
            change_status
          }
        });

        schema.categoricalColumns.forEach((col) => {
          const title = col === 'ai_category' ? 'AI-분석 문의 유형 비교' : `${col}별 비교`;
          const currentList = currentStats.distributions[col] || [];
          const prevList = previousStats.distributions[col] || [];
          const allNames = new Set([...currentList.map((i) => i.name), ...prevList.map((i) => i.name)]);
          const currentMap = new Map(currentList.map((i) => [i.name, i.count]));
          const prevMap = new Map(prevList.map((i) => [i.name, i.count]));
          const comparisonData = Array.from(allNames).sort().map(name => ({
            name,
            current_count: currentMap.get(name) || 0,
            prev_count: prevMap.get(name) || 0
          }));
          components.push({
            component_type: 'comparison_bar_chart',
            title: title,
            source_column: col,
            icon: 'pie-chart',
            color: 'sky',
            data: comparisonData
          });
        });
      } else { // No previous data, generate single report instead
        return this.generateComponents(schema, fullData, year, month, 'single');
      }
    }

    return components.filter(c => c.data && (!Array.isArray(c.data) || c.data.length > 0));
  }
}