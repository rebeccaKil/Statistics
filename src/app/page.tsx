'use client';

import { useState } from 'react';
import { Header } from '@/components/Header';
import { ControlPanel } from '@/components/ControlPanel';
import { SelectionPanel } from '@/components/SelectionPanel';
import { ResultSection } from '@/components/ResultSection';
import { ExcelData, InfographicComponent } from '@/types';

export default function Home() {
  const [excelData, setExcelData] = useState<ExcelData[] | null>(null);
  const [analyzedComponents, setAnalyzedComponents] = useState<InfographicComponent[]>([]);
  // 선택된 인덱스는 결과 렌더링 전용으로 분리 관리
  const [selectedIndices, setSelectedIndices] = useState<number[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [showSelectionPanel, setShowSelectionPanel] = useState(false);

  const handleDataProcessed = (data: ExcelData[]) => {
    setExcelData(data);
  };


  // Gemini 제거됨

  const handleAnalysisStart = async (year: number, month: number, reportType: string) => {
    if (!excelData) return;

    setIsLoading(true);
    setShowSelectionPanel(false);
    setLoadingMessage('데이터 구조를 분석 중입니다... (1/3)');

    try {
      const isDevelopment = process.env.NODE_ENV === 'development' || 
                           typeof window !== 'undefined' && window.location.hostname === 'localhost';
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 
                    (isDevelopment ? 'http://127.0.0.1:8080' : 'https://statistics-49nt.onrender.com');

      setLoadingMessage('서버에서 통계 데이터를 계산 중입니다...');
      const resp = await fetch(`${apiUrl.replace(/\/$/, '')}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rows: excelData, year, month, reportType })
      });
      if (!resp.ok) {
        const txt = await resp.text();
        throw new Error(`분석 API 오류: ${resp.status} ${txt}`);
      }
      const components = await resp.json();

      setAnalyzedComponents(components);
      // 기본값: 모두 선택
      setSelectedIndices((components as InfographicComponent[]).map((c: InfographicComponent, idx: number) => idx));
      setShowSelectionPanel(true);
    } catch (error) {
      console.error('Analysis error:', error);
      alert(`분석 중 오류가 발생했습니다: ${error instanceof Error ? error.message : '알 수 없는 오류'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRenderComponents = (selectedIndices: number[]) => {
    // 선택 상태만 갱신하고 패널은 유지
    setSelectedIndices(selectedIndices);
  };

  const handleColorChange = (index: number, color: string) => {
    setAnalyzedComponents(prev => prev.map((c, i) => i === index ? { ...c, color } : c));
  };

  const handleMetaChange = (index: number, meta: { title?: string; icon?: string; chart_type?: string }) => {
    setAnalyzedComponents(prev => prev.map((c, i) => {
      if (i === index) {
        if (meta.chart_type && c.component_type === 'cumulative_column' && c.data) {
          // chart_type 변경 시 data 내부에도 반영
          return { ...c, ...meta, data: { ...c.data, chart_type: meta.chart_type as 'bar' | 'line' } } as InfographicComponent;
        }
        return { ...c, ...meta } as InfographicComponent;
      }
      return c;
    }));
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-6xl mx-auto p-4 sm:p-6 md:p-8 space-y-8">
        <Header />
        
        <ControlPanel 
          onDataProcessed={handleDataProcessed}
          onAnalysisStart={handleAnalysisStart}
        />
        
        {showSelectionPanel && (
        <SelectionPanel 
          components={analyzedComponents}
          onRender={handleRenderComponents}
          onColorChange={handleColorChange}
          onMetaChange={handleMetaChange}
        />
        )}

        <ResultSection 
          isLoading={isLoading}
          loadingMessage={loadingMessage}
          components={
            selectedIndices.length > 0
              ? analyzedComponents.filter((_, i) => selectedIndices.includes(i))
              : analyzedComponents
          }
        />
      </div>
    </div>
  );
}