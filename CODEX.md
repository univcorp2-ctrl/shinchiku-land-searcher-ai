# CODEX instructions

このrepoは、Excelの物件一覧から投資優先順位を出し、A列URLの資料請求を人間確認付きで支援するCLIです。

## 開発方針

- Python 3.11+
- CLIはTyper
- Excel処理はopenpyxl
- 出力はCSV / XLSX / TXT
- 外部AIは任意。APIキーがない場合は必ずローカル分析で動くこと
- 資料請求の最終送信は自動クリックしないこと
- CAPTCHA、ログイン、利用規約上の制限を迂回しないこと

## 主要コマンド

```bash
pip install -e ".[dev,browser,ai]"
ruff check .
pytest
python scripts/create_sample_workbook.py
python -m shinchiku_land_searcher analyze --input sample_data/sample_properties.xlsx --output-dir outputs
python -m shinchiku_land_searcher request --input sample_data/sample_properties.xlsx --output-dir outputs --no-browser
```

## 改修時の注意

- スコアリング変更時は `tests/test_scoring.py` を更新
- Excel列の推定ロジック変更時は `tests/test_excel_reader.py` を更新
- ブラウザ自動化はサイトごとのばらつきが大きいため、失敗してもログとスクリーンショットを残す
- 個人情報を含む `config.local.yaml` はコミットしない
