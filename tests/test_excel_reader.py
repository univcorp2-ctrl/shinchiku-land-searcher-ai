from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook

from shinchiku_land_searcher.excel_reader import read_property_records


def make_workbook(path: Path) -> None:
    workbook = Workbook()
    ws = workbook.active
    ws.append(["URL", "物件名", "価格"])
    ws.append(["https://example.com/a", "A物件", "1億円"])
    ws.append(["", "URLなし", "5000万円"])
    workbook.save(path)


def test_read_property_records_keeps_rows(tmp_path: Path) -> None:
    path = tmp_path / "properties.xlsx"
    make_workbook(path)
    records = read_property_records(path, url_column="A", require_url=False)
    assert len(records) == 2
    assert records[0].url == "https://example.com/a"
    assert records[0].raw["物件名"] == "A物件"


def test_read_property_records_require_url(tmp_path: Path) -> None:
    path = tmp_path / "properties.xlsx"
    make_workbook(path)
    records = read_property_records(path, url_column="A", require_url=True)
    assert len(records) == 1
    assert records[0].row_number == 2
