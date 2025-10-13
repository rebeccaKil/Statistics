from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from collections import Counter
import numpy as np
import pandas as pd
import numpy as np
from datetime import datetime

# NLP imports with graceful fallbacks
try:
    from konlpy.tag import Okt  # type: ignore
    okt: Optional[Okt] = Okt()
except Exception:
    okt = None

try:
    import nltk  # type: ignore
    # Ensure punkt is available (safe to call multiple times)
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
except Exception:
    nltk = None  # type: ignore


class AnalyzeRequest(BaseModel):
    rows: List[Dict[str, Any]]
    year: int
    month: int
    reportType: str  # 'single' | 'comparison'


class Component(BaseModel):
    component_type: str
    title: str
    source_column: str
    icon: str
    color: str
    data: Any


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes


@app.get("/health")
def health():
    return {"status": "healthy"}


def try_parse_date(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, (datetime,)):
        return value
    if isinstance(value, (int, float)):
        return None
    s = str(value)
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"):
        try:
            return datetime.strptime(s[:19], fmt)
        except Exception:
            continue
    try:
        return pd.to_datetime(s, errors='coerce').to_pydatetime()
    except Exception:
        return None


def detect_columns(df: pd.DataFrame) -> Dict[str, Any]:
    header_cols: List[str] = list(df.columns)
    # 1) 날짜 컬럼: 우선 순위 '날짜' 명시 → 없으면 파싱 비율로 탐지
    if '날짜' in df.columns:
        date_column = '날짜'
    else:
        date_candidates = {}
        for col in df.columns:
            parsed = df[col].apply(try_parse_date)
            ratio = parsed.notnull().mean()
            if ratio > 0.5:  # more than half parseable as date
                date_candidates[col] = ratio
        date_column = max(date_candidates, key=date_candidates.get) if date_candidates else None

    # 2) 텍스트 컬럼: 우선 순위 '문의 내용' → 없으면 평균 길이 최대
    if '문의 내용' in df.columns:
        textual_column = '문의 내용'
    else:
        textual_column = None
        best_len = -1.0
        for col in df.columns:
            if col == date_column:
                continue
            if df[col].dtype == object:
                avg_len = df[col].dropna().astype(str).map(len).mean() if len(df[col].dropna()) > 0 else 0
                if avg_len > best_len:
                    best_len = avg_len
                    textual_column = col

    # 3) 카테고리 컬럼: "첫 번째 행의 헤더 그대로"에서 날짜/텍스트 컬럼을 제외한 나머지 전부
    categorical_columns = [c for c in header_cols if c not in [date_column, textual_column]]

    return {
        "dateColumn": date_column,
        "textualColumn": textual_column,
        "categoricalColumns": categorical_columns,
    }


def tokenize_ko(text: str) -> List[str]:
    """한국어 문장 토큰화 (띄어쓰기 제거 + 불용어 제거)"""
    if not text:
        return []
    # 1) 띄어쓰기 제거
    t = text.replace(" ", "")
    
    # 2) 형태소 분석
    if okt is not None:
        try:
            tokens = okt.morphs(t)
        except Exception:
            import re
            tokens = re.findall(r"[\w\d가-힣]+", t)
    else:
        import re
        tokens = re.findall(r"[\w\d가-힣]+", t)
    
    # 3) 불용어 제거
    stopwords = {
        "문의", "요청", "여부", "확인", "중", "했는데", "했으나", "됩니다", "되었습니다", 
        "안됨", "이상", "가능", "불가", "있나요", "있습니다", "해주세요",
        "합니다", "입니다", "하고", "에서", "으로", "하면", "그런데", "때문", "어떻게"
    }
    tokens = [tok for tok in tokens if tok not in stopwords and len(tok) > 1]
    
    return tokens


def simple_category(text: str) -> str:
    """간단 규칙 기반 카테고리 분류 (사용자 도메인 룰 반영)"""
    t = (text or "").replace(" ", "").lower()
    toks = tokenize_ko(t)
    tokset = set(toks)
    # 바이그램 결합으로 '가능 여부' 등도 검출
    bigrams = {f"{toks[i]} {toks[i+1]}" for i in range(len(toks)-1)}

    def hit(key: str) -> bool:
        return (key in tokset) or (key in bigrams) or (key in t)

    rules = [
        ("예약 가능 여부", {"가능", "가능여부", "예약가능", "이용가능", "가능 여부"}),
        ("예약 확정 관련", {"확정", "확인", "확정여부", "예약확정", "확정 여부", "예약 확인"}),
        ("취소/환불", {"취소", "환불", "수수료", "요청", "취소사유", "취소 사유"}),
        ("특가/프로모션", {"특가", "할인", "종료", "프로모션", "특가 종료"}),
        ("예약 변경", {"변경", "일정", "날짜", "숙박일", "옵션", "예약 변경"}),
        ("추가 인원/옵션", {"추가", "인원", "아동", "어린이", "룸", "객실"}),
        ("픽업/교통", {"픽업", "미팅", "복귀", "이동", "차량", "공항", "미팅장소"}),
        ("후기/리뷰", {"후기", "리뷰", "댓글", "작성"}),
        ("결제/오류", {"결제", "로그인", "에러", "오류", "실패", "앱", "사이트", "바우처"}),
        ("파트너/현지", {"파트너", "가이드", "현지", "연락처", "모객"}),
    ]
    for label, keywords in rules:
        if any(hit(k) for k in keywords):
            return label
    return "기타"


def extract_keywords(texts: List[str], top_n: int = 5) -> List[Dict[str, Any]]:
    """문의 내용에서 주요 키워드 추출 (결합 규칙 적용 + 유사 키워드 병합)"""
    tokens: List[str] = []
    join_suffixes = {"여부", "문의", "확인", "요청", "변경", "오류"}
    combine_rules = {("취소", "환불"), ("취소", "요청"), ("예약", "확인"), ("특가", "종료"), ("확정", "여부")}

    for t in texts:
        if not t:
            continue
        s = str(t).replace(" ", "")
        toks = tokenize_ko(s)
        toks = [tok for tok in toks if len(tok) > 1 and not tok.isdigit()]

        i = 0
        combined: List[str] = []
        while i < len(toks):
            if i + 1 < len(toks) and (toks[i + 1] in join_suffixes):
                combined.append(f"{toks[i]} {toks[i + 1]}")
                i += 2
            elif i + 1 < len(toks) and (toks[i], toks[i + 1]) in combine_rules:
                combined.append(f"{toks[i]} {toks[i + 1]}")
                i += 2
            else:
                combined.append(toks[i])
                i += 1

        tokens.extend(combined)

    # 유사 키워드 병합 규칙 (우선순위 높은 순서대로 정의)
    merge_rules = [
        # 확정 관련 먹통 (확정 + 먹통이 함께 있으면 병합)
        {
            "target": "확정 관련 먹통",
            "required": ["확정", "먹통"],  # 반드시 포함되어야 할 키워드
            "optional": ["버튼", "페이지", "등"]  # 추가로 매칭 가능한 키워드
        },
        # 로그인 오류
        {
            "target": "로그인 오류",
            "required": ["로그인"],
            "optional": ["오류", "세션", "접속", "실패"]
        },
        # 사이트 오류
        {
            "target": "사이트 오류",
            "required": ["사이트"],
            "optional": ["오류", "접속불가", "서버", "에러"]
        },
        # 앱 오류
        {
            "target": "앱 오류",
            "required": ["앱"],
            "optional": ["오류", "모바일", "어플", "업데이트", "에러"]
        },
        # 결제/환불 오류
        {
            "target": "결제/환불 오류",
            "required": ["결제"],
            "optional": ["오류", "환불", "카드", "수수료", "쿠폰", "마일리지", "에러"]
        },
    ]
    
    # 병합된 카운트
    merged_counts: Dict[str, int] = {}
    counts = Counter(tokens)
    
    for token, count in counts.items():
        merged = False
        for rule in merge_rules:
            # 필수 키워드가 모두 포함되어 있는지 확인
            if all(req in token for req in rule["required"]):
                merged_counts[rule["target"]] = merged_counts.get(rule["target"], 0) + count
                merged = True
                break
        
        if not merged:
            merged_counts[token] = merged_counts.get(token, 0) + count
    
    top = sorted(merged_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    # 프론트 차트 포맷(name, count)
    return [{"name": k, "count": int(v)} for k, v in top]


def build_tfidf_matrix(texts: List[str]):
    docs_tokens = []
    for t in texts:
        toks = tokenize_ko(str(t).replace(" ", ""))
        toks = [tok for tok in toks if len(tok) > 1 and not tok.isdigit()]
        docs_tokens.append(toks)

    vocab_map: Dict[str, int] = {}
    for toks in docs_tokens:
        for tok in toks:
            if tok not in vocab_map:
                vocab_map[tok] = len(vocab_map)

    N = len(docs_tokens)
    V = len(vocab_map)
    if V == 0 or N == 0:
        return np.zeros((N, 1), dtype=np.float32), []

    # term frequency
    X = np.zeros((N, V), dtype=np.float32)
    df = np.zeros(V, dtype=np.float32)
    for i, toks in enumerate(docs_tokens):
        if not toks:
            continue
        counts = Counter(toks)
        for tok, cnt in counts.items():
            j = vocab_map[tok]
            X[i, j] = cnt
        for tok in set(toks):
            df[vocab_map[tok]] += 1

    # tf-idf
    idf = np.log((N + 1) / (df + 1)) + 1.0
    X = X * idf
    # l2 normalize
    norms = np.linalg.norm(X, axis=1, keepdims=True) + 1e-9
    X = X / norms
    vocab = [None] * V
    for tok, j in vocab_map.items():
        vocab[j] = tok
    return X, vocab


def kmeans_simple(X: np.ndarray, k: int = 5, max_iter: int = 20, seed: int = 42):
    n = X.shape[0]
    if n == 0:
        return np.array([]), np.array([])
    k = min(k, n)
    rng = np.random.default_rng(seed)
    idx = rng.choice(n, size=k, replace=False)
    centers = X[idx].copy()
    for _ in range(max_iter):
        # assign
        # cosine distance -> maximize dot product, so use negative for argmin trick
        sims = X @ centers.T
        labels = np.argmax(sims, axis=1)
        # update
        new_centers = np.zeros_like(centers)
        for j in range(k):
            members = X[labels == j]
            if len(members) == 0:
                new_centers[j] = centers[j]
            else:
                vec = members.mean(axis=0)
                norm = np.linalg.norm(vec) + 1e-9
                new_centers[j] = vec / norm
        if np.allclose(new_centers, centers):
            break
        centers = new_centers
    return labels, centers


def month_filter(df: pd.DataFrame, date_col: Optional[str], year: int, month: int) -> pd.DataFrame:
    if not date_col or date_col not in df.columns:
        return df.iloc[0:0]
    parsed = df[date_col].apply(try_parse_date)
    return df[(parsed.dt.year == year) & (parsed.dt.month == month)]


def calc_stats(df: pd.DataFrame, date_col: Optional[str], cat_cols: List[str], text_col: Optional[str] = None) -> Optional[Dict[str, Any]]:
    if df is None or df.empty:
        return None

    total_count = len(df)
    # daily counts (date_col 있을 때만)
    peak_day = {"date": "N/A", "count": 0}
    daily_list: List[Dict[str, Any]] = []
    
    if date_col and date_col in df.columns:
        parsed = df[date_col].apply(try_parse_date)
        dates = parsed.dt.strftime('%Y-%m-%d')
        daily_counts = dates.value_counts().to_dict()
        if daily_counts:
            peak_day_iso = max(daily_counts, key=daily_counts.get)
            peak_day_count = int(daily_counts[peak_day_iso])
            d = datetime.strptime(peak_day_iso, "%Y-%m-%d")
            peak_day = {"date": f"{d.month}월 {d.day}일", "count": peak_day_count}
            
            # 일자별 데이터 생성 (상위 10개)
            sorted_daily = sorted(daily_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            for date_str, count in sorted_daily:
                d = datetime.strptime(date_str, "%Y-%m-%d")
                weekday = ['월', '화', '수', '목', '금', '토', '일'][d.weekday()]
                daily_list.append({
                    "date": f"{d.month}월 {d.day}일 ({weekday})",
                    "count": int(count)
                })

    # distributions
    distributions: Dict[str, List[Dict[str, Any]]] = {}
    for col in cat_cols:
        if col not in df.columns:
            distributions[col] = []
            continue
        vc = df[col].astype(str).str.strip().value_counts()
        top = vc.head(5)
        distributions[col] = [
            {"name": str(idx), "count": int(cnt)} for idx, cnt in top.items()
        ]
    
    # 주요 문의 요약 생성 (text_col 기준)
    summary_items: List[str] = []
    if text_col and text_col in df.columns:
        try:
            texts = df[text_col].astype(str).tolist()
            keywords_data = extract_keywords(texts, top_n=5)
            for item in keywords_data[:4]:  # 상위 4개만
                summary_items.append(f"[{item['name']}] {item['count']}건")
        except Exception:
            pass

    return {
        "total_count": int(total_count),
        "peak_day": peak_day,
        "distributions": distributions,
        "daily_list": daily_list,
        "summary_items": summary_items,
    }


def build_components_single(stats: Dict[str, Any], cat_cols: List[str]) -> List[Component]:
    components: List[Component] = []
    components.append(Component(
        component_type='kpi',
        title='총 문의 수',
        source_column='total_count',
        icon='hash',
        color='indigo',
        data={"value": stats["total_count"], "unit": "건", "subtitle": ""}
    ))

    components.append(Component(
        component_type='kpi',
        title='피크 일자',
        source_column='peak_day',
        icon='trending-up',
        color='orange',
        data={"value": stats["peak_day"]["count"], "unit": "건", "subtitle": stats["peak_day"]["date"]}
    ))

    for col in cat_cols:
        components.append(Component(
            component_type='bar_chart',
            title=('AI-분석 문의 유형' if col == 'ai_category' else f'{col}별 분포'),
            source_column=col,
            icon='pie-chart',
            color='sky',
            data=stats["distributions"].get(col, [])
        ))
    return components


def build_components_comparison(curr: Dict[str, Any], prev: Optional[Dict[str, Any]], cat_cols: List[str], curr_month: int, prev_month: int) -> List[Component]:
    # prev가 없어도 비교 차트를 표시 (0으로 표시)
    if not prev:
        prev = {
            "total_count": 0,
            "distributions": {col: [] for col in cat_cols}
        }

    components: List[Component] = []
    current_total = curr["total_count"]
    previous_total = prev["total_count"]
    change_text = "변동 없음"
    change_status = "neutral"
    if previous_total > 0:
        change = (current_total - previous_total) / previous_total * 100.0
        if change > 0.1:
            change_text = f"{round(change)}% 증가"
            change_status = "increase"
        elif change < -0.1:
            change_text = f"{round(abs(change))}% 감소"
            change_status = "decrease"
    elif current_total > 0:
        change_text = "신규 발생"
        change_status = "increase"

    components.append(Component(
        component_type='comparison_kpi',
        title='총 문의 수 비교',
        source_column='total_count',
        icon='hash',
        color='indigo',
        data={
            "current_value": current_total,
            "previous_value": previous_total,
            "unit": "건",
            "change_text": change_text,
            "change_status": change_status,
            "current_label": f"{curr_month}월",
            "previous_label": f"{prev_month}월",
        }
    ))

    # 일일 최대 문의 비교 추가
    current_peak = curr.get("peak_day", {"date": "N/A", "count": 0})
    previous_peak = prev.get("peak_day", {"date": "N/A", "count": 0})
    
    peak_change_text = "변동 없음"
    peak_change_status = "neutral"
    if previous_peak["count"] > 0:
        peak_change = (current_peak["count"] - previous_peak["count"]) / previous_peak["count"] * 100.0
        if peak_change > 0.1:
            peak_change_text = f"{round(peak_change)}% 증가"
            peak_change_status = "increase"
        elif peak_change < -0.1:
            peak_change_text = f"{round(abs(peak_change))}% 감소"
            peak_change_status = "decrease"
    elif current_peak["count"] > 0:
        peak_change_text = "신규 발생"
        peak_change_status = "increase"

    components.append(Component(
        component_type='comparison_kpi',
        title='일일 최대 문의',
        source_column='peak_day',
        icon='trending-up',
        color='orange',
        data={
            "current_value": current_peak["count"],
            "previous_value": previous_peak["count"],
            "unit": "건",
            "change_text": peak_change_text,
            "change_status": peak_change_status,
            "current_label": f"{curr_month}월 {current_peak['date'].split('-')[2]}일" if current_peak["date"] != "N/A" and '-' in current_peak["date"] and len(current_peak["date"].split('-')) >= 3 else f"{curr_month}월",
            "previous_label": f"{prev_month}월 {previous_peak['date'].split('-')[2]}일" if previous_peak["date"] != "N/A" and '-' in previous_peak["date"] and len(previous_peak["date"].split('-')) >= 3 else f"{prev_month}월",
        }
    ))

    for col in cat_cols:
        current_list = curr["distributions"].get(col, [])
        prev_list = prev["distributions"].get(col, [])
        names = sorted(set([i["name"] for i in current_list] + [i["name"] for i in prev_list]))
        current_map = {i["name"]: i["count"] for i in current_list}
        prev_map = {i["name"]: i["count"] for i in prev_list}
        comparison = [{"name": n, "current_count": int(current_map.get(n, 0)), "prev_count": int(prev_map.get(n, 0))} for n in names]
        components.append(Component(
            component_type='comparison_bar_chart',
            title=('AI-분석 문의 유형 비교' if col == 'ai_category' else f'{col}별 비교'),
            source_column=col,
            icon='pie-chart',
            color='sky',
            data={
                "comparison": comparison,
                "current_label": f"{curr_month}월",
                "previous_label": f"{prev_month}월",
            }
        ))
    return components


@app.post("/analyze", response_model=List[Component])
def analyze(req: AnalyzeRequest):
    try:
        df = pd.DataFrame(req.rows or [])
        # 헤더 정규화: 앞뒤 공백 제거
        df.columns = df.columns.map(lambda x: str(x).strip())
        if df.empty:
            return []

        schema = detect_columns(df)
        date_col = schema.get("dateColumn")
        text_col = schema.get("textualColumn")
        cat_cols: List[str] = schema.get("categoricalColumns", [])

        # AI-분석 문의 유형 제거 (사용자 요청)

        # 기준 연/월: 사용자가 선택한 연/월 사용
        target_year = req.year
        target_month = req.month

        # current month stats with fallback
        current_df = month_filter(df, date_col, target_year, target_month)
        current_stats = calc_stats(current_df, date_col, cat_cols, text_col)

        if not current_stats:
            # 폴백 1: date_col이 없거나 선택 월 데이터가 없으면 최신 월로 자동 선택
            if date_col and date_col in df.columns:
                parsed = df[date_col].apply(try_parse_date)
                # 유효 날짜만 모아서 최신 연월 계산
                valid = parsed.dropna()
                if not valid.empty:
                    latest = valid.max()
                    fallback_year, fallback_month = latest.year, latest.month
                    current_df = month_filter(df, date_col, fallback_year, fallback_month)
                    current_stats = calc_stats(current_df, date_col, cat_cols, text_col)

            # 폴백 2: 그래도 없으면 전체 데이터로 집계(피크일자는 N/A)
            if not current_stats:
                current_stats = calc_stats(df, None, cat_cols, text_col)

        if req.reportType == 'single' or not date_col:
            components = build_components_single(current_stats, cat_cols)
            
            # 일자별 데이터 추가
            if current_stats.get("daily_list"):
                components.append(Component(
                    component_type='daily_breakdown',
                    title=f'{target_month}월 일자별 오류 현황',
                    source_column='daily_breakdown',
                    icon='calendar',
                    color='cyan',
                    data=current_stats["daily_list"]
                ))
            
            # 주요 오류 요약 추가
            if current_stats.get("summary_items"):
                components.append(Component(
                    component_type='summary',
                    title=f'{target_month}월 주요 오류 내용 요약',
                    source_column='summary',
                    icon='alert-triangle',
                    color='rose',
                    data={"items": current_stats["summary_items"]}
                ))
            
            # 키워드 분석만 남김 (클러스터 분포 제거)
            try:
                if text_col and text_col in df.columns:
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

        # comparison with previous month
        prev_month = 12 if req.month == 1 else req.month - 1
        prev_year = req.year - 1 if req.month == 1 else req.year
        previous_df = month_filter(df, date_col, prev_year, prev_month)
        previous_stats = calc_stats(previous_df, date_col, cat_cols, text_col) if date_col else None
        components = build_components_comparison(current_stats, previous_stats, cat_cols, target_month, prev_month)
        
        # 일자별 데이터 추가
        if current_stats.get("daily_list"):
            components.append(Component(
                component_type='daily_breakdown',
                title=f'{target_month}월 일자별 오류 현황',
                source_column='daily_breakdown',
                icon='calendar',
                color='cyan',
                data=current_stats["daily_list"]
            ))
        
        # 주요 오류 요약 추가
        if current_stats.get("summary_items"):
            components.append(Component(
                component_type='summary',
                title=f'{target_month}월 주요 오류 내용 요약',
                source_column='summary',
                icon='alert-triangle',
                color='rose',
                data={"items": current_stats["summary_items"]}
            ))
        # 비교 리포트에도 키워드만 추가 (클러스터 분포 제거)
        try:
            if text_col and text_col in df.columns:
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
    except Exception as e:
        # readable error for frontend
        return JSONResponse(status_code=400, content={"error": str(e)})


