# SDD（Spec-Driven Development）— Spec Freeze v2025-10-05r2

> **SSOT**：本文件為本專案單一事實來源。任何流程/行為改動，先改此規格，再改程式與工作流。

## 1) 目標與時序（台北時間）
- **08:30** Suggest：產生 10 題、建立 GitHub Issue 供選題。
- **08:30–08:59** 使用者在該 Issue 評論 `/pick 2,7`（或 `/pick 2 7`）選兩題。
- **09:00** Publish：讀取選題 → 呼叫 **Gemini** 研究 → 生成 2 篇報告（Jinja 模板）→ 更新首頁 → **Smoke** 驗證。
- **排程策略**：GitHub Actions 採「每小時喚醒 + 台北時間守門」，只在 08 與 09 點真正執行。

## 2) 非功能（NFR）
- 準時性：允許平台隊列延遲，但 **09:15 前**需可見新內容。
- 可靠性：LLM 失敗/超時 → 回退預設段落，不阻斷部署。
- 可稽核：prompt 指紋、token 用量、原始回覆、引用，落檔於 `bundle.zip/research.json`。
- 成本：每日題數 2；每題 `max_tokens=2048`、`timeout<=45s`；超限即回退。
- 時區：**Asia/Taipei**（ID / 頁面 / 索引 / 驗證）。

## 3) 介面與契約
### 3.1 Suggest（輸出到 GitHub Issue）
- Title：`[Suggest] <YYYY-MM-DD> 今日 10 題`
- Label：`daily-suggest`
- Body 必含可解析 JSON 區塊（置於 fenced block）：
```json
{ "date":"YYYY-MM-DD",
  "items":[ {"no":1,"title":"…","tags":["…"]}, {"no":2,"title":"…","tags":["…"]},
            {"no":3,"title":"…","tags":["…"]}, {"no":4,"title":"…","tags":["…"]},
            {"no":5,"title":"…","tags":["…"]}, {"no":6,"title":"…","tags":["…"]},
            {"no":7,"title":"…","tags":["…"]}, {"no":8,"title":"…","tags":["…"]},
            {"no":9,"title":"…","tags":["…"]}, {"no":10,"title":"…","tags":["…"]} ]
}

使用者選題評論格式：/pick 2,7（或空白分隔；僅取前兩個有效數字；重複自動去重）。

3.2 Publish（輸入來源優先序）

當日 daily-suggest Issue 的最新 /pick 評論

Fallback：config/topics.json 的前兩題

3.3 Research（Gemini）輸入/輸出（強契約）

輸入（每題）：{title: string, tags: string[], date: YYYY-MM-DD(TPE)}

輸出（落檔 bundle.zip/research.json）：

{
  "subtitle": "string",
  "sections": [{"heading":"string","body":"string"}],
  "citations": [{"title":"string","url":"https://…"}],
  "trace": {
    "model":"gemini-1.5-pro",
    "prompt_hash":"sha256:…",
    "token_usage":{"input":0,"output":0},
    "started_at":"ISO8601Z","finished_at":"ISO8601Z","status":"ok|timeout|quota|error"
  }
}


預設門檻：MAX_TOKENS_PER_TOPIC=2048、REQUEST_TIMEOUT_SEC=45、RETRIES=0、REQUIRE_CITATIONS=false

回退：任一題 status!=ok → 該題使用安全預設段落（流程不中斷）。

3.4 報告/索引（既有）

報告 ID：<slug(title)>-<YYYYMMDD_TPE>（slug 允許 CJK、合併連字號）。

產物三件組：index.html、meta.json（含 created_at_local/utc）、bundle.zip（含 research.json）。

首頁索引：依 created_at_local DESC；右側日期徽章 YYYY-MM-DD；頁尾 Generated: 為 TPE。

4) CI/CD 與排程

Workflows：

suggest.yml（08:30）：每小時喚醒 + 台北時間守門；生成 10 題 Issue（含機器可解析 JSON 區塊）。

publish.yml（09:00）：每小時喚醒 + 守門；流程為 tests → build → deploy → smoke。

Smoke：部署後以 curl 抓首頁，檢查是否包含今天 TPE 日期；失敗重試 ≤3 次，仍失敗自動開 Issue。

5) 測試（DoD）

單元：slugify（CJK/空白/邊界）、TPE 日期入 ID。

契約：create_report 生成三件組；meta.json 同時含 local/utc；research.json 符合 3.3 的 schema（失敗可為 status!=ok）。

整合：scripts.daily 能讀 topics；suggest.yml/publish.yml 能解析 Issue JSON 與 /pick。

排程驗收：Actions 顯示 Next run；08:30 有 Suggest Issue；09:00 首頁新增 2 篇；Smoke 綠勾。

6) 安全 / 治理 / 配置

Secrets：GEMINI_API_KEY（Repo Secret；嚴禁入版控）。

Labels：daily-suggest, daily-picked（系統可自動加在選題 Issue）。

Repo Variables（可選）：MAX_TOKENS_PER_TOPIC、REQUEST_TIMEOUT_SEC、REQUIRE_CITATIONS

權限（可選）：若需白名單，限制允許的使用者才接受 /pick。

7) 回滾與不可變性

發布：主分支 main 推送、08:30 Suggest、09:00 Publish。

回滾：回到上一個綠勾 commit；或重新部署上一版 artifact。

同日重跑：覆蓋同日 ID，不新增重複。

（本文件置於 specs/SDD.md；任何行為改動必須同步更新本文件）
