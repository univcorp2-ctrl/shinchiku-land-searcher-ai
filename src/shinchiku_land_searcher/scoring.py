from __future__ import annotations

import re
from typing import Any

from shinchiku_land_searcher.models import AnalysisConfig, PropertyRecord, ScoreResult

TITLE_ALIASES = ("物件名", "名称", "タイトル", "name", "title", "B")
PRICE_ALIASES = ("価格", "販売価格", "物件価格", "金額", "price")
YIELD_ALIASES = ("利回り", "表面利回り", "想定利回り", "満室利回り", "yield")
WALK_ALIASES = ("徒歩", "駅徒歩", "徒歩分", "最寄駅徒歩", "walk", "walking")
AGE_ALIASES = ("築年", "築年数", "築", "建築年", "築年月", "age")
AREA_ALIASES = ("所在地", "住所", "エリア", "address", "location")
STRUCTURE_ALIASES = ("構造", "建物構造", "structure")


def analyze_records(records: list[PropertyRecord], config: AnalysisConfig) -> list[ScoreResult]:
    scored = [_score_record(record, config) for record in records]
    scored.sort(key=lambda item: item.score, reverse=True)
    return [
        ScoreResult(
            rank=i,
            row_number=item.row_number,
            score=item.score,
            title=item.title,
            url=item.url,
            price_man_yen=item.price_man_yen,
            gross_yield_percent=item.gross_yield_percent,
            walking_minutes=item.walking_minutes,
            building_age_years=item.building_age_years,
            recommendation=item.recommendation,
            reasons=item.reasons,
            risks=item.risks,
            raw=item.raw,
        )
        for i, item in enumerate(scored, start=1)
    ]


def _score_record(record: PropertyRecord, config: AnalysisConfig) -> ScoreResult:
    raw = record.raw
    title = str(_get(raw, TITLE_ALIASES) or f"Row {record.row_number}")
    price = parse_price_man_yen(_get(raw, PRICE_ALIASES))
    gross_yield = parse_percent(_get(raw, YIELD_ALIASES))
    walk = parse_minutes(_get(raw, WALK_ALIASES))
    age = parse_age_years(_get(raw, AGE_ALIASES))

    reasons: list[str] = []
    risks: list[str] = []
    score = 50.0

    if gross_yield is None:
        risks.append("利回りが未取得のため収益性を要確認")
        score -= 8
    else:
        if gross_yield >= config.min_gross_yield_percent + 2:
            score += 22
            reasons.append(f"表面利回りが高め: {gross_yield:.2f}%")
        elif gross_yield >= config.min_gross_yield_percent:
            score += 13
            reasons.append(f"最低利回り条件を満たす: {gross_yield:.2f}%")
        else:
            score -= 18
            risks.append(f"利回りが基準未満: {gross_yield:.2f}%")

    if price is None:
        risks.append("価格が未取得のため総投資額を要確認")
        score -= 5
    elif config.max_price_man_yen is not None:
        if price <= config.max_price_man_yen:
            score += 10
            reasons.append(f"予算内: {price:.0f}万円")
        else:
            over = price - config.max_price_man_yen
            score -= min(18, over / max(config.max_price_man_yen, 1) * 30)
            risks.append(f"予算超過: {price:.0f}万円")

    if walk is None:
        risks.append("駅徒歩が未取得のため賃貸需要を要確認")
        score -= 4
    elif walk <= 7:
        score += 12
        reasons.append(f"駅徒歩が近い: {walk:.0f}分")
    elif walk <= config.max_walking_minutes:
        score += 6
        reasons.append(f"駅徒歩が許容範囲: {walk:.0f}分")
    else:
        score -= 12
        risks.append(f"駅徒歩が遠め: {walk:.0f}分")

    if age is None:
        risks.append("築年数が未取得のため修繕リスクを要確認")
        score -= 3
    elif age <= config.prefer_newer_than_years:
        score += 10
        reasons.append(f"築年数が比較的浅い: {age:.0f}年")
    elif age <= config.max_building_age_years:
        score += 2
        reasons.append(f"築年数は許容範囲: {age:.0f}年")
    else:
        score -= 14
        risks.append(f"築古の修繕リスク: {age:.0f}年")

    all_text = " ".join(str(v) for v in raw.values() if v not in (None, ""))
    found_keywords = [keyword for keyword in config.risk_keywords if keyword in all_text]
    if found_keywords:
        penalty = min(25, 7 * len(found_keywords))
        score -= penalty
        risks.append("注意キーワード: " + ", ".join(found_keywords))

    if not record.url.startswith(("http://", "https://")):
        score -= 8
        risks.append("URLが未取得またはURL形式ではない")

    score = max(0.0, min(100.0, round(score, 1)))
    recommendation = _recommendation(score, risks)

    return ScoreResult(
        rank=0,
        row_number=record.row_number,
        score=score,
        title=title,
        url=record.url,
        price_man_yen=price,
        gross_yield_percent=gross_yield,
        walking_minutes=walk,
        building_age_years=age,
        recommendation=recommendation,
        reasons=reasons or ["追加確認に値するが、主要指標の取得状況を確認してください"],
        risks=risks,
        raw=raw,
    )


def _recommendation(score: float, risks: list[str]) -> str:
    severe_words = ("再建築不可", "告知事項", "旧耐震", "予算超過")
    if score >= 78 and not any(any(word in risk for word in severe_words) for risk in risks):
        return "最優先で資料確認"
    if score >= 65:
        return "優先検討"
    if score >= 50:
        return "条件次第で検討"
    return "後回し / 除外候補"


def _norm(value: str) -> str:
    return re.sub(r"[\s_（）()\[\]【】/・:：-]+", "", value.lower())


def _get(raw: dict[str, Any], aliases: tuple[str, ...]) -> Any:
    normalized = {_norm(str(key)): value for key, value in raw.items()}
    for alias in aliases:
        key = _norm(alias)
        if key in normalized and normalized[key] not in (None, ""):
            return normalized[key]
    for raw_key, value in raw.items():
        raw_key_norm = _norm(str(raw_key))
        if any(_norm(alias) in raw_key_norm for alias in aliases) and value not in (None, ""):
            return value
    return None


def parse_percent(value: Any) -> float | None:
    if value in (None, ""):
        return None
    if isinstance(value, int | float):
        number = float(value)
        return number * 100 if 0 < number <= 1 else number
    match = re.search(r"[-+]?\d+(?:\.\d+)?", str(value).replace(",", ""))
    if not match:
        return None
    return float(match.group(0))


def parse_minutes(value: Any) -> float | None:
    if value in (None, ""):
        return None
    if isinstance(value, int | float):
        return float(value)
    text = str(value).replace(",", "")
    match = re.search(r"徒歩\s*(\d+(?:\.\d+)?)\s*分|駅\s*(\d+(?:\.\d+)?)\s*分|(\d+(?:\.\d+)?)\s*分", text)
    if match:
        return float(next(group for group in match.groups() if group))
    generic = re.search(r"\d+(?:\.\d+)?", text)
    return float(generic.group(0)) if generic else None


def parse_age_years(value: Any) -> float | None:
    if value in (None, ""):
        return None
    if isinstance(value, int | float):
        return float(value)
    text = str(value).strip()
    if "新築" in text:
        return 0.0
    match = re.search(r"築\s*(\d+(?:\.\d+)?)\s*年|(\d+(?:\.\d+)?)\s*年", text)
    if match:
        return float(next(group for group in match.groups() if group))
    year_match = re.search(r"(19\d{2}|20\d{2})", text)
    if year_match:
        # Static approximation for ranking. Users should verify exact completion date.
        return max(0.0, 2026 - float(year_match.group(1)))
    generic = re.search(r"\d+(?:\.\d+)?", text)
    return float(generic.group(0)) if generic else None


def parse_price_man_yen(value: Any) -> float | None:
    if value in (None, ""):
        return None
    if isinstance(value, int | float):
        number = float(value)
        # Excel values are often yen. Smaller values are usually already man-yen.
        return number / 10000 if number >= 100000 else number

    text = str(value).replace(",", "").replace("円", "").strip()
    oku = 0.0
    man = 0.0
    oku_match = re.search(r"(\d+(?:\.\d+)?)\s*億", text)
    man_match = re.search(r"(\d+(?:\.\d+)?)\s*万", text)
    if oku_match:
        oku = float(oku_match.group(1)) * 10000
    if man_match:
        man = float(man_match.group(1))
    if oku_match or man_match:
        return oku + man

    match = re.search(r"\d+(?:\.\d+)?", text)
    if not match:
        return None
    number = float(match.group(0))
    return number / 10000 if number >= 100000 else number
