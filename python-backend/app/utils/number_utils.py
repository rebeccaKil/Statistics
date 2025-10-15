import re
from typing import Any, Optional
import pandas as pd


def to_number(value: Any) -> Optional[float]:
    """
    다양한 형식의 수치 데이터를 float로 변환합니다.
    
    지원하는 형식:
    - 정수/실수: 123, 45.67
    - 쉼표 포함: 1,234,567
    - 퍼센트: 12.5%, -3.2%
    - 증감 기호: ▲123, ▼45 (▲는 양수, ▼는 음수로 변환)
    - 플러스/마이너스: +123, -45
    - 공백 포함: " 123 ", "1 234"
    
    Args:
        value: 변환할 값 (문자열, 숫자, 기타)
    
    Returns:
        float 값 또는 None (변환 실패 시)
    
    Examples:
        >>> to_number("1,234.56")
        1234.56
        >>> to_number("▲12.5%")
        12.5
        >>> to_number("▼100")
        -100.0
        >>> to_number("abc")
        None
    
    Notes:
        - ▼ 기호는 음수로 처리 (주로 감소율 표시)
        - ▲ 기호는 양수로 처리 (주로 증가율 표시)
        - % 기호는 제거만 하고 100으로 나누지 않음 (12.5%는 12.5로 변환)
    """
    # None 체크
    if value is None:
        return None
    
    # pandas NA 체크
    if pd.isna(value):
        return None
    
    # 이미 숫자인 경우
    if isinstance(value, (int, float)):
        # NaN/Inf 체크
        if pd.isna(value) or value == float('inf') or value == float('-inf'):
            return None
        return float(value)
    
    # 문자열로 변환
    s = str(value).strip()
    
    # 빈 문자열 또는 null 문자열 체크
    if not s or s.lower() in {'nan', 'none', 'null', 'na', 'n/a', '-'}:
        return None
    
    # 원본 문자열 보존 (디버깅용)
    original_s = s
    
    # 1. 쉼표 제거 (천 단위 구분자)
    # 예: "1,234,567" -> "1234567"
    s = s.replace(',', '')
    
    # 2. 공백 제거
    # 예: "1 234" -> "1234"
    s = s.replace(' ', '')
    
    # 3. 증감 기호 처리
    # ▼는 음수로, ▲는 양수로 처리
    is_negative = False
    if '▼' in s:
        is_negative = True
        s = s.replace('▼', '')
    if '▲' in s:
        s = s.replace('▲', '')
    
    # 4. 퍼센트 제거 (값은 그대로 유지)
    # 예: "12.5%" -> "12.5" (12.5로 변환, 0.125가 아님)
    s = s.replace('%', '')
    
    # 5. 플러스 기호 제거
    s = s.replace('+', '')
    
    # 6. 기타 특수문자 제거 (숫자, 점, 마이너스만 남김)
    # 예: "₩1,234원" -> "1234"
    s = re.sub(r'[^0-9.\-]', '', s)
    
    # 7. 유효성 검사
    # 빈 문자열, 점만, 마이너스만 있는 경우 무효
    if not s or s in {'-', '.', '-.', '.-'}:
        return None
    
    # 8. 여러 개의 점이 있는 경우 무효 (예: "12.34.56")
    if s.count('.') > 1:
        return None
    
    # 9. 여러 개의 마이너스가 있는 경우 무효 (예: "12--34")
    if s.count('-') > 1:
        return None
    
    # 10. 마이너스가 중간에 있는 경우 무효 (예: "12-34")
    if '-' in s and not s.startswith('-'):
        return None
    
    # 11. float 변환 시도
    try:
        result = float(s)
        
        # 12. 증감 기호에 따라 부호 조정
        if is_negative:
            result = -abs(result)
        
        return result
    except (ValueError, OverflowError):
        # 변환 실패 - 디버깅 정보는 로그로 남기지 않고 None 반환
        return None

