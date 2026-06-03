from __future__ import annotations

import csv
from pathlib import Path

from openpyxl import Workbook

from shinchiku_land_searcher.excel_reader import is_probable_url
from shinchiku_land_searcher.models import PropertyRecord, ScoreResult

RANKING_COLUMNS = [
    "rank", "score", "recommendation", "row_number", "title", "url", "price_man_yen",
    "gross_yield_percent", "walking_minutes", "building_age_years", "reasons", "risks",
]


def write_analysis_outputs(results: list[ScoreResult], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    write_ranking_csv(results, output_dir / "ranking.csv")
    write_ranking_xlsx(results, output_dir / "ranking.xlsx")
    write_advice_txt(results, output_dir / "advice.txt")


def write_ranking_csv(results: list[ScoreResult], path: Path) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=RANKING_COLUMNS)
        writer.writeheader()
        for result in results:
            writer.writerow(_result_row(result))


def write_ranking_xlsx(results: list[ScoreResult], path: Path) -> None:
    workbook = Workbook()
    ws = workbook.active
    ws.title = "ranking"
    ws.append(RANKING_COLUMNS)
    for result in results:
        ws.append([_result_row(result)[column] for column in RANKING_COLUMNS])
    for col in ws.columns:
        max_len = max(len(str(cell.value or "")) for cell in col)
        ws.column_dimensions[col[0].column_letter].width = min(max(max_len + 2, 10), 60)
    workbook.save(path)


def write_advice_txt(results: list[ScoreResult], path: Path, extra_ai_comment: str | None = None) -> None:
    lines: list[str] = ["# 物件検討優先順位アドバイス", ""]
    if not results:
        lines.append("分析対象の物件がありません。")
    else:
        lines.append("## 最初に見るべき物件")
        for result in results[:10]:
            lines.append(f"{result.rank}. {result.title} / {result.score:.1f}点 / {result.recommendation}")
            lines.append(f"   URL: {result.url}")
            lines.append(f"   理由: {'; '.join(result.reasons)}")
            if result.risks:
                lines.append(f"   注意: {'; '.join(result.risks)}")
        lines.extend([
            "", "## 判断の目安",
            "- 78点以上: 早めに資料を取り、レントロール・修繕履歴・管理状況を確認",
            "- 65点以上: 条件が合えば内見・追加ヒアリング",
            "- 50点以上: 価格交渉や出口戦略次第",
            "- 50点未満: 重要なリスクや情報不足が解消されるまで後回し",
        ])
    if extra_ai_comment:
        lines.extend(["", "## AI補足コメント", extra_ai_comment.strip()])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_request_plan(records: list[PropertyRecord], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "request_plan.csv"
    seen: set[str] = set()
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["index", "row_number", "url", "status", "memo"])
        writer.writeheader()
        index = 1
        for record in records:
            if not is_probable_url(record.url) or record.url in seen:
                continue
            seen.add(record.url)
            writer.writerow({
                "index": index,
                "row_number": record.row_number,
                "url": record.url,
                "status": "pending",
                "memo": "human confirmation required before final submit",
            })
            index += 1
    return path


def _result_row(result: ScoreResult) -> dict[str, object]:
    return {
        "rank": result.rank,
        "score": result.score,
        "recommendation": result.recommendation,
        "row_number": result.row_number,
        "title": result.title,
        "url": result.url,
        "price_man_yen": result.price_man_yen if result.price_man_yen is not None else "",
        "gross_yield_percent": result.gross_yield_percent if result.gross_yield_percent is not None else "",
        "walking_minutes": result.walking_minutes if result.walking_minutes is not None else "",
        "building_age_years": result.building_age_years if result.building_age_years is not None else "",
        "reasons": "; ".join(result.reasons),
        "risks": "; ".join(result.risks),
    }
