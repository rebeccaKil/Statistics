from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import re
import pandas as pd
from ..utils.date_utils import try_parse_date
from ..normalizers.text_normalizer import normalize_value
from .keyword_extractor import extract_keywords


# ============================================================
# 통계 계산 설정 상수 (프로젝트에 맞게 조정 가능)
# ============================================================

# 일자별 분석에서 보여줄 최대 일수
# 이유: 너무 많으면 UI가 복잡해지므로 상위 N일만 표시
MAX_DAILY_BREAKDOWN_DAYS = 10

# 카테고리별 분포에서 보여줄 최대 항목 수
# 이유: 상위 N개만 보여주고 나머지는 "기타"로 처리
MAX_CATEGORY_ITEMS = 5

# 요약에 포함할 키워드 개수
# 이유: 중요한 항목을 더 많이 노출하기 위해 기본값을 늘림
MAX_SUMMARY_KEYWORDS = 6

# 추출할 전체 키워드 개수
# 이유: 상위 10개까지 추출해 다양한 이슈를 포착
MAX_KEYWORDS_TO_EXTRACT = 10


def month_filter(
    df: pd.DataFrame, 
    date_col: Optional[str], 
    year: int, 
    month: int
) -> pd.DataFrame:
    """
    특정 연월의 데이터만 필터링합니다.
    
    Args:
        df: 필터링할 데이터프레임
        date_col: 날짜 컬럼 이름
        year: 연도 (예: 2024)
        month: 월 (1~12)
    
    Returns:
        필터링된 데이터프레임 (조건에 맞는 행만 포함)
        날짜 컬럼이 없거나 파싱 실패 시 빈 데이터프레임 반환
    
    Examples:
        >>> df = pd.DataFrame({"날짜": ["2024-01-01", "2024-02-01"], "값": [1, 2]})
        >>> result = month_filter(df, "날짜", 2024, 1)
        >>> len(result)
        1
    
    Notes:
        - date_col이 None이거나 컬럼이 존재하지 않으면 빈 데이터프레임 반환
        - try_parse_date를 사용하여 다양한 날짜 형식 지원
    """
    # 날짜 컬럼이 없으면 빈 데이터프레임 반환
    if not date_col or date_col not in df.columns:
        return df.iloc[0:0]
    
    # 날짜 컬럼 파싱
    try:
        parsed = df[date_col].apply(try_parse_date)
        # 연도와 월이 일치하는 행만 필터링
        mask = (parsed.dt.year == year) & (parsed.dt.month == month)
        return df[mask]
    except Exception:
        # 파싱 실패 시 빈 데이터프레임 반환
        return df.iloc[0:0]


def calc_stats(
    df: pd.DataFrame, 
    date_col: Optional[str], 
    cat_cols: List[str], 
    text_col: Optional[str] = None,
    max_daily_days: int = MAX_DAILY_BREAKDOWN_DAYS,
    max_category_items: int = MAX_CATEGORY_ITEMS
) -> Optional[Dict[str, Any]]:
    """
    데이터프레임의 통계를 계산합니다.
    
    계산 항목:
    1. total_count: 전체 행 개수
    2. peak_day: 가장 많은 데이터가 발생한 날짜와 개수
    3. daily_list: 일자별 데이터 개수 (상위 N일, 요일 포함)
    4. distributions: 각 카테고리 컬럼별 분포 (상위 N개)
    5. summary_items: 텍스트 키워드 요약
    
    Args:
        df: 분석할 데이터프레임
        date_col: 날짜 컬럼 이름 (None이면 날짜 분석 스킵)
        cat_cols: 카테고리 컬럼 이름 리스트
        text_col: 텍스트 컬럼 이름 (None이면 키워드 분석 스킵)
        max_daily_days: 일자별 분석에 포함할 최대 일수
        max_category_items: 카테고리별 분포에 포함할 최대 항목 수
    
    Returns:
        통계 딕셔너리 또는 None (빈 데이터프레임인 경우)
        {
            "total_count": int,
            "peak_day": {"date": str, "count": int},
            "daily_list": [{"date": str, "count": int}, ...],
            "distributions": {col: [{"name": str, "count": int}, ...], ...},
            "summary_items": [str, ...]
        }
    
    Examples:
        >>> df = pd.DataFrame({
        ...     "날짜": ["2024-01-01", "2024-01-01", "2024-01-02"],
        ...     "카테고리": ["A", "A", "B"]
        ... })
        >>> stats = calc_stats(df, "날짜", ["카테고리"])
        >>> stats["total_count"]
        3
        >>> stats["peak_day"]
        {"date": "1월 1일", "count": 2}
    
    Notes:
        - 빈 데이터프레임이면 None 반환
        - 날짜 컬럼이 없거나 파싱 실패하면 peak_day, daily_list는 기본값
        - 카테고리 값은 normalize_value로 정규화 후 집계
        - 텍스트 키워드는 extract_keywords 사용
    """
    # 빈 데이터프레임 체크
    if df is None or df.empty:
        return None

    # ========================================
    # 1. 기본 통계: 전체 개수
    # ========================================
    total_count = len(df)
    
    # ========================================
    # 2. 날짜 관련 통계: 피크 일자, 일자별 분포
    # ========================================
    peak_day = {"date": "N/A", "count": 0}
    daily_list: List[Dict[str, Any]] = []
    
    if date_col and date_col in df.columns:
        try:
            # 날짜 컬럼 파싱
            parsed = df[date_col].apply(try_parse_date)
            
            # null이 아닌 날짜만 사용
            valid_dates = parsed.dropna()
            
            if len(valid_dates) > 0:
                # YYYY-MM-DD 형식으로 변환
                dates = valid_dates.dt.strftime('%Y-%m-%d')
                
                # 날짜별 개수 집계
                daily_counts = dates.value_counts().to_dict()
                
                if daily_counts:
                    # 가장 많은 날 찾기
                    peak_day_iso = max(daily_counts, key=daily_counts.get)
                    peak_day_count = int(daily_counts[peak_day_iso])
                    
                    # "M월 D일" 형식으로 변환
                    d = datetime.strptime(peak_day_iso, "%Y-%m-%d")
                    peak_day = {
                        "date": f"{d.month}월 {d.day}일", 
                        "count": peak_day_count
                    }
                    
                    # 상위 N일 추출 (많은 순으로 정렬)
                    sorted_daily = sorted(
                        daily_counts.items(), 
                        key=lambda x: x[1], 
                        reverse=True
                    )[:max_daily_days]
                    
                    # 일자별 리스트 생성 (요일 포함)
                    weekday_names = ['월', '화', '수', '목', '금', '토', '일']
                    for date_str, count in sorted_daily:
                        d = datetime.strptime(date_str, "%Y-%m-%d")
                        weekday = weekday_names[d.weekday()]
                        daily_list.append({
                            "date": f"{d.month}월 {d.day}일 ({weekday})",
                            "count": int(count)
                        })
        except Exception as e:
            # 날짜 파싱 실패 시 기본값 유지
            pass

    # ========================================
    # 3. 카테고리별 분포
    # ========================================
    distributions: Dict[str, List[Dict[str, Any]]] = {}
    distributions_others: Dict[str, List[Dict[str, Any]]] = {}
    
    for col in cat_cols:
        # 컬럼이 존재하지 않으면 빈 리스트
        if col not in df.columns:
            distributions[col] = []
            continue
        
        try:
            # 문자열로 변환 및 공백 제거
            original_values = df[col].astype(str).str.strip()
            
            # 값 정규화 (유사한 표현 통합)
            normalized_values = original_values.apply(normalize_value)
            
            # 값별 개수 집계
            vc = normalized_values.value_counts()
            
            # 상위 N개 및 기타 계산
            top = vc.head(max_category_items)
            others = vc.iloc[max_category_items:]
            
            # 리스트 형태로 변환
            distributions[col] = [
                {"name": str(idx), "count": int(cnt)} 
                for idx, cnt in top.items()
            ]
            distributions_others[col] = [
                {"name": str(idx), "count": int(cnt)}
                for idx, cnt in others.items()
            ]
        except Exception:
            # 집계 실패 시 빈 리스트
            distributions[col] = []
    
    # ========================================
    # 4. 텍스트 키워드 요약 (키워드 추출 및 병합 적용)
    # ========================================
    summary_items: List[Dict[str, Any]] = []
    summary_details: List[Dict[str, Any]] = []
    
    if text_col and text_col in df.columns:
        try:
            # 텍스트 컬럼 추출 (원문 그대로)
            # pandas의 fillna로 NaN을 빈 문자열로 변환 후 처리
            texts_series = df[text_col].fillna('').astype(str)
            texts = texts_series.tolist()
            
            # 빈 텍스트 제거 및 공백 정리
            # NaN, None, 빈 문자열, 'nan' 문자열 모두 제거
            valid_texts = []
            for t in texts:
                if t and isinstance(t, str):
                    t_clean = t.strip()
                    if t_clean and t_clean.lower() not in ['nan', 'none', 'null', '']:
                        valid_texts.append(t_clean)
            
            if valid_texts:
                # 전체 텍스트를 한 번에 처리하여 병합 규칙 적용
                # extract_keywords는 병합 규칙을 적용하여 유사한 키워드들을 통합함
                from collections import defaultdict
                from ..normalizers.text_normalizer import normalize_value
                from ..analyzers.keyword_extractor import MERGE_RULES
                
                # 전체 텍스트 리스트를 한 번에 처리 (병합 규칙이 제대로 작동하도록)
                keywords = extract_keywords(valid_texts, top_n=len(valid_texts) * 2)
                
                # 키워드 -> 원문 텍스트 매핑 생성
                # 각 텍스트가 어떤 키워드로 변환되었는지 추적
                keyword_to_texts = defaultdict(list)
                
                # 병합 규칙에 해당하는 키워드 목록 생성 (정규화된 버전)
                merged_keywords = set()
                for rule in MERGE_RULES:
                    merged_keywords.add(normalize_value(rule["target"]))
                
                # 각 텍스트를 개별적으로 키워드로 변환하여 매핑
                # 병합 규칙이 적용되도록 전체 리스트에서 처리
                for text in valid_texts:
                    # 단일 텍스트에 대해 키워드 추출 (병합 규칙 적용)
                    text_keywords = extract_keywords([text], top_n=1)
                    if text_keywords:
                        keyword = text_keywords[0]['name']
                        # 정규화된 키워드로 매핑 (병합된 키워드와 매칭하기 위해)
                        normalized_keyword = normalize_value(keyword)
                        keyword_to_texts[normalized_keyword].append(text)
                    else:
                        # 키워드 추출 실패 시 원문 사용
                        normalized_text = normalize_value(text)
                        keyword_to_texts[normalized_text].append(text)
                
                detail_items: List[Dict[str, Any]] = []
                other_texts = []  # 병합 규칙에 해당하지 않는 텍스트들
                
                for kw in keywords:
                    keyword_name = kw['name']
                    count = kw['count']
                    
                    # 정규화된 키워드로 매핑 찾기
                    normalized_keyword = normalize_value(keyword_name)
                    
                    # 해당 키워드에 매핑된 모든 원문 텍스트 가져오기
                    if normalized_keyword in keyword_to_texts:
                        examples = keyword_to_texts[normalized_keyword]
                        # 중복 제거 (같은 텍스트가 여러 번 나올 수 있음)
                        unique_examples = list(dict.fromkeys(examples))
                        
                        # 병합 규칙에 해당하는지 확인
                        if normalized_keyword in merged_keywords:
                            # 병합 규칙에 해당하는 경우
                            detail_items.append({
                                "name": keyword_name,
                                "count": count,
                                "sources": unique_examples
                            })
                        else:
                            # 병합 규칙에 해당하지 않는 경우 "기타"로 분류
                            other_texts.extend(unique_examples)
                    else:
                        # 매핑에 없으면 키워드만 표시 (병합 규칙에 해당하지 않을 수 있음)
                        if normalized_keyword not in merged_keywords:
                            other_texts.append(keyword_name)
                        else:
                            detail_items.append({
                                "name": keyword_name,
                                "count": count,
                                "sources": [keyword_name]
                            })
                
                # 전체 숫자 검증 및 "기타" 처리
                total_keyword_count = sum(kw['count'] for kw in keywords)
                processed_texts = set()
                for item in detail_items:
                    for source in item.get("sources", []):
                        processed_texts.add(source)
                
                # 처리되지 않은 텍스트들을 "기타"에 추가
                for text in valid_texts:
                    if text not in processed_texts:
                        other_texts.append(text)
                
                # "기타" 항목 추가 (중복 제거)
                if other_texts:
                    unique_others = list(dict.fromkeys(other_texts))
                    detail_items.append({
                        "name": "기타",
                        "count": len(unique_others),
                        "sources": unique_others
                    })

                summary_details = detail_items
                summary_items = [
                    {"name": item["name"], "count": item["count"]}
                    for item in detail_items
                ]
        except Exception as e:
            # 키워드 추출 실패 시 빈 리스트 유지
            # 디버깅을 위해 예외 정보는 로그로 남기지 않음 (프로덕션 환경)
            pass

    # ========================================
    # 5. 결과 반환
    # ========================================
    return {
        "total_count": int(total_count),
        "peak_day": peak_day,
        "distributions": distributions,
        "daily_list": daily_list,
        "summary_items": summary_items,
        "summary_details": summary_details,
        "distributions_others": distributions_others,
    }

