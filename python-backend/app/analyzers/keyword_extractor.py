from typing import List, Dict, Any, Optional, Set, Tuple
from collections import Counter
from ..normalizers.text_normalizer import normalize_value

# ============================================================
# KoNLPy 초기화 (한국어 형태소 분석기)
# ============================================================
try:
    from konlpy.tag import Okt
    # Okt: Open Korean Text - 한국어 트위터 형태소 분석기
    okt: Optional[Okt] = Okt()
except Exception:
    # KoNLPy 설치 안 되어 있으면 None (정규식 fallback 사용)
    okt = None


# ============================================================
# 한국어 불용어 (의미 없는 단어들)
# ============================================================
# 이유: 문의 데이터에 자주 나오지만 실제 의미가 없는 단어들
# 예: "문의합니다", "확인해주세요" 같은 일반적인 표현
KOREAN_STOPWORDS = {
    # 의문/요청 표현
    "문의", "요청", "여부", "확인", "있나요", "있습니다", "해주세요",
    # 조사/어미
    "중", "했는데", "했으나", "됩니다", "되었습니다", "합니다", "입니다",
    "하고", "에서", "으로", "하면", "그런데", "때문", "어떻게",
    # 상태 표현
    "안됨", "이상", "가능", "불가",
}

# ============================================================
# 키워드 결합 규칙 (프로젝트별로 수정 가능)
# ============================================================

# 1. 접미사 결합 규칙: 특정 단어 뒤에 접미사가 오면 결합
# 예: "예약" + "확인" -> "예약 확인"
# 이유: "예약 확인"이 하나의 의미 단위이므로 분리하지 않음
JOIN_SUFFIXES: Set[str] = {
    "여부", "문의", "확인", "요청", "변경", "오류"
}

# 2. 쌍 결합 규칙: 특정 단어 쌍이 함께 나오면 결합
# 예: "취소" + "환불" -> "취소 환불"
# 이유: 특정 단어 조합은 하나의 개념으로 취급
COMBINE_RULES: Set[Tuple[str, str]] = {
    ("취소", "환불"),
    ("취소", "요청"),
    ("예약", "확인"),
    ("특가", "종료"),
    ("확정", "여부"),
}

# ============================================================
# 키워드 병합 규칙 (유사 키워드를 하나로 통합)
# ============================================================
# 이유: "확정 버튼 먹통", "확정 페이지 먹통" 등을 "확정 관련 먹통"으로 통합
# 프로젝트별로 도메인에 맞게 수정 필요
MERGE_RULES: List[Dict[str, Any]] = [
    {
        "target": "확정 관련 먹통",
        "required": ["확정", "먹통"],  # 반드시 포함되어야 하는 단어
        "optional": ["버튼", "페이지", "등"]  # 선택적으로 포함될 수 있는 단어
    },
    {
        "target": "로그인 오류",
        "required": ["로그인"],
        "optional": ["오류", "세션", "접속", "실패"]
    },
    {
        "target": "사이트 오류",
        "required": ["사이트"],
        "optional": ["오류", "접속불가", "서버", "에러"]
    },
    {
        "target": "앱 오류",
        "required": ["앱"],
        "optional": ["오류", "모바일", "어플", "업데이트", "에러"]
    },
    {
        "target": "결제/환불 오류",
        "required": ["결제"],
        "optional": ["오류", "환불", "카드", "수수료", "쿠폰", "마일리지", "에러"]
    },
]


def tokenize_ko(
    text: str, 
    stopwords: Optional[Set[str]] = None,
    min_token_length: int = 2
) -> List[str]:
    """
    한국어 문장을 토큰화합니다 (형태소 분석 또는 정규식).
    
    처리 과정:
    1. 공백 제거 (일관된 토큰화를 위해)
    2. 형태소 분석 (KoNLPy Okt) 또는 정규식 fallback
    3. 불용어 제거
    4. 짧은 토큰 제거
    
    Args:
        text: 토큰화할 텍스트
        stopwords: 제거할 불용어 집합 (None이면 기본 불용어 사용)
        min_token_length: 최소 토큰 길이 (이보다 짧으면 제거)
    
    Returns:
        토큰 리스트
    
    Examples:
        >>> tokenize_ko("예약 확인 문의합니다")
        ["예약", "확인"]  # "문의합니다"는 불용어로 제거
    
    Notes:
        - KoNLPy가 없으면 정규식으로 단순 분리
        - 공백을 제거하는 이유: "예약확인"과 "예약 확인"을 동일하게 처리
    """
    if not text:
        return []
    
    # 기본 불용어 사용
    if stopwords is None:
        stopwords = KOREAN_STOPWORDS
    
    # 공백 제거 (일관된 토큰화)
    # 이유: "예약 확인"과 "예약확인"을 동일하게 처리
    t = text.replace(" ", "")
    
    # 토큰화 시도
    if okt is not None:
        try:
            # KoNLPy Okt로 형태소 분석
            # morphs(): 형태소 단위로 분리
            tokens = okt.morphs(t)
        except Exception:
            # 형태소 분석 실패 시 정규식 fallback
            import re
            tokens = re.findall(r"[\w\d가-힣]+", t)
    else:
        # KoNLPy 없으면 정규식으로 단순 분리
        import re
        tokens = re.findall(r"[\w\d가-힣]+", t)
    
    # 필터링: 불용어 제거 + 최소 길이 검사
    tokens = [
        tok for tok in tokens 
        if tok not in stopwords and len(tok) >= min_token_length
    ]
    
    return tokens


def extract_keywords(
    texts: List[str], 
    top_n: int = 5,
    join_suffixes: Optional[Set[str]] = None,
    combine_rules: Optional[Set[Tuple[str, str]]] = None,
    merge_rules: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    텍스트 리스트에서 주요 키워드를 추출합니다.
    
    처리 과정:
    1. 각 텍스트를 토큰화 (형태소 분석)
    2. 토큰 결합 규칙 적용 (예: "예약" + "확인" -> "예약 확인")
    3. 토큰 개수 집계
    4. 유사 키워드 병합 규칙 적용
    5. 상위 N개 추출
    
    Args:
        texts: 분석할 텍스트 리스트
        top_n: 추출할 상위 키워드 개수
        join_suffixes: 접미사 결합 규칙 (None이면 기본 규칙 사용)
        combine_rules: 쌍 결합 규칙 (None이면 기본 규칙 사용)
        merge_rules: 병합 규칙 (None이면 기본 규칙 사용)
    
    Returns:
        [{"name": str, "count": int}, ...] 형식의 키워드 리스트
        개수 많은 순으로 정렬됨
    
    Examples:
        >>> texts = ["예약 확인 문의", "예약 확인 문의", "취소 환불 문의"]
        >>> extract_keywords(texts, top_n=2)
        [{"name": "예약 확인", "count": 2}, {"name": "취소 환불", "count": 1}]
    
    Notes:
        - 숫자만으로 된 토큰은 제거
        - 1글자 토큰도 제거
        - 유사 키워드는 병합 (예: "확정 버튼 먹통", "확정 페이지 먹통" -> "확정 관련 먹통")
    """
    # 기본 규칙 사용
    if join_suffixes is None:
        join_suffixes = JOIN_SUFFIXES
    if combine_rules is None:
        combine_rules = COMBINE_RULES
    if merge_rules is None:
        merge_rules = MERGE_RULES
    
    # ========================================
    # 1. 토큰화 및 결합
    # ========================================
    tokens: List[str] = []
    
    for t in texts:
        # null 또는 빈 텍스트 스킵
        if not t:
            continue
        
        # 공백 제거 및 토큰화
        s = str(t).replace(" ", "")
        toks = tokenize_ko(s)
        
        # 숫자만으로 된 토큰 제거
        # 이유: "123", "456" 같은 숫자는 키워드로 의미 없음
        toks = [tok for tok in toks if len(tok) > 1 and not tok.isdigit()]

        # ========================================
        # 2. 토큰 결합 규칙 적용
        # ========================================
        i = 0
        combined: List[str] = []
        
        while i < len(toks):
            # 규칙 1: 다음 토큰이 접미사면 결합
            # 예: "예약" + "확인" -> "예약 확인"
            if i + 1 < len(toks) and toks[i + 1] in join_suffixes:
                combined.append(f"{toks[i]} {toks[i + 1]}")
                i += 2  # 2개를 소비했으므로 2칸 이동
            
            # 규칙 2: 특정 쌍 조합이면 결합
            # 예: "취소" + "환불" -> "취소 환불"
            elif i + 1 < len(toks) and (toks[i], toks[i + 1]) in combine_rules:
                combined.append(f"{toks[i]} {toks[i + 1]}")
                i += 2
            
            # 규칙에 해당 없으면 그대로 추가
            else:
                combined.append(toks[i])
                i += 1

        tokens.extend(combined)

    # ========================================
    # 3. 토큰 개수 집계
    # ========================================
    counts = Counter(tokens)
    
    # ========================================
    # 4. 유사 키워드 병합
    # ========================================
    merged_counts: Dict[str, int] = {}
    
    for token, count in counts.items():
        # 정규화 (유사 표현 통합)
        normalized_token = normalize_value(token)
        
        # 병합 규칙 적용
        merged = False
        for rule in merge_rules:
            # 필수 키워드가 모두 포함되어 있는지 확인
            # 예: "확정", "먹통"이 모두 있으면 "확정 관련 먹통"으로 병합
            if all(req in normalized_token for req in rule["required"]):
                target = rule["target"]
                merged_counts[target] = merged_counts.get(target, 0) + count
                merged = True
                break
        
        # 병합 규칙에 해당 없으면 그대로 집계
        if not merged:
            merged_counts[normalized_token] = merged_counts.get(normalized_token, 0) + count
    
    # ========================================
    # 5. 상위 N개 추출
    # ========================================
    # 개수 많은 순으로 정렬
    top = sorted(merged_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    # 딕셔너리 형태로 변환
    return [{"name": k, "count": int(v)} for k, v in top]

