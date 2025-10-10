'use client';

import { useEffect, useState } from 'react';
import { Image as ImageIcon } from 'lucide-react';
import { InfographicComponent } from '@/types';
import { colorOptions } from '@/lib/colorUtils';
import { iconOptions, getIconComponent } from '@/lib/iconUtils';

interface SelectionPanelProps {
  components: InfographicComponent[];
  onRender: (selectedIndices: number[]) => void;
  onColorChange: (index: number, color: string) => void;
  onMetaChange?: (index: number, meta: { title?: string; icon?: string }) => void;
}

export function SelectionPanel({ components, onRender, onColorChange, onMetaChange }: SelectionPanelProps) {
  const [selectedItems, setSelectedItems] = useState<number[]>(
    components.map((_, index) => index)
  );

  // 컴포넌트 목록이 바뀌면 선택 상태를 초기화(모두 선택)
  useEffect(() => {
    setSelectedItems(components.map((_, index) => index));
  }, [components]);

  const handleCheckboxChange = (index: number, checked: boolean) => {
    if (checked) {
      setSelectedItems([...selectedItems, index]);
    } else {
      setSelectedItems(selectedItems.filter(item => item !== index));
    }
  };

  const handleRender = () => {
    onRender(selectedItems);
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
                    defaultValue={(component as { title?: string }).title}
                    onBlur={(e) => onMetaChange(index, { title: e.target.value })}
                    className="flex-1 text-sm font-medium p-1 border rounded bg-white text-slate-700 border-slate-300 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="제목"
                  />
                ) : (
                  <span className="flex-1 text-sm font-medium text-slate-700 truncate">{component.title}</span>
                )}
              </div>

              {/* 아이콘과 색상 선택 - 한 줄로 배치 */}
              <div className="flex items-center space-x-2">
                {/* 아이콘 선택 */}
                {onMetaChange && (
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

                {/* 색상 선택 */}
                <div className="flex items-center space-x-1">
                  <div 
                    className="w-3 h-3 rounded" 
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
