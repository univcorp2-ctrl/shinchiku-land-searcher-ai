from __future__ import annotations

import os

from shinchiku_land_searcher.models import ScoreResult


def generate_ai_comment(results: list[ScoreResult], provider: str = "local") -> str:
    provider = provider.lower().strip()
    if provider == "local":
        return _local_comment(results)
    if provider == "openai":
        return _openai_comment(results)
    if provider in {"anthropic", "claude"}:
        return _anthropic_comment(results)
    raise ValueError(f"Unsupported AI provider: {provider}")


def _local_comment(results: list[ScoreResult]) -> str:
    if not results:
        return "分析対象がありません。"
    lines = ["ローカル分析では、収益性・駅距離・築年数・注意キーワードの総合点で判断しています。"]
    lines.append("最初に確認する順番は次の通りです。")
    for result in results[:5]:
        lines.append(f"- {result.rank}位: {result.title}（{result.score:.1f}点）")
    lines.append("資料取得後は、賃貸借契約、レントロール、修繕履歴、管理費・修繕積立金、土地権利、融資条件を必ず確認してください。")
    return "\n".join(lines)


def _prompt(results: list[ScoreResult]) -> str:
    rows = []
    for result in results[:20]:
        rows.append({
            "rank": result.rank,
            "title": result.title,
            "score": result.score,
            "price_man_yen": result.price_man_yen,
            "gross_yield_percent": result.gross_yield_percent,
            "walking_minutes": result.walking_minutes,
            "building_age_years": result.building_age_years,
            "recommendation": result.recommendation,
            "risks": result.risks,
        })
    return (
        "あなたは不動産投資の一次スクリーニング担当です。"
        "次のランキングを見て、どの順番で資料請求・詳細確認すべきか、"
        "注意点と次アクションを日本語で簡潔に助言してください。"
        f"\nデータ: {rows}"
    )


def _openai_comment(results: list[ScoreResult]) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "OPENAI_API_KEY が未設定のため、ローカルコメントを使用します。\n" + _local_comment(results)
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            messages=[{"role": "user", "content": _prompt(results)}],
            temperature=0.2,
        )
        return response.choices[0].message.content or _local_comment(results)
    except Exception as exc:  # pragma: no cover
        return f"OpenAIコメント生成に失敗したため、ローカルコメントを使用します: {exc}\n" + _local_comment(results)


def _anthropic_comment(results: list[ScoreResult]) -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return "ANTHROPIC_API_KEY が未設定のため、ローカルコメントを使用します。\n" + _local_comment(results)
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest"),
            max_tokens=1200,
            temperature=0.2,
            messages=[{"role": "user", "content": _prompt(results)}],
        )
        return "\n".join(block.text for block in message.content if hasattr(block, "text"))
    except Exception as exc:  # pragma: no cover
        return f"Anthropicコメント生成に失敗したため、ローカルコメントを使用します: {exc}\n" + _local_comment(results)
