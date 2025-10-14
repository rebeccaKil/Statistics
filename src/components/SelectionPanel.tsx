'use client';

import { useState } from 'react';
import { Image as ImageIcon } from 'lucide-react';
import { InfographicComponent } from '@/types';
import { colorOptions } from '@/lib/colorUtils';
import { iconOptions, getIconComponent } from '@/lib/iconUtils';

interface SelectionPanelProps {
  components: InfographicComponent[];
  onRender: (selectedIndices: number[]) => void;
  onColorChange: (index: number, color: string) => void;
  onMetaChange?: (index: number, meta: { title?: string; icon?: string; chart_type?: string }) => void;
}

export function SelectionPanel({ components, onRender, onColorChange, onMetaChange }: SelectionPanelProps) {
  const [selectedItems, setSelectedItems] = useState<number[]>(
    components.map((_, index) => index)
  );
  const [chartTypes, setChartTypes] = useState<Record<number, string>>({});

  // 선택 상태는 사용자가 변경한 값을 유지하도록 초기화 리셋을 제거합니다.

  const handleCheckboxChange = (index: number, checked: boolean) => {
    const next = checked
      ? [...selectedItems, index]
      : selectedItems.filter(item => item !== index);
    setSelectedItems(next);
    // 선택 변경을 즉시 부모에 반영
    onRender(next);
  };

  const handleRender = () => {
    onRender(selectedItems);
  };

  const handleChartTypeChange = (index: number, type: string) => {
    setChartTypes(prev => ({ ...prev, [index]: type }));
    if (onMetaChange) {
      onMetaChange(index, { chart_type: type });
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg p-4 space-y-4 max-h-96 overflow-y-auto">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-slate-800">5. 인포그래픽 항목 선택</h2>
        <div className="flex items-center space-x-2 text-sm text-slate-600">
          <span>선택됨: {selectedItems.length}/{components.length}</span>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
        {components.map((component, index) => {
          const currentColor = (component as { color?: string }).color || 'indigo';
          const currentIcon = (component as { icon?: string }).icon || 'BarChart3';
          const isCumulativeColumn = component.component_type === 'cumulative_column';
          const currentChartType = chartTypes[index] || ((component.data as any)?.chart_type || 'bar');
          const IconPreview = getIconComponent(currentIcon);
          const colorPreview = colorOptions.find(c => c.value === currentColor)?.preview || '#6366f1';
          
          return (
            <div key={index} className="bg-slate-50 rounded-lg border border-slate-200 p-3 space-y-2">
              {/* 체크박스와 제목 */}
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={selectedItems.includes(index)}
                  onChange={(e) => handleCheckboxChange(index, e.target.checked)}
                  className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
                {onMetaChange ? (
                  <input
                    type="text"
                    value={(component as { title?: string }).title || ''}
                    onChange={(e) => onMetaChange(index, { title: e.target.value })}
                    className="flex-1 text-sm font-medium p-1 border rounded bg-white text-slate-700 border-slate-300 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="제목"
                  />
                ) : (
                  <span className="flex-1 text-sm font-medium text-slate-700 truncate">{component.title}</span>
                )}
              </div>

              {/* 누적 컬럼일 경우 막대/선 선택 추가 */}
              {isCumulativeColumn && (
                <div className="flex items-center space-x-2 text-xs">
                  <span className="text-slate-600 font-medium">차트 타입:</span>
                  <label className="flex items-center cursor-pointer">
                    <input
                      type="radio"
                      name={`chart-type-${index}`}
                      value="bar"
                      checked={currentChartType === 'bar'}
                      onChange={() => handleChartTypeChange(index, 'bar')}
                      className="mr-1 h-3 w-3 text-indigo-600"
                    />
                    <span className="text-slate-700">막대</span>
                  </label>
                  <label className="flex items-center cursor-pointer">
                    <input
                      type="radio"
                      name={`chart-type-${index}`}
                      value="line"
                      checked={currentChartType === 'line'}
                      onChange={() => handleChartTypeChange(index, 'line')}
                      className="mr-1 h-3 w-3 text-indigo-600"
                    />
                    <span className="text-slate-700">선</span>
                  </label>
                </div>
              )}

              {/* 색상 선택 - 누적 컬럼도 색상 선택 가능 */}
              <div className="flex items-center space-x-2">
                {/* 아이콘 선택 - 일반 컴포넌트만 */}
                {onMetaChange && !isCumulativeColumn && (
                  <div className="flex items-center space-x-1">
                    <IconPreview className="w-3 h-3" style={{ color: colorPreview }} />
                    <select
                      value={currentIcon}
                      onChange={(e) => onMetaChange(index, { icon: e.target.value })}
                      className="text-xs p-1 border rounded bg-white text-slate-700 border-slate-300 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      {iconOptions.map((opt) => (
                        <option key={opt.value} value={opt.value}>
                          {opt.label}
                        </option>
                      ))}
                    </select>
                  </div>
                )}

                {/* 색상 선택 - 모든 컴포넌트 */}
                <div className="flex items-center space-x-1">
                  <span className="text-xs text-slate-600">색상:</span>
                  <div 
                    className="w-3 h-3 rounded border border-slate-300" 
                    style={{ backgroundColor: colorPreview }}
                  />
                  <select
                    value={currentColor}
                    onChange={(e) => onColorChange(index, e.target.value)}
                    className="text-xs p-1 border rounded bg-white text-slate-700 border-slate-300 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    {colorOptions.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      <div className="sticky bottom-0 bg-white pt-2 border-t border-slate-200">
        <button
          onClick={handleRender}
          className="w-full bg-indigo-600 text-white font-bold py-2 px-4 rounded-lg flex items-center justify-center hover:bg-indigo-700 transition-colors text-sm"
        >
          <ImageIcon className="mr-2 h-4 w-4" />
          선택한 항목으로 인포그래픽 그리기
        </button>
      </div>
    </div>
  );
}
