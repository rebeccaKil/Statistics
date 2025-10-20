from typing import Dict, Any, List, Optional
from ..models import Component
import pandas as pd
from ..utils.date_utils import try_parse_date


# ============================================================
# 컴포넌트 빌더 설정 상수
# ============================================================

# 비교 분석에서 변화를 감지할 최소 임계값 (%)
# 이유: 0.1% 미만의 변화는 "변동 없음"으로 처리
# 예: 100건 -> 100건 (0% 변화) -> "변동 없음"
#     100건 -> 105건 (5% 증가) -> "5% 증가"
CHANGE_THRESHOLD_PERCENT = 0.1


def build_components_single(
    stats: Dict[str, Any], 
    cat_cols: List[str]
) -> List[Component]:
    """
    단일 월 리포트의 인포그래픽 컴포넌트를 생성합니다.
    
    생성되는 컴포넌트:
    1. 총 문의 수 KPI
    2. 피크 일자 KPI  
    3. 각 카테고리별 분포 막대 차트
    
    Args:
        stats: calc_stats()에서 반환한 통계 딕셔너리
        cat_cols: 카테고리 컬럼 이름 리스트
    
    Returns:
        Component 객체 리스트
    
    Examples:
        >>> stats = {
        ...     "total_count": 100,
        ...     "peak_day": {"date": "1월 15일", "count": 20},
        ...     "distributions": {"유형": [{"name": "A", "count": 50}]}
        ... }
        >>> components = build_components_single(stats, ["유형"])
        >>> len(components)
        3  # KPI 2개 + 막대 차트 1개
    
    Notes:
        - stats가 None이거나 필수 키가 없으면 빈 리스트 반환
        - 카테고리 컬럼이 stats에 없으면 빈 데이터로 차트 생성
    """
    components: List[Component] = []
    
    # stats 유효성 검사
    if not stats or "total_count" not in stats or "peak_day" not in stats:
        return components
    
    # ========================================
    # 1. 총 문의 수 KPI
    # ========================================
    components.append(Component(
        component_type='kpi',
        title='총 문의 수',
        source_column='total_count',
        icon='hash',  # # 아이콘 (숫자 의미)
        color='indigo',
        data={
            "value": stats["total_count"], 
            "unit": "건", 
            "subtitle": ""
        }
    ))

    # ========================================
    # 2. 피크 일자 KPI
    # ========================================
    components.append(Component(
        component_type='kpi',
        title='피크 일자',
        source_column='peak_day',
        icon='trending-up',  # 상승 아이콘
        color='orange',
        data={
            "value": stats["peak_day"]["count"], 
            "unit": "건", 
            "subtitle": stats["peak_day"]["date"]  # "M월 D일" 형식
        }
    ))

    # ========================================
    # 3. 카테고리별 분포 막대 차트
    # ========================================
    for col in cat_cols:
        components.append(Component(
            component_type='bar_chart',
            title=f'{col}별 분포',
            source_column=col,
            icon='pie-chart',
            color='sky',
            data=stats.get("distributions", {}).get(col, [])
        ))
    
    return components


def build_components_comparison(
    curr: Dict[str, Any], 
    prev: Optional[Dict[str, Any]], 
    cat_cols: List[str], 
    curr_month: int, 
    prev_month: int,
    change_threshold: float = CHANGE_THRESHOLD_PERCENT
) -> List[Component]:
    """
    월 비교 리포트의 인포그래픽 컴포넌트를 생성합니다.
    
    생성되는 컴포넌트:
    1. 총 문의 수 비교 KPI (증감률 포함)
    2. 일일 최대 문의 비교 KPI
    3. 각 카테고리별 비교 막대 차트
    
    Args:
        curr: 현재 월 통계 딕셔너리
        prev: 이전 월 통계 딕셔너리 (None이면 0으로 간주)
        cat_cols: 카테고리 컬럼 이름 리스트
        curr_month: 현재 월 (1~12)
        prev_month: 이전 월 (1~12)
        change_threshold: 변화 감지 임계값 (%) - 이보다 작으면 "변동 없음"
    
    Returns:
        Component 객체 리스트
    
    Examples:
        >>> curr = {"total_count": 105, "peak_day": {"date": "1월 15일", "count": 20}}
        >>> prev = {"total_count": 100, "peak_day": {"date": "12월 10일", "count": 18}}
        >>> components = build_components_comparison(curr, prev, [], 1, 12)
        >>> components[0].data["change_text"]
        "5% 증가"
    
    Notes:
        - prev가 None이면 이전 데이터 없음으로 처리
        - 변화율이 change_threshold 미만이면 "변동 없음"
        - **버그 수정**: peak_day["date"]는 "M월 D일" 형식이므로 "-"로 split 불가
    """
    # 이전 데이터가 없으면 기본값 설정
    if not prev:
        prev = {
            "total_count": 0,
            "peak_day": {"date": "N/A", "count": 0},
            "distributions": {col: [] for col in cat_cols}
        }

    components: List[Component] = []
    
    # ========================================
    # 1. 총 문의 수 비교 KPI
    # ========================================
    current_total = curr.get("total_count", 0)
    previous_total = prev.get("total_count", 0)
    
    # 변화율 계산 및 텍스트 생성
    change_text = "변동 없음"
    change_status = "neutral"
    
    if previous_total > 0:
        # 변화율 (%) 계산
        change = (current_total - previous_total) / previous_total * 100.0
        
        # 임계값 이상이면 증감 표시
        if change > change_threshold:
            change_text = f"{round(change)}% 증가"
            change_status = "increase"
        elif change < -change_threshold:
            change_text = f"{round(abs(change))}% 감소"
            change_status = "decrease"
    elif current_total > 0:
        # 이전 데이터 없고 현재 데이터 있으면 신규
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

    # ========================================
    # 2. 일일 최대 문의 비교 KPI
    # ========================================
    current_peak = curr.get("peak_day", {"date": "N/A", "count": 0})
    previous_peak = prev.get("peak_day", {"date": "N/A", "count": 0})
    
    # 피크 변화율 계산
    peak_change_text = "변동 없음"
    peak_change_status = "neutral"
    
    if previous_peak["count"] > 0:
        peak_change = (current_peak["count"] - previous_peak["count"]) / previous_peak["count"] * 100.0
        if peak_change > change_threshold:
            peak_change_text = f"{round(peak_change)}% 증가"
            peak_change_status = "increase"
        elif peak_change < -change_threshold:
            peak_change_text = f"{round(abs(peak_change))}% 감소"
            peak_change_status = "decrease"
    elif current_peak["count"] > 0:
        peak_change_text = "신규 발생"
        peak_change_status = "increase"

    # 라벨 생성 - **버그 수정**
    # peak_day["date"]는 "M월 D일" 형식 (예: "1월 15일")
    # 기존 코드는 "YYYY-MM-DD" 형식으로 가정하고 split('-')했으나 오류 발생
    # 해결: date를 그대로 사용
    current_label = f"{curr_month}월"
    previous_label = f"{prev_month}월"
    
    # 날짜가 있으면 날짜 포함 (이미 "M월 D일" 형식)
    if current_peak["date"] != "N/A":
        current_label = f"{curr_month}월 ({current_peak['date']})"
    if previous_peak["date"] != "N/A":
        previous_label = f"{prev_month}월 ({previous_peak['date']})"

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
            "current_label": current_label,
            "previous_label": previous_label,
        }
    ))

    # ========================================
    # 3. 카테고리별 비교 막대 차트
    # ========================================
    for col in cat_cols:
        # 현재/이전 월의 카테고리 분포 데이터
        current_list = curr.get("distributions", {}).get(col, [])
        prev_list = prev.get("distributions", {}).get(col, [])
        current_others = curr.get("distributions_others", {}).get(col, [])
        prev_others = prev.get("distributions_others", {}).get(col, [])
        
        # 기준월(현재월) 상위 항목 순서를 그대로 사용
        # 이유: 비교 그래프는 기준월을 기준으로 내림차순 정렬되어야 함
        names = [i["name"] for i in current_list]
        
        # 카테고리별 개수 맵 생성
        current_map = {i["name"]: i["count"] for i in current_list}
        prev_map = {i["name"]: i["count"] for i in prev_list}
        
        # 비교 데이터 생성
        comparison = [
            {
                "name": n,
                "current_count": int(current_map.get(n, 0)),
                "prev_count": int(prev_map.get(n, 0)),
            }
            for n in names
        ]

        # 기타 막대는 생성하지 않음 (요청 사항: 그래프에 '기타'는 인위적으로 추가하지 않음)
        
        components.append(Component(
            component_type='comparison_bar_chart',
            title=f'{col}별 비교',
            source_column=col,
            icon='pie-chart',
            color='sky',
            data={
                "comparison": comparison,
                "current_label": f"{curr_month}월",
                "previous_label": f"{prev_month}월",
                # 색상 힌트를 함께 전달 (프론트에서 기본값으로 사용)
                "current_color": "#0ea5e9",   # sky.text500
                "previous_color": "#38bdf8",  # sky.bar400
                "others": {
                    "current": current_others,
                    "previous": prev_others,
                }
            }
        ))
    
    return components


def build_monthly_distribution(
    df: pd.DataFrame,
    travel_date_col: str,
    title: str = '월별 여행일자 분포',
    top_n: int = 12
) -> Optional[Component]:
    """
    여행일/여행일자 컬럼 기반 월별 분포 컴포넌트를 생성합니다.

    Args:
        df: 전체 데이터프레임
        travel_date_col: 여행일/여행일자 컬럼 이름
        title: 컴포넌트 제목
        top_n: 표시할 월 개수 (기본 12)

    Returns:
        Component 또는 None (유효한 데이터 없을 때)
    """
    if travel_date_col not in df.columns:
        return None

    try:
        parsed = df[travel_date_col].apply(try_parse_date).dropna()
        if parsed.empty:
            return None

        # 월(1~12) 기준으로 합산 (연도 무시, 전체 월 분포)
        month_counts = parsed.dt.month.value_counts().sort_values(ascending=False)
        if month_counts.empty:
            return None

        # 상위 N개만 사용하되, 일반적으로 12개월 모두 노출
        month_counts = month_counts.head(top_n)
        items = [
            {"name": f"{int(m)}월", "count": int(c)}
            for m, c in month_counts.items()
        ]

        return Component(
            component_type='monthly_distribution',
            title=title,
            source_column=travel_date_col,
            icon='calendar',
            color='orange',
            data=items
        )
    except Exception:
        return None
