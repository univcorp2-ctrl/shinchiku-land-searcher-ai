from __future__ import annotations

import csv
import time
from pathlib import Path
from typing import Iterable

from rich.console import Console

from shinchiku_land_searcher.excel_reader import is_probable_url
from shinchiku_land_searcher.models import PropertyRecord, RequestProfile

console = Console()

REQUEST_TEXTS = [
    "資料請求",
    "資料を請求",
    "資料を取り寄せ",
    "お問い合わせ",
    "問合せ",
    "問い合わせ",
    "Request",
    "Contact",
]

FIELD_PATTERNS = {
    "name": ["name", "氏名", "お名前", "姓名", "full_name"],
    "email": ["email", "mail", "メール", "e-mail"],
    "phone": ["tel", "phone", "電話", "携帯"],
    "postal_code": ["postal", "zip", "郵便", "postcode"],
    "address": ["address", "住所", "所在地"],
    "message": ["message", "body", "comment", "内容", "備考", "お問い合わせ内容"],
}


def unique_urls(records: Iterable[PropertyRecord]) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()
    for record in records:
        if is_probable_url(record.url) and record.url not in seen:
            urls.append(record.url)
            seen.add(record.url)
    return urls


def write_request_log_header(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        csv.DictWriter(f, fieldnames=["url", "status", "memo"]).writeheader()


def append_request_log(path: Path, url: str, status: str, memo: str) -> None:
    with path.open("a", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["url", "status", "memo"])
        writer.writerow({"url": url, "status": status, "memo": memo})


def run_browser_assist(
    urls: list[str],
    *,
    profile: RequestProfile,
    output_dir: Path,
    headless: bool = False,
    limit: int | None = None,
    start_index: int = 1,
    delay_seconds: float = 2.0,
) -> None:
    """Open request pages and assist filling. It never clicks final submit."""

    try:
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover - depends on optional extra
        raise RuntimeError(
            "Playwright is not installed. Run: pip install -e '.[browser]' && python -m playwright install chromium"
        ) from exc

    selected = urls[start_index - 1 :]
    if limit:
        selected = selected[:limit]

    log_path = output_dir / "request_log.csv"
    write_request_log_header(log_path)
    screenshot_dir = output_dir / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(locale="ja-JP")
        page = context.new_page()
        for i, url in enumerate(selected, start=start_index):
            console.rule(f"{i}: {url}")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=45000)
                time.sleep(delay_seconds)
                clicked = click_request_entry(page)
                time.sleep(delay_seconds)
                filled = fill_profile_fields(page, profile)
                screenshot_path = screenshot_dir / f"request_{i:03}.png"
                page.screenshot(path=str(screenshot_path), full_page=True)
                memo = f"entry_clicked={clicked}; filled={filled}; screenshot={screenshot_path.name}"
                append_request_log(log_path, url, "prepared", memo)
                console.print(
                    "[yellow]送信直前で停止しています。画面を確認し、必要なら手動で送信してください。[/yellow]"
                )
                input("確認後にEnterで次のURLへ進みます。スキップした場合もEnter。")
            except PlaywrightTimeoutError as exc:
                append_request_log(log_path, url, "timeout", str(exc))
                console.print(f"[red]Timeout:[/red] {exc}")
            except Exception as exc:  # pragma: no cover - browser runtime variability
                append_request_log(log_path, url, "error", str(exc))
                console.print(f"[red]Error:[/red] {exc}")
        context.close()
        browser.close()


def click_request_entry(page: object) -> bool:
    for text in REQUEST_TEXTS:
        try:
            locator = page.get_by_text(text, exact=False).first
            if locator.count() > 0:
                locator.click(timeout=3000)
                return True
        except Exception:
            continue
    return False


def fill_profile_fields(page: object, profile: RequestProfile) -> int:
    values = {
        "name": profile.name,
        "email": profile.email,
        "phone": profile.phone,
        "postal_code": profile.postal_code,
        "address": profile.address,
        "message": profile.message,
    }
    count = 0
    for field_name, value in values.items():
        if not value:
            continue
        if fill_first_matching_input(page, FIELD_PATTERNS[field_name], value):
            count += 1
    return count


def fill_first_matching_input(page: object, patterns: list[str], value: str) -> bool:
    selectors = ["input", "textarea"]
    for selector in selectors:
        try:
            elements = page.locator(selector)
            total = elements.count()
            for i in range(total):
                element = elements.nth(i)
                attrs = " ".join(
                    str(element.get_attribute(attr) or "")
                    for attr in ["name", "id", "placeholder", "aria-label", "autocomplete"]
                ).lower()
                if any(pattern.lower() in attrs for pattern in patterns):
                    current = element.input_value(timeout=1000) if selector == "input" else ""
                    if not current:
                        element.fill(value, timeout=3000)
                        return True
        except Exception:
            continue
    return False
