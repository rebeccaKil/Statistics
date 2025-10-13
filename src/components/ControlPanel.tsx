'use client';

import { useState } from 'react';
import { BrainCircuit } from 'lucide-react';
import { FileUploader } from './FileUploader';
import { SheetImporter } from './SheetImporter';
import { ExcelData } from '@/types';

interface ControlPanelProps {
  onDataProcessed: (data: ExcelData[]) => void;
  onAnalysisStart: (year: number, month: number, reportType: string) => void;
}

export function ControlPanel({ onDataProcessed, onAnalysisStart }: ControlPanelProps) {
  const [activeTab, setActiveTab] = useState<'file' | 'link'>('file');
  const [year, setYear] = useState(2025);
  const [month, setMonth] = useState(8);
  const [reportType, setReportType] = useState<'single' | 'comparison'>('single');
  const [hasData, setHasData] = useState(false);
  

  const handleDataLoaded = (data: ExcelData[]) => {
    onDataProcessed(data);
    setHasData(true);
  };

  

  const handleAnalysis = () => {
    onAnalysisStart(year, month, reportType);
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 md:p-8 space-y-6">
      {/* Gemini 관련 설정 제거됨 */}

      {/* 데이터 가져오기 섹션 */}
      <div>
        <label className="font-bold text-slate-700 text-lg">1. 데이터 가져오기</label>
        
        {/* 탭 버튼 */}
        <div className="mt-2 border-b border-gray-200">
          <nav className="-mb-px flex space-x-4">
            <button
              onClick={() => setActiveTab('file')}
              className={`whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'file'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
              }`}
            >
              파일 업로드
            </button>
            <button
              onClick={() => setActiveTab('link')}
              className={`whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'link'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
              }`}
            >
              스프레드시트 링크
            </button>
          </nav>
        </div>

        {/* 탭 콘텐츠 */}
        <div className="mt-4">
          {activeTab === 'file' ? (
            <FileUploader onDataLoaded={handleDataLoaded} />
          ) : (
            <SheetImporter onDataLoaded={handleDataLoaded} />
          )}
        </div>
      </div>

      {/* 분석 설정 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div>
          <label className="font-bold text-slate-700 text-lg">2. 기준 연도</label>
          <input
            type="number"
            value={year}
            onChange={(e) => setYear(parseInt(e.target.value))}
            className="mt-2 w-full p-3 border border-slate-300 rounded-md bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="예: 2025"
          />
        </div>
        <div>
          <label className="font-bold text-slate-700 text-lg">3. 기준 월</label>
          <input
            type="number"
            value={month}
            onChange={(e) => setMonth(parseInt(e.target.value))}
            className="mt-2 w-full p-3 border border-slate-300 rounded-md bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="예: 8"
            min="1"
            max="12"
          />
        </div>
        <div>
          <label className="font-bold text-slate-700 text-lg">4. 리포트 종류</label>
          <div className="mt-2 space-y-2">
            <label className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="report-type"
                value="single"
                checked={reportType === 'single'}
                onChange={(e) => setReportType(e.target.value as 'single')}
                className="mr-2 h-4 w-4 text-indigo-600 focus:ring-indigo-500"
              />
              <span className="text-slate-700 font-medium">당월 통계</span>
            </label>
            <label className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="report-type"
                value="comparison"
                checked={reportType === 'comparison'}
                onChange={(e) => setReportType(e.target.value as 'comparison')}
                className="mr-2 h-4 w-4 text-indigo-600 focus:ring-indigo-500"
              />
              <span className="text-slate-700 font-medium">전월 비교</span>
            </label>
          </div>
        </div>
        
      </div>

      {/* 분석 시작 버튼 */}
      <div>
        <button
          onClick={handleAnalysis}
          disabled={!hasData}
          className={`w-full font-bold py-3 px-4 rounded-lg flex items-center justify-center transition-colors ${
            hasData
              ? 'bg-indigo-600 text-white hover:bg-indigo-700'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          <BrainCircuit className="mr-2 h-5 w-5" />
          데이터 분석 시작하기
        </button>
      </div>
    </div>
  );
}
