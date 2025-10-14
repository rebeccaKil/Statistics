'use client';

import { useState } from 'react';
import { Link as LinkIcon, CheckCircle, Loader2, X } from 'lucide-react';
import Papa from 'papaparse';
import { ExcelData } from '@/types';

interface SheetImporterProps {
  onDataLoaded: (data: ExcelData[]) => void;
}

export function SheetImporter({ onDataLoaded }: SheetImporterProps) {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');

  const importSheet = async () => {
    if (!url.trim()) {
      alert('스프레드시트 URL을 입력해주세요.');
      return;
    }

    const regex = /https:\/\/docs\.google\.com\/spreadsheets\/d\/([a-zA-Z0-9-_]+)/;
    const match = url.match(regex);
    if (!match) {
      alert('유효한 Google 스프레드시트 URL이 아닙니다.');
      return;
    }

    const sheetId = match[1];
    const gid = (new URL(url)).hash.split('=')[1] || '0';
    const csvUrl = `https://docs.google.com/spreadsheets/d/${sheetId}/export?format=csv&gid=${gid}`;

    setIsLoading(true);
    setStatus('loading');

    try {
      const response = await fetch(csvUrl);
      if (!response.ok) {
        throw new Error(`Status: ${response.status}`);
      }
      
      const csvText = await response.text();
      
      // Papa Parse로 CSV 파싱
      Papa.parse(csvText, {
        header: true,
        skipEmptyLines: true,
        complete: (results) => {
          try {
            if (results.errors.length > 0) {
              console.warn('CSV 파싱 경고:', results.errors);
            }
            
            // 데이터 타입 변환 (문자열을 적절한 타입으로)
            const jsonData = results.data.map((row: unknown) => {
              const typedRow = row as Record<string, string>;
              const processedRow: ExcelData = {};
              Object.keys(typedRow).forEach(key => {
                const value = typedRow[key];
                // 날짜 형식 감지 및 변환
                if (typeof value === 'string' && value.match(/^\d{4}-\d{2}-\d{2}/)) {
                  processedRow[key] = new Date(value);
                } else if (typeof value === 'string' && !isNaN(Number(value)) && value.trim() !== '') {
                  // 숫자 문자열을 숫자로 변환
                  processedRow[key] = Number(value);
                } else {
                  processedRow[key] = value;
                }
              });
              return processedRow;
            });
            
            setStatus('success');
            onDataLoaded(jsonData);
          } catch (error) {
            console.error('CSV 처리 오류:', error);
            setStatus('error');
          } finally {
            setIsLoading(false);
          }
        },
        error: (error: Error) => {
          console.error('CSV 파싱 오류:', error);
          setStatus('error');
          setIsLoading(false);
        }
      });
    } catch (error) {
      console.error('Error importing sheet:', error);
      setStatus('error');
      setIsLoading(false);
    }
  };

  const clearUrl = () => {
    setUrl('');
    setStatus('idle');
  };

  return (
    <div className="space-y-3">
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
        <div className="relative flex-1">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="w-full p-3 pr-10 border border-slate-300 rounded-md bg-white text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="Google 스프레드시트 링크를 붙여넣으세요"
          />
          {url && (
            <button
              onClick={clearUrl}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-1 hover:bg-slate-100 rounded-full transition-colors"
              title="링크 삭제"
            >
              <X className="h-5 w-5 text-slate-500 hover:text-slate-700" />
            </button>
          )}
        </div>
        <button
          onClick={importSheet}
          disabled={isLoading}
          className={`font-bold py-3 px-4 rounded-lg flex-shrink-0 flex items-center justify-center transition-colors ${
            isLoading
              ? 'bg-gray-400 text-white cursor-not-allowed'
              : 'bg-indigo-600 text-white hover:bg-indigo-700'
          }`}
        >
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin mr-2" />
          ) : (
            <LinkIcon className="h-4 w-4 mr-2" />
          )}
          불러오기
        </button>
      </div>
      
      <div className="h-6 flex items-center justify-center">
        {status === 'loading' && (
          <div className="flex items-center text-slate-500">
            <Loader2 className="h-4 w-4 animate-spin mr-2" />
            <p>시트 데이터를 불러오는 중...</p>
          </div>
        )}
        {status === 'success' && (
          <div className="flex items-center text-green-600">
            <CheckCircle className="h-4 w-4 mr-2" />
            <p>데이터를 성공적으로 불러왔습니다!</p>
          </div>
        )}
        {status === 'error' && (
          <p className="text-red-500">
            데이터를 불러오는 데 실패했습니다. URL과 시트 공유 설정을 확인해주세요.
          </p>
        )}
      </div>
    </div>
  );
}
