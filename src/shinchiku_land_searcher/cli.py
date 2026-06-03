from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from shinchiku_land_searcher import __version__
from shinchiku_land_searcher.ai_advisor import generate_ai_comment
from shinchiku_land_searcher.config import load_analysis_config, load_request_profile
from shinchiku_land_searcher.excel_reader import read_property_records
from shinchiku_land_searcher.reports import write_advice_txt, write_analysis_outputs, write_request_plan
from shinchiku_land_searcher.request_assistant import run_browser_assist, unique_urls
from shinchiku_land_searcher.scoring import analyze_records

app = typer.Typer(help="Property document-request assistant and investment ranking CLI.")
console = Console()
InputArg = Annotated[Path, typer.Option("--input", "-i", help="Input xlsx file path.")]
OutputArg = Annotated[Path, typer.Option("--output-dir", "-o", help="Output directory.")]
ConfigArg = Annotated[Path | None, typer.Option("--config", "-c", help="Local YAML config.")]


@app.callback()
def main(version: Annotated[bool, typer.Option("--version", help="Show version.")] = False) -> None:
    if version:
        console.print(__version__)
        raise typer.Exit()


@app.command()
def analyze(
    input: InputArg,
    output_dir: OutputArg = Path("outputs"),
    config: ConfigArg = None,
    sheet: Annotated[str | None, typer.Option("--sheet", help="Worksheet name. Default: active sheet.")] = None,
    url_column: Annotated[str, typer.Option("--url-column", help="Column containing property URLs.")] = "A",
    header_row: Annotated[int, typer.Option("--header-row", help="Header row number.")] = 1,
    no_header: Annotated[bool, typer.Option("--no-header", help="Use Excel column letters as headers.")] = False,
    ai_provider: Annotated[str, typer.Option("--ai-provider", help="local/openai/anthropic.")] = "local",
) -> None:
    records = read_property_records(input, sheet_name=sheet, url_column=url_column, header_row=header_row, no_header=no_header, require_url=False)
    results = analyze_records(records, load_analysis_config(config))
    output_dir.mkdir(parents=True, exist_ok=True)
    write_analysis_outputs(results, output_dir)
    ai_comment = generate_ai_comment(results, ai_provider)
    write_advice_txt(results, output_dir / "advice.txt", extra_ai_comment=ai_comment)
    write_request_plan(records, output_dir)
    console.print(f"[green]Analysis completed:[/green] {len(results)} rows -> {output_dir}")


@app.command()
def request(
    input: InputArg,
    output_dir: OutputArg = Path("outputs"),
    config: ConfigArg = None,
    sheet: Annotated[str | None, typer.Option("--sheet", help="Worksheet name. Default: active sheet.")] = None,
    url_column: Annotated[str, typer.Option("--url-column", help="Column containing property URLs.")] = "A",
    header_row: Annotated[int, typer.Option("--header-row", help="Header row number.")] = 1,
    no_header: Annotated[bool, typer.Option("--no-header", help="Use Excel column letters as headers.")] = False,
    no_browser: Annotated[bool, typer.Option("--no-browser", help="Only create request_plan.csv.")] = False,
    limit: Annotated[int | None, typer.Option("--limit", help="Maximum number of URLs to process.")] = None,
    start_index: Annotated[int, typer.Option("--start-index", help="1-based URL index to start.")] = 1,
    headless: Annotated[bool, typer.Option("--headless", help="Run browser in headless mode.")] = False,
) -> None:
    records = read_property_records(input, sheet_name=sheet, url_column=url_column, header_row=header_row, no_header=no_header, require_url=True)
    plan_path = write_request_plan(records, output_dir)
    urls = unique_urls(records)
    console.print(f"[green]Request plan created:[/green] {plan_path} ({len(urls)} URLs)")
    if no_browser:
        return
    run_browser_assist(urls, profile=load_request_profile(config), output_dir=output_dir, limit=limit, start_index=start_index, headless=headless)


@app.command(name="run")
def run_all(
    input: InputArg,
    output_dir: OutputArg = Path("outputs"),
    config: ConfigArg = None,
    sheet: Annotated[str | None, typer.Option("--sheet", help="Worksheet name. Default: active sheet.")] = None,
    url_column: Annotated[str, typer.Option("--url-column", help="Column containing property URLs.")] = "A",
    header_row: Annotated[int, typer.Option("--header-row", help="Header row number.")] = 1,
    no_header: Annotated[bool, typer.Option("--no-header", help="Use Excel column letters as headers.")] = False,
    no_browser: Annotated[bool, typer.Option("--no-browser", help="Only create request_plan.csv.")] = True,
    ai_provider: Annotated[str, typer.Option("--ai-provider", help="local/openai/anthropic.")] = "local",
) -> None:
    analyze(input=input, output_dir=output_dir, config=config, sheet=sheet, url_column=url_column, header_row=header_row, no_header=no_header, ai_provider=ai_provider)
    request(input=input, output_dir=output_dir, config=config, sheet=sheet, url_column=url_column, header_row=header_row, no_header=no_header, no_browser=no_browser)


@app.command("sample-config")
def sample_config(output: Annotated[Path, typer.Option("--output", "-o")] = Path("config.local.yaml")) -> None:
    source = Path(__file__).resolve().parents[2] / "config.example.yaml"
    output.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    console.print(f"Created: {output}")


if __name__ == "__main__":
    app()
