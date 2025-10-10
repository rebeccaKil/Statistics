# AI 기반 엑셀 데이터 분석 및 인포그래픽 생성기

Python FastAPI 분석 백엔드와 Next.js를 활용하여 CSV/Google 스프레드시트 데이터를 분석하고 시각적인 인포그래픽을 생성하는 웹 애플리케이션입니다.

## 🚀 주요 기능

- **다양한 데이터 소스 지원**: CSV 파일 및 Google 스프레드시트 링크
- **Python 기반 데이터 분석**: pandas/numpy/nltk/konlpy 기반 분석 및 간단 분류
- **인터랙티브 인포그래픽**: KPI, 막대 차트, 비교 분석 등 다양한 시각화
- **반응형 디자인**: 모바일과 데스크톱에서 최적화된 사용자 경험
- **컴포넌트 기반 아키텍처**: 확장 가능한 Next.js 구조

## 🛠️ 기술 스택

- **Frontend**: Next.js 15, React 19, TypeScript
- **UI Framework**: Tailwind CSS
- **Icons**: Lucide React
- **Data Processing**: Papa Parse (CSV)
- **Analysis Backend**: Python FastAPI (pandas, numpy, nltk, konlpy)
- **Deployment**: Vercel

## 📋 사전 요구사항

- Node.js 18.0.0 이상
- Google AI Studio API 키
- Vercel 계정 (배포용)

## 🚀 설치 및 실행

### 1. 저장소 클론
```bash
git clone <repository-url>
cd ai-excel-analyzer
```

### 2. 의존성 설치
```bash
npm install
```

### 3. 환경변수 설정
```bash
# .env.local 파일 생성
echo "GEMINI_API_KEY=your_actual_api_key_here" > .env.local
```

### 4. 로컬 개발 서버 실행
```bash
npm run dev
```

## 🌐 Vercel 배포

### 1. Vercel CLI 설치
```bash
npm install -g vercel
```

### 2. Vercel 로그인
```bash
vercel login
```

### 3. 프로젝트 배포
```bash
vercel
```

### 4. 환경변수 설정
프론트엔드(.env.local) 환경변수:
- `NEXT_PUBLIC_ANALYZE_API_URL` (예: https://your-render-service.onrender.com)

## 📊 사용 방법

1. **데이터 가져오기**
   - CSV 파일을 드래그 앤 드롭하거나 클릭하여 업로드
   - 또는 Google 스프레드시트 링크 입력 (CSV 형식으로 자동 변환)

2. **분석 설정**
   - 기준 연도와 월 선택
   - 리포트 종류 선택 (당월 통계 또는 전월 비교)

3. **AI 분석 실행**
   - "AI 분석 시작하기" 버튼 클릭
   - AI가 데이터 구조를 분석하고 통계 계산

4. **인포그래픽 생성**
   - 원하는 통계 항목 선택
   - "인포그래픽 그리기" 버튼으로 시각화 생성

## 📁 프로젝트 구조

```
ai-excel-analyzer/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── api/               # API 라우트
│   │   ├── globals.css        # 전역 스타일
│   │   ├── layout.tsx         # 루트 레이아웃
│   │   └── page.tsx           # 메인 페이지
│   ├── components/            # React 컴포넌트
│   │   ├── infographic/       # 인포그래픽 컴포넌트
│   │   ├── ControlPanel.tsx   # 제어 패널
│   │   ├── FileUploader.tsx   # 파일 업로더
│   │   ├── Header.tsx         # 헤더
│   │   ├── ResultSection.tsx  # 결과 섹션
│   │   ├── SelectionPanel.tsx # 선택 패널
│   │   └── SheetImporter.tsx  # 스프레드시트 임포터
│   └── lib/                   # 유틸리티 및 서비스
│       ├── dataProcessor.ts   # 데이터 처리 로직
│       ├── geminiService.ts   # Gemini AI 서비스
│       └── iconUtils.ts       # 아이콘 유틸리티
├── public/                    # 정적 파일
├── package.json              # 프로젝트 설정
├── tailwind.config.js        # Tailwind 설정
└── README.md                 # 프로젝트 문서
```

## 🔧 API 키 발급 방법

1. [Google AI Studio](https://aistudio.google.com/app/apikey) 방문
2. Google 계정으로 로그인
3. "Create API Key" 클릭
4. 생성된 API 키를 환경변수에 설정

## 📈 지원하는 데이터 형식

- **CSV 파일**: UTF-8 인코딩의 CSV 파일 (첫 번째 행은 헤더)
- **Google 스프레드시트**: 공개 설정된 스프레드시트 링크 (CSV로 자동 변환)
- **날짜 컬럼**: YYYY-MM-DD 형식의 날짜 데이터
- **카테고리 컬럼**: 그룹화할 수 있는 분류 데이터
- **텍스트 컬럼**: AI가 분석할 수 있는 자유 형식 텍스트

## 🎨 생성되는 인포그래픽 유형

- **KPI 카드**: 총 문의 수, 피크 일자 등 핵심 지표
- **막대 차트**: 카테고리별 분포 및 순위
- **비교 분석**: 전월 대비 증감률 및 변화 추이
- **AI 분석 요약**: 텍스트 데이터 기반 자동 분류 결과

## 🏗️ 아키텍처 특징

- **컴포넌트 기반**: 재사용 가능한 React 컴포넌트
- **타입 안전성**: TypeScript로 타입 안전성 보장
- **서버사이드 렌더링**: Next.js App Router 활용
- **API 라우트**: 서버리스 함수로 환경변수 관리
- **반응형 디자인**: Tailwind CSS로 모바일 최적화

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해 주세요.

---

**Made with ❤️ by TS1042**