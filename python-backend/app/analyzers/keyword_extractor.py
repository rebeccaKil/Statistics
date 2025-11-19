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
    "문의", "요청", "확인", "있나요", "있습니다", "해주세요",
    # 조사/어미
    "중", "했는데", "했으나", "됩니다", "되었습니다", "합니다", "입니다",
    "하고", "에서", "으로", "하면", "그런데", "때문", "어떻게",
    # 상태 표현
    "안됨", "이상", "불가",
    # 주의: "여부", "가능"은 병합 규칙에서 사용되므로 불용어에서 제외
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
    # 여행 문의 관련 통합 규칙
    {
        "target": "확정 여부",
        "required": ["확정", "여부"],
        "optional": ["예약", "문의", "확인", "가능"]
    },
    {
        "target": "예약 가능 여부",
        "required": ["가능"],
        "optional": ["예약", "여부", "문의", "확인", "날짜", "진행"]
    },
    {
        "target": "취소 가능 여부",
        "required": ["취소", "가능"],
        "optional": ["여부", "문의", "확인", "요청"]
    },
    {
        "target": "픽업/드랍",
        "required": [],
        "optional": ["픽업", "드랍", "관련", "문의", "장소", "시간", "위치"]
    },
    {
        "target": "상품 문의",
        "required": [],
        "optional": ["상품", "투어", "이용", "출발", "시간", "현장", "지불금", "진행"]
    },
    {
        "target": "불만/민원",
        "required": [],
        "optional": ["불만", "민원"]
    },
    {
        "target": "취소 사유",
        "required": ["취소", "사유"],
        "optional": ["문의", "확인", "거절"]
    },
    {
        "target": "취소 사유",
        "required": [],
        "optional": ["거절", "사유"]
    },
    {
        "target": "취소 요청",
        "required": ["취소", "요청"],
        "optional": ["문의", "가능", "여부"]
    },
    {
        "target": "상세 일정 문의",
        "required": ["일정"],
        "optional": ["상세", "세부", "문의", "확인", "출발", "시간", "투어"]
    },
    {
        "target": "예약 확인",
        "required": ["예약", "확인"],
        "optional": ["문의", "여부", "가능", "건", "내역"]
    },
    {
        "target": "일정 변경",
        "required": ["일정", "변경"],
        "optional": ["문의", "가능", "여부", "요청"]
    },
    {
        "target": "환불 관련",
        "required": ["환불"],
        "optional": ["관련", "문의", "여부", "전액", "추가", "진행"]
    },
    {
        "target": "옵션/포함사항",
        "required": [],
        "optional": ["옵션", "포함", "사항", "불포함", "문의", "확인", "변경", "상세"]
    },
    {
        "target": "취소 수수료",
        "required": ["취소", "수수료"],
        "optional": ["문의", "확인", "환불"]
    },
    {
        "target": "예약 취소",
        "required": ["예약", "취소"],
        "optional": ["문의", "요청", "가능", "여부"]
    },
    # 기존 오류 관련 규칙
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
    {
        "target": "마케팅 수신거부 미준수",
        "required": ["마케팅", "수신거부"],  # "마케팅"과 "수신거부" 모두 필수 (더 구체적으로 매칭)
        "optional": ["수신", "거부", "알림", "메일", "푸시", "받음", "했으나", "미준수"]
    },
    {
        "target": "예약 확인 불가",
        "required": ["예약", "확인"],
        "optional": ["불가", "안됨", "안된다", "확인불가", "예약건", "예약내역", "결제", "완료", "했으나", "안된다고"]
    },
]


def _split_long_token(token: str) -> str:
    """
    긴 토큰을 의미 단위로 분리하여 띄어쓰기 추가
    
    예:
        "쿠폰적용불가문의" -> "쿠폰 적용 불가 문의"
        "채팅서버연결중으로채팅불가" -> "채팅 서버 연결 중으로 채팅 불가"
    
    Args:
        token: 분리할 토큰
    
    Returns:
        띄어쓰기가 추가된 토큰
    """
    if len(token) <= 2:
        return token
    
    # 일반적인 한국어 단어 패턴으로 분리 시도
    # 2-3글자 단위로 분리하되, 의미 있는 단어 경계 찾기
    import re
    
    # 한글 단어 패턴: 2-4글자 단위로 분리
    # 예: "쿠폰적용불가문의" -> ["쿠폰", "적용", "불가", "문의"]
    parts = []
    i = 0
    
    while i < len(token):
        # 2-3글자 단위로 분리 시도
        if i + 3 <= len(token):
            # 3글자 단위로 분리
            parts.append(token[i:i+3])
            i += 3
        elif i + 2 <= len(token):
            # 2글자 단위로 분리
            parts.append(token[i:i+2])
            i += 2
        else:
            # 남은 1글자
            if parts:
                parts[-1] += token[i]
            else:
                parts.append(token[i])
            i += 1
    
    # 결과가 너무 많으면 2글자씩으로 재분리
    if len(parts) > 6:
        parts = []
        i = 0
        while i < len(token):
            if i + 2 <= len(token):
                parts.append(token[i:i+2])
                i += 2
            else:
                if parts:
                    parts[-1] += token[i]
                else:
                    parts.append(token[i])
                i += 1
    
    return " ".join(parts)


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
    # 원본 텍스트와 키워드 매핑을 저장 (띄어쓰기 보존용)
    # 키: 정규화된 키워드(공백 제거), 값: 원본 텍스트에서 추출한 키워드(띄어쓰기 포함)
    original_keyword_map: Dict[str, str] = {}
    tokens: List[str] = []
    
    for t in texts:
        # null 또는 빈 텍스트 스킵
        if not t:
            continue
        
        # 원본 텍스트 유지 (결과 표시용)
        original_text = str(t).strip()
        
        # 원본에 띄어쓰기가 있는지 확인
        has_original_spaces = " " in original_text
        
        # 분석 시에는 띄어쓰기 제거 (일관된 분석을 위해)
        # "마케팅 수신거부"와 "마케팅수신거부"를 동일하게 처리
        text_for_analysis = original_text.replace(" ", "")
        
        # ========================================
        # 0. 병합 규칙에 해당하는 키워드 먼저 추출
        # ========================================
        # 원본 텍스트에서 병합 규칙에 해당하는 키워드를 먼저 찾아서 추출
        # 더 구체적인 규칙을 먼저 체크하기 위해 우선순위 정렬
        matched_merge_keyword = None
        text_lower = text_for_analysis.lower()
        
        # 우선순위: 필수 키워드가 많은 규칙을 먼저 체크 (더 구체적인 규칙 우선)
        # required가 빈 리스트인 규칙은 텍스트 추출 단계에서는 제외 (나중에 병합 단계에서 처리)
        sorted_rules = [r for r in merge_rules if r["required"]]  # required가 있는 규칙만 체크
        sorted_rules = sorted(sorted_rules, key=lambda r: (-len(r["required"]), r["target"]))
        
        for rule in sorted_rules:
            # 특수 케이스: "마케팅 수신거부 미준수" (required에 "수신거부"가 있지만 "수신"과 "거부"로 분리될 수 있음)
            if rule["target"] == "마케팅 수신거부 미준수":
                has_marketing = "마케팅" in text_lower
                has_susin_geobu = "수신거부" in text_lower
                has_susin = "수신" in text_lower
                has_geobu = "거부" in text_lower
                
                # "마케팅"과 ("수신거부" 또는 ("수신"과 "거부"))가 모두 있어야 함
                if has_marketing and (has_susin_geobu or (has_susin and has_geobu)):
                    # 원본 텍스트에 "미준수"가 포함되어 있는지 확인
                    has_mijunsu = "미준수" in text_lower or "미준" in text_lower
                    
                    # 원본 텍스트에서 "마케팅 수신거부" 부분 추출
                    if has_original_spaces:
                        # 원본에서 "마케팅"과 "수신거부" 관련 부분 찾기
                        original_words = original_text.split()
                        matched_words = []
                        found_marketing = False
                        found_susin_geobu = False
                        found_mijunsu_word = False
                        
                        for word in original_words:
                            word_lower = word.lower().replace(" ", "")
                            if "마케팅" in word_lower and not found_marketing:
                                matched_words.append(word)
                                found_marketing = True
                            elif ("수신거부" in word_lower or ("수신" in word_lower and "거부" in word_lower)) and not found_susin_geobu:
                                matched_words.append(word)
                                found_susin_geobu = True
                            elif ("미준수" in word_lower or "미준" in word_lower) and not found_mijunsu_word:
                                matched_words.append(word)
                                found_mijunsu_word = True
                            
                            if found_marketing and found_susin_geobu:
                                # "미준수"가 있으면 계속 찾고, 없으면 중단
                                if not has_mijunsu:
                                    break
                                elif found_mijunsu_word:
                                    break
                        
                        if matched_words and found_marketing and found_susin_geobu:
                            extracted_keyword = " ".join(matched_words)
                            # "미준수"가 포함되어 있지 않으면 rule["target"] 사용
                            if not has_mijunsu:
                                matched_merge_keyword = rule["target"]
                            else:
                                matched_merge_keyword = extracted_keyword
                        else:
                            # 단어 단위로 찾지 못했으면 원본 텍스트에서 직접 찾기
                            # "마케팅"과 "수신거부"가 포함된 연속된 부분 추출
                            original_lower = original_text.lower()
                            marketing_idx = original_lower.find("마케팅")
                            extracted_keyword = None
                            
                            if marketing_idx >= 0:
                                # "마케팅" 이후에 "수신거부" 또는 "수신"과 "거부" 찾기
                                after_marketing = original_text[marketing_idx:]
                                after_marketing_lower = after_marketing.lower()
                                
                                # "수신거부" 찾기
                                susin_geobu_idx = after_marketing_lower.find("수신거부")
                                if susin_geobu_idx >= 0:
                                    end_idx = marketing_idx + susin_geobu_idx + len("수신거부")
                                    extracted_keyword = original_text[marketing_idx:end_idx].strip()
                                else:
                                    # "수신"과 "거부" 따로 찾기
                                    susin_idx = after_marketing_lower.find("수신")
                                    if susin_idx >= 0:
                                        geobu_idx = after_marketing_lower.find("거부", susin_idx)
                                        if geobu_idx >= 0:
                                            end_idx = marketing_idx + geobu_idx + len("거부")
                                            extracted_keyword = original_text[marketing_idx:end_idx].strip()
                            
                            if not extracted_keyword:
                                matched_merge_keyword = rule["target"]
                            else:
                                # "미준수"가 포함되어 있지 않으면 rule["target"] 사용
                                if not has_mijunsu:
                                    matched_merge_keyword = rule["target"]
                                else:
                                    matched_merge_keyword = extracted_keyword
                    else:
                        # 띄어쓰기가 없으면 원본 텍스트에서 직접 찾기
                        marketing_idx = text_lower.find("마케팅")
                        extracted_keyword = None
                        
                        if marketing_idx >= 0:
                            after_marketing = text_for_analysis[marketing_idx:]
                            after_marketing_lower = after_marketing.lower()
                            
                            susin_geobu_idx = after_marketing_lower.find("수신거부")
                            if susin_geobu_idx >= 0:
                                end_idx = marketing_idx + susin_geobu_idx + len("수신거부")
                                extracted_keyword = text_for_analysis[marketing_idx:end_idx]
                            else:
                                susin_idx = after_marketing_lower.find("수신")
                                if susin_idx >= 0:
                                    geobu_idx = after_marketing_lower.find("거부", susin_idx)
                                    if geobu_idx >= 0:
                                        end_idx = marketing_idx + geobu_idx + len("거부")
                                        extracted_keyword = text_for_analysis[marketing_idx:end_idx]
                        
                        if not extracted_keyword:
                            matched_merge_keyword = rule["target"]
                        else:
                            # "미준수"가 포함되어 있지 않으면 rule["target"] 사용
                            if not has_mijunsu:
                                matched_merge_keyword = rule["target"]
                            else:
                                matched_merge_keyword = extracted_keyword
                    break
            
            # 일반적인 병합 규칙
            elif all(req in text_lower for req in rule["required"]):
                # 원본 텍스트에서 필수 키워드가 포함된 부분 추출
                if has_original_spaces:
                    original_words = original_text.split()
                    matched_words = []
                    required_found = {req: False for req in rule["required"]}
                    
                    for word in original_words:
                        word_lower = word.lower().replace(" ", "")
                        for req in rule["required"]:
                            if req in word_lower and not required_found[req]:
                                matched_words.append(word)
                                required_found[req] = True
                                break
                        
                        if all(required_found.values()):
                            break
                    
                    if matched_words and all(required_found.values()):
                        matched_merge_keyword = rule["target"]
                    else:
                        matched_merge_keyword = rule["target"]
                else:
                    matched_merge_keyword = rule["target"]
                break
        
        # 병합 규칙에 해당하는 키워드가 있으면 그것을 사용하고 다음 텍스트로
        if matched_merge_keyword:
            tokens.append(matched_merge_keyword)
            continue
        
        # 형태소 분석 수행
        toks = tokenize_ko(text_for_analysis)
        
        # 숫자만으로 된 토큰 제거
        # 이유: "123", "456" 같은 숫자는 키워드로 의미 없음
        toks = [tok for tok in toks if len(tok) > 1 and not tok.isdigit()]
        
        # 토큰이 없으면 원본 텍스트를 그대로 사용 (전체 숫자 맞추기 위해)
        if not toks:
            # 원본 텍스트를 키워드로 사용 (불용어만 있거나 토큰이 없는 경우)
            tokens.append(original_text)
            continue

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
            
            # 규칙에 해당 없으면 단일 토큰 추가
            else:
                combined.append(toks[i])
                i += 1
        
        # ========================================
        # 3. 원본 텍스트의 띄어쓰기 우선 사용
        # ========================================
        # 원본에 띄어쓰기가 있으면, 원본 텍스트에서 해당 키워드 부분을 찾아 띄어쓰기 보존
        if has_original_spaces and combined:
            # 원본 텍스트를 단어 단위로 분리 (띄어쓰기 기준)
            original_words = original_text.split()
            original_text_no_space = "".join(original_words).lower()
            
            # 토큰들을 원본 텍스트의 단어들과 매칭하여 띄어쓰기 보존
            matched_keyword = None
            
            # 형태소 분석 결과를 원본 텍스트와 매칭
            # 토큰 시퀀스를 원본 텍스트에서 찾기
            token_sequence = "".join([t.replace(" ", "") for t in combined]).lower()
            
            # 원본 텍스트에서 토큰 시퀀스가 포함된 부분 찾기
            if token_sequence in original_text_no_space:
                # 원본 텍스트에서 해당 부분의 시작과 끝 위치 찾기
                start_idx = original_text_no_space.find(token_sequence)
                end_idx = start_idx + len(token_sequence)
                
                # 원본 단어들에서 해당 범위에 포함되는 단어들 찾기
                char_pos = 0
                matched_words = []
                for word in original_words:
                    word_no_space = word.replace(" ", "").lower()
                    word_start = char_pos
                    word_end = char_pos + len(word_no_space)
                    
                    # 단어가 토큰 시퀀스 범위와 겹치면 포함
                    if word_start < end_idx and word_end > start_idx:
                        matched_words.append(word)
                    
                    char_pos = word_end
                    
                    # 모든 토큰을 포함했으면 종료
                    if char_pos >= end_idx:
                        break
                
                if matched_words:
                    matched_keyword = " ".join(matched_words)
            
            # 매칭 실패 시, 단어 단위로 재시도
            if not matched_keyword:
                # 각 토큰이 원본 단어에 포함되는지 확인
                matched_words = []
                token_idx = 0
                for word in original_words:
                    word_no_space = word.replace(" ", "").lower()
                    if token_idx < len(combined):
                        token_no_space = combined[token_idx].replace(" ", "").lower()
                        if token_no_space in word_no_space or word_no_space in token_no_space:
                            matched_words.append(word)
                            token_idx += 1
                            if token_idx >= len(combined):
                                break
                
                if matched_words and len(matched_words) == len(combined):
                    matched_keyword = " ".join(matched_words)
            
            # 원본에서 매칭된 키워드가 있으면 사용
            if matched_keyword:
                final_keyword = matched_keyword
            else:
                # 매칭 실패 시 기존 로직 사용
                if len(combined) > 1:
                    final_keyword = " ".join(combined)
                elif len(combined) == 1:
                    single_token = combined[0]
                    if len(single_token) >= 4:
                        final_keyword = _split_long_token(single_token)
                    else:
                        final_keyword = single_token
                else:
                    # combined가 비어있으면 원본 텍스트를 그대로 사용
                    final_keyword = original_text
        else:
            # 원본에 띄어쓰기가 없으면 기존 로직 사용
            if len(combined) > 1:
                final_keyword = " ".join(combined)
            elif len(combined) == 1:
                single_token = combined[0]
                if len(single_token) >= 4:
                    final_keyword = _split_long_token(single_token)
                else:
                    final_keyword = single_token
            else:
                # combined가 비어있으면 원본 텍스트를 그대로 사용
                final_keyword = original_text
        
        # 정규화된 키워드(공백 제거)를 키로 하여 원본 띄어쓰기 보존
        normalized_key = normalize_value(final_keyword)
        if normalized_key not in original_keyword_map:
            original_keyword_map[normalized_key] = final_keyword
        
        tokens.append(final_keyword)

    # ========================================
    # 3. 토큰 개수 집계 (공백 무시하여 통계 집계)
    # ========================================
    # 통계 집계는 공백을 무시하고 수행
    normalized_counts: Dict[str, Tuple[int, str]] = {}
    
    for token in tokens:
        # 원본 토큰 유지 (띄어쓰기 포함)
        original_token = token
        
        # 병합 규칙 체크용: 공백 제거 버전 (비교용)
        normalized_token = normalize_value(token)
        
        # 정규화된 키워드로 개수 집계 (공백 무시)
        if normalized_token not in normalized_counts:
            normalized_counts[normalized_token] = (1, original_token)
        else:
            existing_count, existing_token = normalized_counts[normalized_token]
            # 원본 띄어쓰기가 있는 토큰을 우선 사용
            if " " in original_token and " " not in existing_token:
                normalized_counts[normalized_token] = (existing_count + 1, original_token)
            else:
                normalized_counts[normalized_token] = (existing_count + 1, existing_token)
    
    # ========================================
    # 4. 유사 키워드 병합
    # ========================================
    # 키: 정규화된 키워드(비교용), 값: (개수, 원본 키워드 - 띄어쓰기 포함)
    merged_counts: Dict[str, Tuple[int, str]] = {}
    
    for normalized_key, (count, original_token) in normalized_counts.items():
        # 병합 규칙 적용
        merged = False
        # 우선순위: required가 있는 규칙을 먼저 체크, required가 빈 리스트인 규칙은 나중에 체크
        rules_with_required = [r for r in merge_rules if r["required"]]
        rules_without_required = [r for r in merge_rules if not r["required"]]
        sorted_rules = sorted(rules_with_required, key=lambda r: (-len(r["required"]), r["target"])) + rules_without_required
        
        for rule in sorted_rules:
            # 필수 키워드가 모두 포함되어 있는지 확인 (공백 제거 버전으로 비교)
            # 예: "확정", "먹통"이 모두 있으면 "확정 관련 먹통"으로 병합
            required_matched = all(req in normalized_key for req in rule["required"])
            
            # 특수 케이스: "마케팅 수신거부 미준수"의 경우 "수신"과 "거부"가 분리되어도 인식
            if rule["target"] == "마케팅 수신거부 미준수":
                # "마케팅"이 있고, ("수신거부" 또는 ("수신"과 "거부"가 모두) 있으면 병합
                has_marketing = "마케팅" in normalized_key
                has_susin_geobu = "수신거부" in normalized_key
                has_susin = "수신" in normalized_key
                has_geobu = "거부" in normalized_key
                
                if has_marketing and (has_susin_geobu or (has_susin and has_geobu)):
                    # 원본에 띄어쓰기가 있으면 그것을 우선 사용
                    # 원본에 "마케팅 수신거부" 관련 키워드가 있으면 그것을 사용
                    if " " in original_token:
                        # 원본에 "마케팅"과 "수신거부" 관련 키워드가 모두 포함되어 있는지 확인
                        original_lower = original_token.lower()
                        if "마케팅" in original_lower and ("수신거부" in original_lower or ("수신" in original_lower and "거부" in original_lower)):
                            target = original_token
                        else:
                            # 원본에 일부만 있으면 규칙의 target 사용
                            target = rule["target"]
                    else:
                        # 원본에 띄어쓰기가 없으면 규칙의 target 사용
                        target = rule["target"]
                    
                    # 병합 키는 정규화된 버전 사용 (공백 무시)
                    merge_key = normalize_value(target)
                    if merge_key not in merged_counts:
                        merged_counts[merge_key] = (count, target)
                    else:
                        existing_count, existing_target = merged_counts[merge_key]
                        # 원본 띄어쓰기가 있는 경우 우선 사용
                        if " " in target and " " not in existing_target:
                            merged_counts[merge_key] = (existing_count + count, target)
                        else:
                            merged_counts[merge_key] = (existing_count + count, existing_target)
                    merged = True
                    break
            
            # required가 빈 리스트인 경우: optional 키워드 중 특정 키워드들이 포함되어야 병합
            elif len(rule["required"]) == 0:
                # 특수 처리: 각 규칙별로 필요한 키워드 조합 확인
                if rule["target"] == "픽업/드랍":
                    # "픽업" 또는 "드랍"이 포함되어 있어야 함
                    has_pickup = "픽업" in normalized_key
                    has_drop = "드랍" in normalized_key
                    if has_pickup or has_drop:
                        target = rule["target"]
                    else:
                        continue
                elif rule["target"] == "옵션/포함사항":
                    # "옵션" 또는 "포함"이 포함되어 있어야 함
                    has_option = "옵션" in normalized_key
                    has_include = "포함" in normalized_key
                    if has_option or has_include:
                        target = rule["target"]
                    else:
                        continue
                elif rule["target"] == "불만/민원":
                    # "불만" 또는 "민원"이 반드시 포함되어 있어야 함
                    # 단, "일정"이 포함된 경우는 제외 (일정 문의와 구분)
                    has_complaint = "불만" in normalized_key
                    has_grievance = "민원" in normalized_key
                    has_schedule = "일정" in normalized_key
                    if (has_complaint or has_grievance) and not has_schedule:
                        target = rule["target"]
                    else:
                        continue
                elif rule["target"] == "상품 문의":
                    product_keywords = ["상품", "투어", "이용", "현장", "지불금", "출발", "시간"]
                    if any(pk in normalized_key for pk in product_keywords):
                        target = rule["target"]
                    else:
                        continue
                elif rule["target"] == "취소 사유":
                    if "거절" in normalized_key and "사유" in normalized_key:
                        target = rule["target"]
                    else:
                        continue
                else:
                    # 다른 규칙은 optional 키워드 중 하나라도 매칭되면 병합
                    optional_matched = any(opt in normalized_key for opt in rule["optional"])
                    if optional_matched:
                        target = rule["target"]
                    else:
                        continue
                
                # 병합 키는 정규화된 버전 사용 (공백 무시)
                merge_key = normalize_value(target)
                if merge_key not in merged_counts:
                    merged_counts[merge_key] = (count, target)
                else:
                    existing_count, existing_target = merged_counts[merge_key]
                    merged_counts[merge_key] = (existing_count + count, existing_target)
                merged = True
                break
            
            # 일반적인 병합 규칙
            elif required_matched:
                # 원본에 띄어쓰기가 있으면 그것을 우선 사용
                if " " in original_token:
                    # 원본에 필수 키워드가 모두 포함되어 있는지 확인
                    original_lower = original_token.lower()
                    if all(req in original_lower for req in rule["required"]):
                        target = original_token
                    else:
                        # 원본에 일부만 있으면 규칙의 target 사용
                        target = rule["target"]
                else:
                    # 원본에 띄어쓰기가 없으면 규칙의 target 사용
                    target = rule["target"]
                
                # 특수 처리: "예약 가능" -> "예약 가능 여부"로 병합
                # "예약 가능"이 "예약 가능 여부" 규칙에 매칭되도록
                if rule["target"] == "예약 가능 여부":
                    has_possible = "가능" in normalized_key or "가능여부" in normalized_key
                    has_reservation = "예약" in normalized_key or "진행" in normalized_key or "예약가능" in normalized_key
                    if has_possible and (has_reservation or "가능여부" in normalized_key):
                        target = rule["target"]
                elif rule["target"] == "취소 가능 여부":
                    # "취소"와 "가능"이 모두 있으면 "취소 가능 여부"로 병합
                    if "취소" in normalized_key and "가능" in normalized_key:
                        target = rule["target"]
                
                # 병합 키는 정규화된 버전 사용 (공백 무시)
                merge_key = normalize_value(target)
                if merge_key not in merged_counts:
                    merged_counts[merge_key] = (count, target)
                else:
                    existing_count, existing_target = merged_counts[merge_key]
                    # 원본 띄어쓰기가 있는 경우 우선 사용
                    if " " in target and " " not in existing_target:
                        merged_counts[merge_key] = (existing_count + count, target)
                    else:
                        merged_counts[merge_key] = (existing_count + count, existing_target)
                merged = True
                break
        
        # 병합 규칙에 해당 없으면 원본 토큰(띄어쓰기 포함)으로 집계
        if not merged:
            # 정규화된 키를 사용하여 통계 집계 (공백 무시)
            # 하지만 최종 반환값은 원본 토큰을 유지
            if normalized_key not in merged_counts:
                # 첫 번째로 나온 원본 토큰을 저장
                merged_counts[normalized_key] = (count, original_token)
            else:
                # 기존 항목의 개수 증가
                existing_count, existing_token = merged_counts[normalized_key]
                # 원본 띄어쓰기가 있는 토큰을 우선 사용
                if " " in original_token and " " not in existing_token:
                    merged_counts[normalized_key] = (existing_count + count, original_token)
                else:
                    merged_counts[normalized_key] = (existing_count + count, existing_token)
    
    # ========================================
    # 5. 상위 N개 추출
    # ========================================
    # (개수, 원본 키워드) 튜플로 변환
    # merged_counts의 값은 (count, original_token) 튜플이므로 원본 토큰을 가져옴
    final_items = [(count, original_token) for key, (count, original_token) in merged_counts.items()]
    
    # 개수 많은 순으로 정렬
    top = sorted(final_items, key=lambda x: x[0], reverse=True)[:top_n]
    
    # 딕셔너리 형태로 변환 (원본 토큰 사용 - 띄어쓰기 포함)
    return [{"name": original_token, "count": int(count)} for count, original_token in top]

