"""
AI Excel Analyzer API - FastAPI 백엔드

이 API는 CSV/Google Sheets 데이터를 분석하여 인포그래픽 컴포넌트를 생성합니다.

주요 기능:
- 컬럼 자동 감지 (날짜/텍스트/카테고리)
- 통계 계산 (총 개수, 피크 일자, 분포 등)
- 키워드 추출 (한글 형태소 분석)
- 3가지 리포트 타입 (단일/비교/누적)
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np

from .models import AnalyzeRequest, Component
from .utils.number_utils import to_number
from .analyzers import detect_columns, extract_keywords, calc_stats
from .analyzers.stats_calculator import month_filter
from .builders import build_components_single, build_components_comparison
from .builders.component_builder import build_monthly_distribution

# FastAPI 애플리케이션 초기화
app = FastAPI(
    title="AI Excel Analyzer API",
    description="CSV/Google Sheets 데이터 분석 및 인포그래픽 생성 API",
    version="2.0.0"
)

# CORS 미들웨어 설정
# 이유: 프론트엔드(Vercel/Render)에서 API 호출 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용 (프로덕션에서는 특정 도메인만 허용 권장)
    allow_credentials=True,
    allow_methods=["*"],   # 모든 HTTP 메서드 허용
    allow_headers=["*"],   # 모든 헤더 허용
)


@app.get("/")
def root():
    """
    루트 엔드포인트 - API 정보 반환
    
    Returns:
        API 정보 딕셔너리
    """
    return {
        "message": "AI Excel Analyzer API",
        "status": "running",
        "version": "2.0.0",
        "features": [
            "cumulative_chart",      # 누적 차트 리포트
            "text_normalization",    # 텍스트 정규화
            "modular_architecture"   # 모듈화 아키텍처
        ]
    }


@app.get("/health")
def health():
    """
    헬스체크 엔드포인트 - 서비스 상태 확인
    
    Returns:
        서비스 상태
    """
    return {"status": "healthy"}


@app.post("/analyze", response_model=list[Component])
def analyze(req: AnalyzeRequest):
    """
    데이터 분석 메인 엔드포인트
    
    처리 흐름:
    1. DataFrame 생성 및 전처리
    2. 컬럼 자동 감지 (날짜/텍스트/카테고리)
    3. 요청된 연월의 데이터 필터링
    4. 통계 계산
    5. 리포트 타입에 따라 컴포넌트 생성
       - single: 단일 월 통계
       - comparison: 전월 비교
       - cumulative: 누적 차트
    
    Args:
        req: AnalyzeRequest (rows, year, month, reportType)
    
    Returns:
        Component 리스트 (인포그래픽 컴포넌트)
    
    Raises:
        400 Error: 데이터 처리 중 오류 발생 시
    
    Notes:
        - 빈 데이터는 빈 리스트 반환
        - 요청한 연월에 데이터 없으면 최신 월로 fallback
        - 날짜 컬럼 없으면 전체 데이터로 분석
    """
    try:
        # ========================================
        # 1. DataFrame 생성 및 전처리
        # ========================================
        # rows가 None이면 빈 리스트 사용
        df = pd.DataFrame(req.rows or [])
        
        # 컬럼 이름 정리 (공백 제거)
        # 이유: " 날짜 " 같은 컬럼명을 "날짜"로 통일
        df.columns = df.columns.map(lambda x: str(x).strip())
        
        # 빈 데이터프레임이면 빈 리스트 반환
        if df.empty:
            return []

        # ========================================
        # 2. 컬럼 자동 감지
        # ========================================
        schema = detect_columns(df)
        date_col = schema.get("dateColumn")       # 날짜 컬럼
        text_col = schema.get("textualColumn")    # 텍스트 컬럼
        cat_cols = schema.get("categoricalColumns", [])  # 카테고리 컬럼들

        # ========================================
        # 3. 대상 연월 설정
        # ========================================
        target_year = req.year
        target_month = req.month

        # ========================================
        # 4. 요청된 연월의 데이터 필터링 및 통계 계산
        # ========================================
        current_df = month_filter(df, date_col, target_year, target_month)
        current_stats = calc_stats(current_df, date_col, cat_cols, text_col)

        # ========================================
        # 5. Fallback: 요청한 연월에 데이터 없을 때
        # ========================================
        if not current_stats:
            # 5-1. 날짜 컬럼이 있으면 최신 월로 fallback
            if date_col and date_col in df.columns:
                from .utils.date_utils import try_parse_date
                
                # 유효한 날짜 파싱
                parsed = df[date_col].apply(try_parse_date)
                valid = parsed.dropna()
                
                if not valid.empty:
                    # 가장 최근 날짜 찾기
                    latest = valid.max()
                    fallback_year, fallback_month = latest.year, latest.month
                    
                    # 최신 월 데이터로 재시도
                    current_df = month_filter(df, date_col, fallback_year, fallback_month)
                    current_stats = calc_stats(current_df, date_col, cat_cols, text_col)

            # 5-2. 여전히 없으면 전체 데이터로 분석 (날짜 필터링 없이)
            if not current_stats:
                current_stats = calc_stats(df, None, cat_cols, text_col)

        # ========================================
        # 6. 리포트 타입별 컴포넌트 생성
        # ========================================
        
        # 6-1. 누적 차트 리포트
        if req.reportType == 'cumulative':
            return _build_cumulative_report(df, date_col, target_year, target_month)

        # 6-2. 단일 월 리포트 (날짜 컬럼 없으면 자동으로 이 타입)
        if req.reportType == 'single' or not date_col:
            comps = _build_single_report(current_stats, cat_cols, current_df, text_col, target_month)
            # 여행일/여행일자 컬럼이 있는 경우 월별 분포 추가
            for travel_col_candidate in ['여행일', '여행일자']:
                if travel_col_candidate in df.columns:
                    monthly = build_monthly_distribution(df, travel_col_candidate)
                    if monthly is not None:
                        comps.append(monthly.dict())
                        break
            return comps

        # 6-3. 전월 비교 리포트
        comps = _build_comparison_report(
            df, date_col, cat_cols, text_col,
            current_stats, current_df,
            target_year, target_month
        )
        # 여행일/여행일자 월별 분포 추가 (비교 리포트에도 함께 노출)
        for travel_col_candidate in ['여행일', '여행일자']:
            if travel_col_candidate in df.columns:
                monthly = build_monthly_distribution(df, travel_col_candidate)
                if monthly is not None:
                    comps.append(monthly.dict())
                    break
        return comps

    except Exception as e:
        # 오류 발생 시 400 응답
        return JSONResponse(status_code=400, content={"error": str(e)})


def _build_cumulative_report(df, date_col, target_year, target_month):
    """
    누적 차트 리포트 생성 (월별 누적 데이터)
    
    처리 과정:
    1. 날짜 컬럼 재확인 (컬럼 감지가 실패했을 경우 대비)
    2. 대상 월까지의 데이터만 필터링
    3. 월별로 그룹화하여 숫자 컬럼 집계
    4. 각 숫자 컬럼별로 누적 차트 컴포넌트 생성
    
    Args:
        df: 전체 데이터프레임
        date_col: 날짜 컬럼 이름 (None일 수 있음)
        target_year: 대상 연도
        target_month: 대상 월 (이 월까지의 누적 데이터)
    
    Returns:
        Component 리스트 또는 JSONResponse (오류 시)
    
    Notes:
        - 날짜 컬럼 없으면 400 오류 반환
        - 숫자 컬럼만 차트로 생성
        - 각 컬럼마다 다른 색상 지정
    """
    from .utils.date_utils import try_parse_date
    
    # ========================================
    # 1. 날짜 컬럼 재확인 (fallback 로직)
    # ========================================
    # 이유: detect_columns에서 날짜 컬럼을 못 찾았을 수 있음
    inferred_date_col = None
    best_ratio = -1.0
    
    for col in df.columns:
        # 각 컬럼을 날짜로 파싱 시도
        parsed_try = df[col].apply(try_parse_date)
        ratio = parsed_try.notnull().mean()
        
        # 가장 성공률이 높은 컬럼 선택
        if ratio > best_ratio:
            best_ratio = ratio
            inferred_date_col = col
            parsed_dates = parsed_try
    
    if inferred_date_col is None or best_ratio <= 0:
        return JSONResponse(status_code=400, content={"error": "누적 리포트: 날짜 컬럼을 찾을 수 없습니다."})

    periods = pd.to_datetime(parsed_dates, errors='coerce').dt.to_period('M')
    target_period = pd.Period(f"{target_year}-{target_month:02d}", freq='M')
    mask = periods <= target_period
    df_cum = df.loc[mask].copy()
    df_cum['_ym'] = periods[mask].dt.strftime('%Y-%m')
    
    for c in df_cum.columns:
        if c == '_ym':
            continue
        if not pd.api.types.is_numeric_dtype(df_cum[c]):
            try:
                converted = df_cum[c].map(to_number)
                if converted.notnull().any():
                    df_cum[c] = converted
            except Exception:
                pass
    
    all_periods = periods.dropna()
    if not all_periods.empty:
        min_period = all_periods.min()
        max_period = min(target_period, all_periods.max())
        all_months = pd.period_range(start=min_period, end=max_period, freq='M')
        all_labels = [p.strftime('%Y-%m') for p in all_months]
    else:
        all_labels = []

    numeric_cols = [c for c in df_cum.columns if c != '_ym' and pd.api.types.is_numeric_dtype(df_cum[c])]
    color_palette = ['indigo', 'blue', 'green', 'yellow', 'orange', 'red', 'pink', 'purple', 'cyan', 'teal']
    
    components = []
    for idx, col in enumerate(numeric_cols):
        monthly_values = df_cum.groupby('_ym')[col].sum().reindex(all_labels, fill_value=0)
        values_list = [int(float(v)) for v in monthly_values.tolist()]
        assigned_color = color_palette[idx % len(color_palette)]
        
        components.append(Component(
            component_type='cumulative_column',
            title=col,
            source_column=col,
            icon='bar-chart',
            color=assigned_color,
            data={
                'column_name': col,
                'labels': all_labels,
                'values': values_list,
                'chart_type': 'bar'
            }
        ))
    
    if not components:
        return JSONResponse(status_code=400, content={"error": "숫자형 컬럼을 찾을 수 없습니다."})
        
    return [c.dict() for c in components]


def _build_single_report(current_stats, cat_cols, current_df, text_col, target_month):
    """
    단일 월 리포트 생성
    
    생성 컴포넌트:
    1. 기본 컴포넌트 (KPI, 막대 차트)
    2. 일자별 분석 (있는 경우)
    3. 주요 오류 요약 (있는 경우)
    4. 키워드 차트 (텍스트 컬럼 있는 경우)
    
    Args:
        current_stats: calc_stats 결과
        cat_cols: 카테고리 컬럼 리스트
        current_df: 현재 월 데이터프레임
        text_col: 텍스트 컬럼 이름
        target_month: 대상 월
    
    Returns:
        Component 딕셔너리 리스트
    """
    # 기본 컴포넌트 생성
    components = build_components_single(current_stats, cat_cols)
    
    if current_stats.get("daily_list"):
        components.append(Component(
            component_type='daily_breakdown',
            title=f'{target_month}월 일자별 오류 현황',
            source_column='daily_breakdown',
            icon='calendar',
            color='cyan',
            data=current_stats["daily_list"]
        ))
    
    if current_stats.get("summary_items"):
        components.append(Component(
            component_type='summary',
            title=f'{target_month}월 주요 오류 내용 요약',
            source_column='summary',
            icon='alert-triangle',
            color='rose',
            data={"items": current_stats["summary_items"]}
        ))
    
    try:
        if text_col and text_col in current_df.columns:
            curr_texts = current_df[text_col].astype(str).tolist()
            keywords = extract_keywords(curr_texts, top_n=5)
            if keywords:
                components.append(Component(
                    component_type='bar_chart',
                    title='주요 문의 키워드',
                    source_column='keywords_top',
                    icon='pie-chart',
                    color='rose',
                    data=keywords
                ))
    except Exception:
        pass
    
    return [c.dict() for c in components]


def _build_comparison_report(df, date_col, cat_cols, text_col, current_stats, current_df, target_year, target_month):
    """
    전월 비교 리포트 생성
    
    생성 컴포넌트:
    1. 비교 컴포넌트 (비교 KPI, 비교 막대 차트)
    2. 일자별 분석 (있는 경우)
    3. 주요 오류 요약 (있는 경우)
    4. 키워드 차트 (텍스트 컬럼 있는 경우)
    
    Args:
        df: 전체 데이터프레임
        date_col: 날짜 컬럼 이름
        cat_cols: 카테고리 컬럼 리스트
        text_col: 텍스트 컬럼 이름
        current_stats: 현재 월 통계
        current_df: 현재 월 데이터프레임
        target_year: 대상 연도
        target_month: 대상 월
    
    Returns:
        Component 딕셔너리 리스트
    """
    # 이전 월 계산
    # 예: 1월이면 전년도 12월, 2월이면 1월
    prev_month = 12 if target_month == 1 else target_month - 1
    prev_year = target_year - 1 if target_month == 1 else target_year
    
    # 이전 월 데이터 필터링 및 통계 계산
    previous_df = month_filter(df, date_col, prev_year, prev_month)
    previous_stats = calc_stats(previous_df, date_col, cat_cols, text_col) if date_col else None
    
    # 비교 컴포넌트 생성
    components = build_components_comparison(current_stats, previous_stats, cat_cols, target_month, prev_month)
    
    if current_stats.get("daily_list"):
        components.append(Component(
            component_type='daily_breakdown',
            title=f'{target_month}월 일자별 오류 현황',
            source_column='daily_breakdown',
            icon='calendar',
            color='cyan',
            data=current_stats["daily_list"]
        ))
    
    if current_stats.get("summary_items"):
        components.append(Component(
            component_type='summary',
            title=f'{target_month}월 주요 오류 내용 요약',
            source_column='summary',
            icon='alert-triangle',
            color='rose',
            data={"items": current_stats["summary_items"]}
        ))
    
    try:
        if text_col and text_col in current_df.columns:
            curr_texts = current_df[text_col].astype(str).tolist()
            keywords = extract_keywords(curr_texts, top_n=5)
            if keywords:
                components.append(Component(
                    component_type='bar_chart',
                    title=f'주요 문의 키워드({target_month}월)',
                    source_column='keywords_top',
                    icon='pie-chart',
                    color='rose',
                    data=keywords
                ))
    except Exception:
        pass
    
    return [c.dict() for c in components]
