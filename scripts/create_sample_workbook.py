from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DIR = ROOT / "sample_data"
SAMPLE_DIR.mkdir(exist_ok=True)

workbook = Workbook()
ws = workbook.active
ws.title = "properties"
ws.append(["URL", "物件名", "価格", "表面利回り", "駅徒歩", "築年数", "所在地", "メモ"])
ws.append(["https://example.com/property/a", "駅近RCマンション", "1億2000万円", "7.2%", "徒歩6分", "築18年", "東京都", ""])
ws.append(["https://example.com/property/b", "高利回り木造", "6800万円", "9.1%", "徒歩15分", "築38年", "神奈川県", "旧耐震の可能性"])
ws.append(["https://example.com/property/c", "築浅アパート", "9200万円", "6.4%", "徒歩9分", "築8年", "千葉県", ""])
workbook.save(SAMPLE_DIR / "sample_properties.xlsx")
print(SAMPLE_DIR / "sample_properties.xlsx")
