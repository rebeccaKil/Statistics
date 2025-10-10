'use client';

import { useState, useRef } from 'react';
import { Upload, FileCheck } from 'lucide-react';
import Papa from 'papaparse';
import { ExcelData } from '@/types';

interface FileUploaderProps {
  onDataLoaded: (data: ExcelData[]) => void;
}

export function FileUploader({ onDataLoaded }: FileUploaderProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [fileName, setFileName] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = (file: File) => {
    if (!file) return;
    
    // CSV 파일만 허용
    if (!file.name.toLowerCase().endsWith('.csv')) {
      alert('CSV 파일만 업로드 가능합니다.');
      return;
    }
    
    Papa.parse(file, {
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
          
          setFileName(file.name);
          onDataLoaded(jsonData);
        } catch (error) {
          console.error('CSV 처리 오류:', error);
          alert('CSV 파일을 처리하는 중 오류가 발생했습니다.');
        }
      },
      error: (error) => {
        console.error('CSV 파싱 오류:', error);
        alert('CSV 파일을 읽는 중 오류가 발생했습니다.');
      }
    });
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files.length) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length) {
      handleFile(e.target.files[0]);
    }
  };

  return (
    <div
      className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
        isDragOver
          ? 'border-indigo-500 bg-indigo-50'
          : 'border-slate-300 hover:border-slate-400'
      }`}
      onClick={() => fileInputRef.current?.click()}
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragOver(true);
      }}
      onDragLeave={() => setIsDragOver(false)}
      onDrop={handleDrop}
    >
      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        accept=".csv"
        onChange={handleFileInput}
      />
      
      {fileName ? (
        <div className="text-green-600">
          <FileCheck className="mx-auto h-12 w-12 text-green-500" />
          <p className="mt-2 font-semibold text-slate-700">데이터 로드 완료</p>
          <p className="text-sm text-slate-500">({fileName})</p>
        </div>
      ) : (
        <div className="text-slate-500">
          <Upload className="mx-auto h-12 w-12 text-slate-400" />
          <p className="mt-2">여기에 CSV 파일을 드래그하거나 클릭하여 업로드하세요.</p>
          <p className="text-sm">(날짜, 카테고리, 채널, 지역, 문의내용 등)</p>
        </div>
      )}
    </div>
  );
}
