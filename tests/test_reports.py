from __future__ import annotations

from pathlib import Path

from shinchiku_land_searcher.models import PropertyRecord
from shinchiku_land_searcher.reports import write_request_plan


def test_write_request_plan_deduplicates_urls(tmp_path: Path) -> None:
    records = [
        PropertyRecord(2, "https://example.com/a", {}),
        PropertyRecord(3, "https://example.com/a", {}),
        PropertyRecord(4, "not-url", {}),
    ]

    path = write_request_plan(records, tmp_path)
    text = path.read_text(encoding="utf-8-sig")

    assert text.count("https://example.com/a") == 1
    assert "not-url" not in text
