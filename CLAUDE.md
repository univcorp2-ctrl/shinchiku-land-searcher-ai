# Claude instructions

あなたはこのrepoの開発補助AIです。目的は、ユーザーのExcel物件一覧を読み込み、投資検討順のアドバイスと資料請求準備をCLIで安全に実行できる状態に保つことです。

## 必ず守ること

1. 外部サイトへの最終送信を自動クリックしない。
2. CAPTCHA、ログイン、サイト制限を迂回しない。
3. APIキーなしでもローカル分析が動く状態を維持する。
4. 個人情報・APIキー・連絡先入り設定をrepoに含めない。
5. 変更後は `ruff check .` と `pytest` が通るようにする。

## 重要ファイル

- `src/shinchiku_land_searcher/cli.py`
- `src/shinchiku_land_searcher/scoring.py`
- `src/shinchiku_land_searcher/request_assistant.py`
- `docs/architecture.md`
- `docs/setup.md`

## ユーザー想定パス

```text
G:\マイドライブ\AI_Agents\github\repos\Shinchiku_Land_Searcher\final_output\Apartment_Investment_Master.xlsx
```

A列URLを標準にする。違う列の場合は `--url-column` を使う。
