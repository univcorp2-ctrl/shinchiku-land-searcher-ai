from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from shinchiku_land_searcher.models import AnalysisConfig, RequestProfile


def load_yaml(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError("Config YAML must contain a mapping at the top level.")
    return data


def load_analysis_config(path: Path | None) -> AnalysisConfig:
    data = load_yaml(path).get("analysis", {})
    if not isinstance(data, dict):
        data = {}
    return AnalysisConfig(
        max_price_man_yen=_maybe_float(data.get("max_price_man_yen")),
        min_gross_yield_percent=float(data.get("min_gross_yield_percent", 6.0)),
        max_walking_minutes=float(data.get("max_walking_minutes", 12.0)),
        max_building_age_years=float(data.get("max_building_age_years", 35.0)),
        prefer_newer_than_years=float(data.get("prefer_newer_than_years", 20.0)),
        risk_keywords=tuple(data.get("risk_keywords", AnalysisConfig().risk_keywords)),
    )


def load_request_profile(path: Path | None) -> RequestProfile:
    data = load_yaml(path).get("request_profile", {})
    if not isinstance(data, dict):
        data = {}
    return RequestProfile(
        name=str(data.get("name", "") or ""),
        email=str(data.get("email", "") or ""),
        phone=str(data.get("phone", "") or ""),
        postal_code=str(data.get("postal_code", "") or ""),
        address=str(data.get("address", "") or ""),
        message=str(data.get("message", RequestProfile().message) or ""),
    )


def _maybe_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    return float(value)
