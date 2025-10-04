import os, re, io, zipfile, json
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from datetime import datetime
from .models import ReportRequest, ReportMeta
from .templater import render_report, slugify
from .gcs_io import write_text, write_json, write_bytes, list_reports, read_json

load_dotenv()
app = FastAPI(title="Research Pipeline API")

ARCHIVE_INDEX = os.getenv("ARCHIVE_INDEX", "index.html")

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

    date = datetime.utcnow().strftime("%Y%m%d")
    report_id = f"{slugify(req.topic)}-{date}"

    meta = ReportMeta(report_id=report_id, title=req.topic, tags=req.tags)

    ctx = dict(req.data or {})
    ctx.update({
        "title": req.topic,
        "created_at": meta.created_at.strftime("%Y-%m-%d"),
        "tags": req.tags,
    })

    html = render_report(req.template, ctx)

    base = f"reports/{report_id}"
    write_text(f"{base}/index.html", html)
    write_json(f"{base}/meta.json", meta.model_dump(mode="json"))

    mem = io.BytesIO()
    with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("index.html", html)
        z.writestr(
            "meta.json",
            json.dumps(meta.model_dump(mode="json"), ensure_ascii=False, indent=2).encode("utf-8"),
        )
    write_bytes(f"{base}/bundle.zip", mem.getvalue())

    rebuild_archive()
    return {"report_id": report_id, "view": f"{base}/index.html"}

@app.post("/rebuild-archive")
def rebuild_archive():
    # 讀取所有 meta.json → 用其中的 title/created_at，避免 slug 失真
    meta_paths = [p for p in list_reports("reports/") if p.endswith("meta.json")]
    records = []
    for p in meta_paths:
        try:
            m = read_json(p)
            rid = m.get("report_id") or _extract_report_id(p)
            title = m.get("title") or rid.rsplit("-", 1)[0].replace("-", " ")
            created_at = m.get("created_at", "")
            records.append({"rid": rid, "title": title, "created_at": created_at})
        except Exception:
            rid = _extract_report_id(p)
            title = rid.rsplit("-", 1)[0].replace("-", " ")
            records.append({"rid": rid, "title": title, "created_at": ""})

    # 以 created_at 由新到舊排序（ISO 字串可直接比較）
    records.sort(key=lambda r: r["created_at"], reverse=True)

    items = []
    for r in records:
        date_badge = f' <span style="opacity:.6">{r["created_at"][:10]}</span>' if r["created_at"] else ""
        items.append(f'<li><a href="reports/{r["rid"]}/index.html">{r["title"]}</a>{date_badge}</li>')

    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>研究檔案庫</title></head>
<body><h1>研究檔案庫</h1><ul>{''.join(items)}</ul>
<p>Generated: {datetime.utcnow().isoformat()}</p></body></html>"""
    write_text(ARCHIVE_INDEX, html)
    return {"count": len(records), "index": ARCHIVE_INDEX}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8080)
