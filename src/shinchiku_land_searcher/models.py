from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PropertyRecord:
    row_number: int
    url: str
    raw: dict[str, Any]


@dataclass(frozen=True)
class ScoreResult:
    rank: int
    row_number: int
    score: float
    title: str
    url: str
    price_man_yen: float | None
    gross_yield_percent: float | None
    walking_minutes: float | None
    building_age_years: float | None
    recommendation: str
    reasons: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AnalysisConfig:
    max_price_man_yen: float | None = None
    min_gross_yield_percent: float = 6.0
    max_walking_minutes: float = 12.0
    max_building_age_years: float = 35.0
    prefer_newer_than_years: float = 20.0
    risk_keywords: tuple[str, ...] = (
        "借地", "再建築不可", "告知事項", "旧耐震", "既存不適格", "傾き", "雨漏り", "滞納", "サブリース"
    )


@dataclass(frozen=True)
class RequestProfile:
    name: str = ""
    email: str = ""
    phone: str = ""
    postal_code: str = ""
    address: str = ""
    message: str = "資料を確認したく、物件資料の送付をお願いいたします。"
