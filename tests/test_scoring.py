from __future__ import annotations

from shinchiku_land_searcher.models import AnalysisConfig, PropertyRecord
from shinchiku_land_searcher.scoring import analyze_records, parse_age_years, parse_percent, parse_price_man_yen


def test_parsers_handle_japanese_formats() -> None:
    assert parse_price_man_yen("1億2000万円") == 12000
    assert parse_price_man_yen("6800万円") == 6800
    assert parse_percent("7.5%") == 7.5
    assert parse_percent(0.065) == 6.5
    assert parse_age_years("築18年") == 18
    assert parse_age_years("新築") == 0


def test_analyze_records_ranks_better_property_first() -> None:
    records = [
        PropertyRecord(
            row_number=2,
            url="https://example.com/good",
            raw={"物件名": "良い物件", "価格": "9000万円", "表面利回り": "8.0%", "駅徒歩": "徒歩5分", "築年数": "築10年"},
        ),
        PropertyRecord(
            row_number=3,
            url="https://example.com/risky",
            raw={"物件名": "リスク物件", "価格": "1億円", "表面利回り": "4.5%", "駅徒歩": "徒歩20分", "築年数": "築45年", "メモ": "再建築不可"},
        ),
    ]

    results = analyze_records(records, AnalysisConfig(max_price_man_yen=10000))

    assert results[0].title == "良い物件"
    assert results[0].score > results[1].score
    assert results[1].recommendation == "後回し / 除外候補"
