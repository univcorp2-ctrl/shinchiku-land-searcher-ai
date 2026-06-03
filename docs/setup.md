# Setup Guide

## 1. Pythonを用意

Python 3.11以上を使います。

```bash
python --version
```

## 2. インストール

```bash
git clone https://github.com/<OWNER>/shinchiku-land-searcher-ai.git
cd shinchiku-land-searcher-ai
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[browser,ai]"
python -m playwright install chromium
```

## 3. 設定ファイル

```bash
cp config.example.yaml config.local.yaml
```

`config.local.yaml` に資料請求用の連絡先を入れます。このファイルは `.gitignore` 済みです。

## 4. Excel分析

```bash
python -m shinchiku_land_searcher analyze \
  --input "G:\マイドライブ\AI_Agents\github\repos\Shinchiku_Land_Searcher\final_output\Apartment_Investment_Master.xlsx" \
  --url-column A \
  --output-dir outputs
```

## 5. 資料請求準備

一覧だけ作る場合:

```bash
python -m shinchiku_land_searcher request \
  --input "G:\マイドライブ\AI_Agents\github\repos\Shinchiku_Land_Searcher\final_output\Apartment_Investment_Master.xlsx" \
  --output-dir outputs \
  --no-browser
```

ブラウザ補助を使う場合:

```bash
python -m shinchiku_land_searcher request \
  --input "G:\マイドライブ\AI_Agents\github\repos\Shinchiku_Land_Searcher\final_output\Apartment_Investment_Master.xlsx" \
  --output-dir outputs \
  --config config.local.yaml \
  --limit 10
```

## 6. 出力確認

`outputs/` 以下を確認します。

- `advice.txt`: 最初に検討する順番
- `ranking.xlsx`: 詳細スコア
- `request_plan.csv`: 資料請求対象URL
- `request_log.csv`: ブラウザ補助ログ

## トラブルシュート

### Excelの1行目がヘッダーではない

```bash
python -m shinchiku_land_searcher analyze --input file.xlsx --no-header
```

### URLがA列ではない

```bash
python -m shinchiku_land_searcher analyze --input file.xlsx --url-column C
```

### Playwrightがない

```bash
pip install -e ".[browser]"
python -m playwright install chromium
```

### AI APIキーなしで使いたい

何も設定せず `--ai-provider local` を使います。これが標準です。
