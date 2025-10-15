from pydantic import BaseModel
from typing import Any, Dict, List


class AnalyzeRequest(BaseModel):
    rows: List[Dict[str, Any]]
    year: int
    month: int
    reportType: str


class Component(BaseModel):
    component_type: str
    title: str
    source_column: str
    icon: str
    color: str
    data: Any

