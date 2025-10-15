from datetime import datetime
from typing import Any, Optional
import pandas as pd


def try_parse_date(value: Any) -> Optional[datetime]:
    """
    다양한 날짜 형식을 파싱하여 datetime 객체로 반환합니다.
    
    지원하는 날짜 형식:
    - 완전한 날짜: YYYY-MM-DD, YYYY/MM/DD, YYYY.MM.DD
    - 날짜+시간: YYYY-MM-DD HH:MM:SS, YYYY/MM/DD HH:MM:SS
    - 월/일만: MM/DD, MM-DD, MM.DD (현재 연도로 보완)
    - 연/월만: YYYY-MM, YYYY/MM, MM/YYYY, MM-YYYY (1일로 보완)
    - pandas가 인식 가능한 모든 형식 (fallback)
    
    Args:
        value: 파싱할 날짜 값 (문자열, datetime, 숫자 등)
    
    Returns:
        datetime 객체 또는 None (파싱 실패 시)
    
    Examples:
        >>> try_parse_date("2024-01-15")
        datetime(2024, 1, 15, 0, 0)
        >>> try_parse_date("01/15")  # 현재 연도로 보완
        datetime(2024, 1, 15, 0, 0)
        >>> try_parse_date(None)
        None
    """
    # None 체크
    if value is None:
        return None
    
    # 이미 datetime 객체인 경우 그대로 반환
    if isinstance(value, datetime):
        return value
    
    # 숫자형은 날짜로 처리하지 않음 (엑셀 시리얼 날짜는 pandas fallback에서 처리)
    if isinstance(value, (int, float)):
        # NaN 체크
        if pd.isna(value):
            return None
        # 엑셀 시리얼 날짜 가능성 있으면 pandas에게 위임
        # 일반 숫자는 None 반환 (예: 전화번호, ID 등)
        if value < 10000:  # 1900-01-01부터 약 27년 이내 (명백히 날짜 아님)
            return None
    
    # 문자열로 변환 및 전처리
    s = str(value).strip()
    
    # 빈 문자열 체크
    if not s or s.lower() in ('nan', 'none', 'nat', 'null'):
        return None
    
    # 1. 완전한 날짜 형식 시도 (가장 일반적)
    # 이유: 대부분의 CSV 데이터는 YYYY-MM-DD 형식 사용
    date_formats = [
        "%Y-%m-%d",          # ISO 8601 표준
        "%Y/%m/%d",          # 슬래시 구분
        "%Y.%m.%d",          # 점 구분
        "%Y-%m-%d %H:%M:%S", # 날짜+시간
        "%Y/%m/%d %H:%M:%S"  # 슬래시+시간
    ]
    
    for fmt in date_formats:
        try:
            # 시간 포함 형식은 최대 19자만 사용 (밀리초 무시)
            return datetime.strptime(s[:19], fmt)
        except (ValueError, IndexError):
            continue
    
    # 2. 월/일만 있는 경우 (연도 없음)
    # 이유: "01/15" 같은 데이터는 현재 연도로 보완
    month_day_formats = ["%m/%d", "%m-%d", "%m.%d"]
    for fmt in month_day_formats:
        try:
            dt = datetime.strptime(s, fmt)
            current_year = datetime.now().year
            return datetime(current_year, dt.month, dt.day)
        except ValueError:
            continue
    
    # 3. 연/월만 있는 경우 (일 없음)
    # 이유: "2024-01" 같은 데이터는 해당 월의 1일로 보완
    month_year_formats = ["%m/%Y", "%m-%Y", "%m.%Y", "%Y-%m", "%Y/%m"]
    for fmt in month_year_formats:
        try:
            dt = datetime.strptime(s, fmt)
            return datetime(dt.year, dt.month, 1)
        except ValueError:
            continue
    
    # 4. Pandas fallback (엑셀 시리얼 날짜, 비표준 형식 등)
    # 이유: pandas는 다양한 날짜 형식을 인식할 수 있음
    try:
        parsed = pd.to_datetime(s, errors='coerce')
        if pd.notna(parsed):
            return parsed.to_pydatetime()
    except (ValueError, TypeError):
        pass
    
    # 모든 시도 실패 - None 반환
    return None

