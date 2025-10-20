import pandas as pd
import re
from typing import Dict, List, Tuple, Optional


# ============================================================
# 도메인별 정규화 규칙 (프로젝트에 맞게 수정 가능)
# ============================================================

# 1. 완전 일치 규칙: 정확히 일치하는 값들을 통합
# 예: "sns", "s.n.s", "에스엔에스" -> "SNS"
EXACT_MATCH_RULES: Dict[str, List[str]] = {
    "SNS": ["sns", "s.n.s", "에스엔에스"],
    # 공백 무시 통합 (대표 표기 선택)
    "가능여부": ["가능여부", "가능 여부"],
    "환불여부": ["환불여부", "환불 여부"],
}

# 2. 키워드 조합 규칙: 여러 키워드가 모두 포함된 경우 통합
# (keyword1, keyword2, ...) -> 정규화된 값
KEYWORD_COMBINATION_RULES: List[Tuple[Tuple[str, ...], str]] = [
    (("사이트", "이벤트"), "사이트내 이벤트"),
    (("포털", "검색"), "포털 검색"),
    (("지인", "추천"), "지인추천"),
    # 공백 유무 관계없이 동일 처리
    (("확정", "여부"), "예약확정문의"),
]

# 3. 우선순위 키워드 규칙: 특정 키워드가 포함되면 우선 처리
# [(우선순위, 키워드들, 결과값), ...]
PRIORITY_KEYWORD_RULES: List[Tuple[int, List[str], str]] = [
    # 우선순위 1: "문의"와 "확정"이 모두 있으면 "예약확정문의"
    (1, ["문의", "확정"], "예약확정문의"),
    # 우선순위 2: "문의"와 예약 확인 관련 키워드
    (2, ["문의", "예약확인"], "예약확인문의"),
    (2, ["문의", "예약됐는지"], "예약확인문의"),
    (2, ["문의", "예약되었는지"], "예약확인문의"),
    (2, ["문의", "잘예약"], "예약확인문의"),
    (2, ["문의", "예약완료"], "예약확인문의"),
]

# 4. 단일 키워드 포함 규칙: 특정 키워드가 포함되면 통합
SINGLE_KEYWORD_RULES: Dict[str, str] = {
    "줌줌투어": "줌줌투어",  # "줌줌투어"가 포함되면 -> "줌줌투어"
}

# 5. 괄호 제거 규칙: 괄호와 내용이 있으면 제거
# 예: "광고(네이버)" -> "광고"
BRACKET_REMOVAL_KEYWORDS: List[str] = ["광고"]


def normalize_value(value: str, use_custom_rules: bool = True) -> str:
    """
    데이터 값을 정규화하여 유사한 표현들을 하나로 통합합니다.
    
    정규화 규칙 (순서대로 적용):
    1. 완전 일치 규칙: 대소문자/공백 무시하고 완전히 일치하는 값 통합
    2. 우선순위 키워드 규칙: 여러 키워드 조합을 우선순위에 따라 처리
    3. 키워드 조합 규칙: 특정 키워드 조합이 있으면 통합
    4. 단일 키워드 규칙: 특정 키워드가 포함되면 통합
    5. 괄호 제거 규칙: 특정 키워드에서 괄호와 내용 제거
    
    Args:
        value: 정규화할 문자열
        use_custom_rules: 도메인 특화 규칙 사용 여부 (기본: True)
                         False로 설정하면 기본 정규화만 수행
    
    Returns:
        정규화된 문자열
    
    Examples:
        >>> normalize_value("  SNS  ")
        "SNS"
        >>> normalize_value("사이트 내 이벤트")
        "사이트내 이벤트"
        >>> normalize_value("광고(네이버)")
        "광고"
        >>> normalize_value("예약 확정 문의")
        "예약확정문의"
    
    Notes:
        - 도메인 특화 규칙은 파일 상단의 상수에서 수정 가능
        - 새로운 프로젝트에서는 use_custom_rules=False로 설정하거나
          규칙을 수정하여 사용
    """
    # None 또는 NaN 체크
    if not value or pd.isna(value):
        return value
    
    # 기본 정규화: 문자열 변환 및 양끝 공백 제거
    val = str(value).strip()
    
    # 빈 문자열이면 그대로 반환
    if not val:
        return val
    
    # 도메인 특화 규칙을 사용하지 않으면 공백 제거만 수행 후 반환
    if not use_custom_rules:
        # 모든 공백(스페이스 포함)을 제거해 표기 차이 통합
        return re.sub(r"\s+", "", val)
    
    # 비교용: 소문자 + 모든 공백 제거 버전
    val_no_space = re.sub(r"\s+", "", val)
    val_lower = val_no_space.lower()
    
    # ========================================
    # 1. 완전 일치 규칙 적용
    # ========================================
    for normalized, variants in EXACT_MATCH_RULES.items():
        if val_lower in [re.sub(r"\s+", "", v).lower() for v in variants]:
            return normalized
    
    # ========================================
    # 2. 우선순위 키워드 규칙 적용
    # ========================================
    # 우선순위 순으로 정렬하여 처리
    sorted_priority_rules = sorted(PRIORITY_KEYWORD_RULES, key=lambda x: x[0])
    for priority, keywords, result in sorted_priority_rules:
        # 모든 키워드가 포함되어 있는지 확인
        if all(kw in val_lower for kw in keywords):
            return result
    
    # ========================================
    # 3. 키워드 조합 규칙 적용
    # ========================================
    for keyword_tuple, result in KEYWORD_COMBINATION_RULES:
        # 모든 키워드가 포함되어 있는지 확인
        if all(kw in val_lower for kw in keyword_tuple):
            return result
    
    # ========================================
    # 4. 단일 키워드 규칙 적용
    # ========================================
    for keyword, result in SINGLE_KEYWORD_RULES.items():
        if keyword in val_no_space:  # 공백 무시 포함 체크
            return result
    
    # ========================================
    # 5. 괄호 제거 규칙 적용
    # ========================================
    for keyword in BRACKET_REMOVAL_KEYWORDS:
        if keyword in val:
            # 괄호가 있는 경우 괄호와 내용 제거
            if "(" in val or "（" in val:
                return keyword
    
    # 어떤 규칙에도 해당하지 않으면 공백을 제거한 값 반환(표기 통합)
    return val_no_space


def add_normalization_rule(
    rule_type: str,
    normalized_value: str,
    keywords: Optional[List[str]] = None,
    priority: int = 10
) -> None:
    """
    런타임에 정규화 규칙을 추가합니다.
    
    Args:
        rule_type: 규칙 타입 ("exact", "keyword", "combination", "single", "bracket")
        normalized_value: 정규화된 결과값
        keywords: 규칙에 사용할 키워드 리스트
        priority: 우선순위 (낮을수록 먼저 적용, 기본: 10)
    
    Examples:
        >>> add_normalization_rule("exact", "Facebook", ["페이스북", "페북", "fb"])
        >>> add_normalization_rule("keyword", "할인문의", ["할인", "문의"], priority=3)
    """
    if rule_type == "exact" and keywords:
        EXACT_MATCH_RULES[normalized_value] = keywords
    elif rule_type == "keyword" and keywords:
        PRIORITY_KEYWORD_RULES.append((priority, keywords, normalized_value))
    elif rule_type == "combination" and keywords:
        KEYWORD_COMBINATION_RULES.append((tuple(keywords), normalized_value))
    elif rule_type == "single" and keywords:
        SINGLE_KEYWORD_RULES[keywords[0]] = normalized_value
    elif rule_type == "bracket" and keywords:
        BRACKET_REMOVAL_KEYWORDS.extend(keywords)

