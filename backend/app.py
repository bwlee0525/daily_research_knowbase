import os, re, io, zipfile, json
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from datetime import datetime
from zoneinfo import ZoneInfo
from .models import ReportRequest, ReportMeta
from .templater import render_report, slugify
from .gcs_io import write_text, write_json, write_bytes, list_reports, read_json

load_dotenv()
app = FastAPI(title="Research Pipeline API")

ARCHIVE_INDEX = os.getenv("ARCHIVE_INDEX", "index.html")
TPE = ZoneInfo("Asia/Taipei")

def _now_tpe() -> datetime:
    return datetime.now(TPE)

def _extract_report_id(path: str) -> str:
    parts = re.split(r"[\\/]+", path)
    if "reports" in parts:
        i = parts.index("reports")
        if i + 1 < len(parts):
            return parts[i + 1]
    return "unknown"

@app.post("/reports")
def create_report(req: ReportRequest):
    if not req.topic or len(req.topic) < 3:
        raise HTTPException(status_code=422, detail="topic too short")

    now = _now_tpe()
    date = now.strftime("%Y%m%d")                     # ← ID 用台北日曆
    report_id = f"{slugify(req.topic)}-{date}"

    meta = ReportMeta(report_id=report_id, title=req.topic, tags=req.tags)

    # 模板上下文：用台北日期
    ctx = dict(req.data or {})
    ctx.update({
        "title": req.topic,
        "created_at": now.strftime("%Y-%m-%d"),
        "tags": req.tags,
    })

    html = render_report(req.template, ctx)

    base = f"reports/{report_id}"
    write_text(f"{base}/index.html", html)

    # meta.json：同時保存 UTC 與台北時間（索引用 local）
    meta_json = meta.model_dump(mode="json")
    meta_json["created_at_utc"] = meta_json.pop("created_at")     # 原本是 UTC
    meta_json["created_at_local"] = now.isoformat()               # 台北 ISO

    write_json(f"{base}/meta.json", meta_json)

    # bundle.zip 也寫入相同 meta
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("index.html", html)
        z.writestr("meta.json", json.dumps(meta_json, ensure_ascii=False, indent=2).encode("utf-8"))
    write_bytes(f"{base}/bundle.zip", mem.getvalue())

    rebuild_archive()
    return {"report_id": report_id, "view": f"{base}/index.html"}

@app.post("/rebuild-archive")
def rebuild_archive():
    # 讀每篇 meta.json → 以 created_at_local 顯示與排序，fallback 用 created_at_utc
    meta_paths = [p for p in list_reports("reports/") if p.endswith("meta.json")]
    records = []
    for p in meta_paths:
        try:
            m = read_json(p)
            rid = m.get("report_id") or _extract_report_id(p)
            title = m.get("title") or rid.rsplit("-", 1)[0].replace("-", " ")
            created = m.get("created_at_local") or m.get("created_at_utc") or ""
            records.append({"rid": rid, "title": title, "created": created})
        except Exception:
            rid = _extract_report_id(p)
            title = rid.rsplit("-", 1)[0].replace("-", " ")
            records.append({"rid": rid, "title": title, "created": ""})

    records.sort(key=lambda r: r["created"], reverse=True)  # ISO 字串可直接排序

    items = []
    for r in records:
        date_badge = f' <span style="opacity:.6">{r["created"][:10]}</span>' if r["created"] else ""
        items.append(f'<li><a href="reports/{r["rid"]}/index.html">{r["title"]}</a>{date_badge}</li>')

    now = _now_tpe().isoformat()
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>研究檔案庫</title></head>
<body><h1>研究檔案庫</h1><ul>{''.join(items)}</ul>
<p>Generated: {now}</p></body></html>"""
    write_text(ARCHIVE_INDEX, html)
    return {"count": len(records), "index": ARCHIVE_INDEX}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8080)
