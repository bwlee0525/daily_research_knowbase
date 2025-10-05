📄 規格（SSOT）：[specs/SDD.md](specs/SDD.md)

# Research Pipeline (SDD Starter)

這是一個**初學者友善**的 SDD 範例專案：按「規格 → 設計 → 實作 → 驗證」交付。
你可以先在本機產生一份報告與索引，再視需要部署到 Cloud Run + GCS。

## 快速開始（本機）
1. 安裝 Python 3.11、VS Code（建議 Dev Containers + Docker）。
2. 在專案根目錄執行：
   ```bash
   pip install -r backend/requirements.txt
   python -m backend.app   # 啟動 API 於 http://127.0.0.1:8080
   ```
   或開發模式：`uvicorn backend.app:app --reload`
3. 產生一份範例報告（不需 GCS）：
   ```bash
   LOCAL_OUT=out python - <<'PY'
from backend.app import create_report
from backend.models import ReportRequest
print(create_report(ReportRequest(topic="hello SDD", tags=["demo"])))
PY
   ```
   產物會在 `out/reports/...`；用瀏覽器打開 `out/reports/<id>/index.html`。

## 規格檔
- `product_spec.yaml`、`api_spec.yaml`、`report_spec.yaml`、`ops_spec.yaml`

## 部署（概要）
- 建置：`docker build -t research-pipeline:dev -f backend/Dockerfile .`
- Cloud Run 部署與 GCS 設定請依你環境填入 `GCS_BUCKET` 等參數。

> 模板檔：`frontend/templates/report_v1.html` 來源於你提供的報告 HTML，已加入 `{{ title }}` 與 `{{ created_at }}` 兩個變數。
