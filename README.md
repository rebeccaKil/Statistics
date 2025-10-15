# 데이터 분석 및 인포그래픽 생성기

Python FastAPI 분석 백엔드와 Next.js를 활용하여 CSV/Google 스프레드시트 데이터를 분석하고 시각적인 인포그래픽을 생성하는 웹 애플리케이션입니다.

## 🚀 주요 기능

- **다양한 데이터 소스 지원**: CSV 파일 및 Google 스프레드시트 링크
- **모듈화된 데이터 분석**: 
  - 컬럼 타입 자동 감지
  - 키워드 추출 (nltk/konlpy)
  - 통계 계산 및 집계
  - 텍스트 정규화
- **다양한 리포트 타입**:
  - 당월 통계 리포트
  - 전월 비교 리포트
  - 누적 차트 리포트
- **인터랙티브 인포그래픽**: KPI, 막대 차트, 비교 분석, 누적 차트 등 다양한 시각화
- **반응형 디자인**: 모바일과 데스크톱에서 최적화된 사용자 경험
- **확장 가능한 아키텍처**: Frontend/Backend 모듈화 구조

## 🛠️ 기술 스택

### Frontend
- **Framework**: Next.js 15, React 19
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **CSV Parsing**: Papa Parse

### Backend
- **Framework**: FastAPI (Python 3.9+)
- **Data Analysis**: pandas, numpy
- **NLP**: nltk, konlpy (한글 형태소 분석)
- **Data Models**: Pydantic
- **Server**: uvicorn

### Deployment
- **Frontend & Backend**: Render

## 📋 사전 요구사항

- Node.js 18.0.0 이상
- Python 3.9 이상 (백엔드용)
- Render 계정 (배포용)

## 🚀 설치 및 실행

### Frontend 설정

#### 1. 저장소 클론
```bash
git clone <repository-url>
cd ai-excel-analyzer
```

#### 2. 의존성 설치
```bash
npm install
```

#### 3. 환경변수 설정
```bash
# .env.local 파일 생성
echo "NEXT_PUBLIC_ANALYZE_API_URL=http://localhost:8000" > .env.local
```

#### 4. 로컬 개발 서버 실행
```bash
npm run dev
```

### Backend 설정

#### 1. Python 가상환경 생성
```bash
cd python-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

#### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

#### 3. 서버 실행
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

백엔드 서버가 http://localhost:8000 에서 실행됩니다.

## 🌐 배포 (Render)

### 1. Backend 배포

#### 1-1. Render 대시보드에서 New Web Service 생성
- Repository 연결
- Name: `ai-excel-analyzer-backend` (또는 원하는 이름)
- Root Directory: `python-backend`
- Environment: `Python 3`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### 1-2. 배포 완료 후 URL 복사
배포된 백엔드 URL을 복사합니다 (예: `https://ai-excel-analyzer-backend.onrender.com`)

### 2. Frontend 배포

#### 2-1. Render 대시보드에서 New Static Site 생성
- Repository 연결
- Name: `ai-excel-analyzer-frontend` (또는 원하는 이름)
- Root Directory: `.` (프로젝트 루트)
- Build Command: `npm install && npm run build`
- Publish Directory: `out`

#### 2-2. 환경변수 설정
Render 대시보드의 Environment 탭에서 환경변수 추가:
- Key: `NEXT_PUBLIC_ANALYZE_API_URL`
- Value: 백엔드 URL (예: `https://ai-excel-analyzer-backend.onrender.com`)

#### 2-3. next.config.ts 설정 확인
프로젝트에 다음 설정이 포함되어 있는지 확인:
```typescript
output: 'export'  // Static export for Render Static Site
```

### 주의사항
- 백엔드를 먼저 배포한 후, 백엔드 URL을 프론트엔드 환경변수에 설정하세요.
- Render의 무료 플랜은 일정 시간 사용하지 않으면 슬립 모드로 전환됩니다.
- 첫 요청 시 약 30초 정도 대기 시간이 발생할 수 있습니다.

## 📊 사용 방법

1. **데이터 가져오기**
   - CSV 파일을 드래그 앤 드롭하거나 클릭하여 업로드
   - 또는 Google 스프레드시트 링크 입력 (CSV 형식으로 자동 변환)

2. **분석 설정**
   - 기준 연도와 월 선택
   - 리포트 종류 선택:
     - **당월 통계**: 선택한 월의 단일 통계 분석
     - **전월 비교**: 전월 대비 증감률 및 변화 추이 분석
     - **누적 차트**: 선택한 월까지의 누적 데이터 시각화

3. **데이터 분석 실행**
   - "AI 분석 시작하기" 버튼 클릭
   - Python 백엔드가 자동으로:
     - 날짜/카테고리/텍스트 컬럼 감지
     - 통계 계산 및 집계
     - 키워드 추출 (한글/영문 지원)
     - 인포그래픽 컴포넌트 생성

4. **인포그래픽 생성**
   - 분석 결과에서 원하는 통계 항목 선택
   - "인포그래픽 그리기" 버튼으로 시각화 생성
   - 생성된 차트와 그래프 확인

## 📁 프로젝트 구조

```
ai-excel-analyzer/
├── src/                        # Frontend (Next.js)
│   ├── app/                    # Next.js App Router
│   │   ├── api/               # API 라우트
│   │   ├── globals.css        # 전역 스타일
│   │   ├── layout.tsx         # 루트 레이아웃
│   │   └── page.tsx           # 메인 페이지
│   ├── components/            # React 컴포넌트
│   │   ├── common/            # 공통 컴포넌트
│   │   │   └── InfographicCard.tsx  # 인포그래픽 카드
│   │   ├── infographic/       # 인포그래픽 컴포넌트
│   │   │   ├── BarChart.tsx           # 막대 차트
│   │   │   ├── ComparisonBarChart.tsx # 비교 막대 차트
│   │   │   ├── ComparisonKPI.tsx      # 비교 KPI
│   │   │   ├── CumulativeChart.tsx    # 누적 차트
│   │   │   ├── DailyBreakdown.tsx     # 일자별 분석
│   │   │   ├── KPICard.tsx            # KPI 카드
│   │   │   └── Summary.tsx            # 요약
│   │   ├── ControlPanel.tsx   # 제어 패널
│   │   ├── FileUploader.tsx   # 파일 업로더
│   │   ├── Header.tsx         # 헤더
│   │   ├── ResultSection.tsx  # 결과 섹션
│   │   ├── SelectionPanel.tsx # 선택 패널
│   │   └── SheetImporter.tsx  # 스프레드시트 임포터
│   ├── hooks/                 # React 커스텀 훅
│   │   └── useChart.ts        # 차트 훅
│   ├── lib/                   # 유틸리티 및 서비스
│   │   ├── colorUtils.ts      # 색상 유틸리티
│   │   ├── dataProcessor.ts   # 데이터 처리 로직
│   │   └── iconUtils.ts       # 아이콘 유틸리티
│   └── types/                 # TypeScript 타입 정의
│       └── index.ts           # 공통 타입
├── python-backend/            # Backend (FastAPI)
│   ├── app/
│   │   ├── analyzers/         # 데이터 분석 모듈
│   │   │   ├── column_detector.py   # 컬럼 타입 감지
│   │   │   ├── keyword_extractor.py # 키워드 추출
│   │   │   └── stats_calculator.py  # 통계 계산
│   │   ├── builders/          # 컴포넌트 빌더
│   │   │   └── component_builder.py # 인포그래픽 컴포넌트 생성
│   │   ├── normalizers/       # 데이터 정규화
│   │   │   └── text_normalizer.py   # 텍스트 정규화
│   │   ├── utils/             # 유틸리티
│   │   │   ├── date_utils.py        # 날짜 처리
│   │   │   └── number_utils.py      # 숫자 처리
│   │   ├── main.py            # FastAPI 메인 애플리케이션
│   │   └── models.py          # Pydantic 데이터 모델
│   ├── Dockerfile             # 백엔드 도커 설정
│   └── requirements.txt       # Python 의존성
├── public/                    # 정적 파일
├── package.json              # 프로젝트 설정
├── tailwind.config.js        # Tailwind 설정
└── README.md                 # 프로젝트 문서
```

## 📈 지원하는 데이터 형식

- **CSV 파일**: UTF-8 인코딩의 CSV 파일 (첫 번째 행은 헤더)
- **Google 스프레드시트**: 공개 설정된 스프레드시트 링크 (CSV로 자동 변환)
- **날짜 컬럼**: YYYY-MM-DD 형식의 날짜 데이터
- **카테고리 컬럼**: 그룹화할 수 있는 분류 데이터
- **텍스트 컬럼**: AI가 분석할 수 있는 자유 형식 텍스트

## 🎨 생성되는 인포그래픽 유형

- **KPI 카드**: 총 문의 수, 피크 일자 등 핵심 지표
- **막대 차트**: 카테고리별 분포 및 순위
- **비교 분석**: 전월 대비 증감률 및 변화 추이 (비교 KPI, 비교 막대 차트)
- **누적 차트**: 월별 누적 데이터 시각화 (숫자 컬럼별 자동 생성)
- **일자별 분석**: 일별 데이터 분포 히트맵
- **키워드 분석**: 텍스트 데이터 기반 주요 키워드 추출 및 시각화
- **AI 분석 요약**: 텍스트 데이터 기반 자동 분류 결과

## 🏗️ 아키텍처 특징

### Frontend
- **컴포넌트 기반**: 재사용 가능한 React 컴포넌트
- **타입 안전성**: TypeScript로 타입 안전성 보장
- **서버사이드 렌더링**: Next.js App Router 활용
- **커스텀 훅**: useChart 등 상태 관리 최적화
- **반응형 디자인**: Tailwind CSS로 모바일 최적화

### Backend
- **모듈화 아키텍처**: 분석/빌더/정규화 모듈 분리
- **단일 책임 원칙**: 각 모듈이 명확한 역할 담당
- **확장성**: 새로운 분석기/빌더 추가 용이
- **타입 검증**: Pydantic 모델로 데이터 검증
- **RESTful API**: FastAPI 기반 고성능 API

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