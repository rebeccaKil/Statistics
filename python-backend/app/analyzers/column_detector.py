from typing import Dict, Any, List, Optional
import pandas as pd
from ..utils.date_utils import try_parse_date


# ============================================================
# 컬럼 감지 설정 (프로젝트에 맞게 조정 가능)
# ============================================================

# 날짜 컬럼으로 간주할 최소 파싱 성공률 (0.0 ~ 1.0)
# 예: 0.5 = 50% 이상의 값이 날짜로 파싱되어야 날짜 컬럼으로 인식
DATE_COLUMN_MIN_RATIO = 0.5

# 텍스트 컬럼으로 간주할 최소 평균 문자열 길이
# 예: 20 = 평균 20자 이상이어야 텍스트 컬럼으로 인식
TEXT_COLUMN_MIN_AVG_LENGTH = 20.0

# 우선 인식할 날짜 컬럼 이름들 (정확히 일치 시 우선 선택)
PREFERRED_DATE_COLUMN_NAMES = ['날짜', 'date', '일자', '접수일', '작성일']

# 우선 인식할 텍스트 컬럼 이름들 (정확히 일치 시 우선 선택)
PREFERRED_TEXT_COLUMN_NAMES = ['문의 내용', 'content', '내용', '설명', 'description', '메모']


def detect_columns(
    df: pd.DataFrame,
    date_min_ratio: float = DATE_COLUMN_MIN_RATIO,
    text_min_avg_length: float = TEXT_COLUMN_MIN_AVG_LENGTH
) -> Dict[str, Any]:
    """
    데이터프레임에서 날짜, 텍스트, 카테고리 컬럼을 자동으로 감지합니다.
    
    감지 로직:
    1. 날짜 컬럼:
       - 우선: PREFERRED_DATE_COLUMN_NAMES에 있는 이름 찾기
       - 차선: 각 컬럼의 값을 날짜로 파싱 시도하여 성공률이 높은 컬럼 선택
       - 기준: date_min_ratio 이상의 성공률 필요
    
    2. 텍스트 컬럼:
       - 우선: PREFERRED_TEXT_COLUMN_NAMES에 있는 이름 찾기
       - 차선: object 타입 컬럼 중 평균 문자열 길이가 가장 긴 컬럼 선택
       - 기준: text_min_avg_length 이상의 평균 길이 필요
       - 날짜 컬럼은 제외
    
    3. 카테고리 컬럼:
       - 날짜, 텍스트 컬럼을 제외한 나머지 모든 컬럼
    
    Args:
        df: 분석할 데이터프레임
        date_min_ratio: 날짜 컬럼으로 인식할 최소 파싱 성공률 (0.0 ~ 1.0)
        text_min_avg_length: 텍스트 컬럼으로 인식할 최소 평균 길이
    
    Returns:
        {
            "dateColumn": str | None,
            "textualColumn": str | None,
            "categoricalColumns": List[str]
        }
    
    Examples:
        >>> df = pd.DataFrame({
        ...     "날짜": ["2024-01-01", "2024-01-02"],
        ...     "문의 내용": ["이것은 긴 텍스트입니다...", "또 다른 긴 텍스트..."],
        ...     "카테고리": ["A", "B"]
        ... })
        >>> detect_columns(df)
        {
            "dateColumn": "날짜",
            "textualColumn": "문의 내용",
            "categoricalColumns": ["카테고리"]
        }
    
    Notes:
        - 빈 데이터프레임이면 모든 값이 None 또는 빈 리스트
        - 컬럼 이름이 정확히 일치하면 파싱 없이 우선 선택 (성능 최적화)
    """
    # 빈 데이터프레임 체크
    if df is None or df.empty or len(df.columns) == 0:
        return {
            "dateColumn": None,
            "textualColumn": None,
            "categoricalColumns": [],
        }
    
    header_cols: List[str] = list(df.columns)
    
    # ========================================
    # 1. 날짜 컬럼 감지
    # ========================================
    date_column: Optional[str] = None
    
    # 1-1. 우선순위: 정확히 일치하는 컬럼 이름 찾기
    for preferred_name in PREFERRED_DATE_COLUMN_NAMES:
        if preferred_name in df.columns:
            date_column = preferred_name
            break
    
    # 1-2. 차선: 날짜 파싱 성공률이 높은 컬럼 찾기
    if date_column is None:
        date_candidates: Dict[str, float] = {}
        
        for col in df.columns:
            try:
                # 각 컬럼의 값을 날짜로 파싱 시도
                parsed = df[col].apply(try_parse_date)
                # 성공률 계산 (None이 아닌 비율)
                ratio = parsed.notnull().mean()
                
                # 최소 성공률 이상이면 후보로 등록
                if ratio >= date_min_ratio:
                    date_candidates[col] = ratio
            except Exception:
                # 파싱 중 예외 발생 시 해당 컬럼은 날짜가 아님
                continue
        
        # 가장 성공률이 높은 컬럼 선택
        if date_candidates:
            date_column = max(date_candidates, key=date_candidates.get)
    
    # ========================================
    # 2. 텍스트 컬럼 감지
    # ========================================
    textual_column: Optional[str] = None
    
    # 2-1. 우선순위: 정확히 일치하는 컬럼 이름 찾기
    for preferred_name in PREFERRED_TEXT_COLUMN_NAMES:
        if preferred_name in df.columns and preferred_name != date_column:
            textual_column = preferred_name
            break
    
    # 2-2. 차선: 평균 문자열 길이가 가장 긴 object 타입 컬럼 찾기
    if textual_column is None:
        best_len = -1.0
        
        for col in df.columns:
            # 날짜 컬럼은 제외
            if col == date_column:
                continue
            
            # object 타입 (문자열) 컬럼만 대상
            if df[col].dtype == object:
                try:
                    # null이 아닌 값들의 평균 길이 계산
                    non_null_values = df[col].dropna()
                    if len(non_null_values) > 0:
                        avg_len = non_null_values.astype(str).map(len).mean()
                        
                        # 최소 길이 이상이고, 현재까지 최대 길이인 경우
                        if avg_len >= text_min_avg_length and avg_len > best_len:
                            best_len = avg_len
                            textual_column = col
                except Exception:
                    # 길이 계산 중 예외 발생 시 해당 컬럼은 텍스트가 아님
                    continue
    
    # ========================================
    # 3. 카테고리 컬럼 = 나머지 모든 컬럼
    # ========================================
    categorical_columns = [
        c for c in header_cols 
        if c not in [date_column, textual_column]
    ]
    
    return {
        "dateColumn": date_column,
        "textualColumn": textual_column,
        "categoricalColumns": categorical_columns,
    }

