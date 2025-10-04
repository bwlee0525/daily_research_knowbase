import os, json, io, zipfile
from google.cloud import storage

BUCKET = os.getenv("GCS_BUCKET", "")
LOCAL_OUT = os.getenv("LOCAL_OUT", "out")

def _client():
    return storage.Client() if BUCKET else None

def _ensure_local_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def write_text(path: str, content: str, content_type: str = "text/html"):
    if BUCKET:
        b = _client().bucket(BUCKET); b.blob(path).upload_from_string(content, content_type=content_type)
    else:
        full = os.path.join(LOCAL_OUT, path); _ensure_local_dir(full)
        with open(full, "w", encoding="utf-8") as f: f.write(content)

def write_json(path: str, obj: dict):
    data = json.dumps(obj, ensure_ascii=False, indent=2)
    write_text(path, data, "application/json")

def write_bytes(path: str, data: bytes, content_type: str = "application/zip"):
    if BUCKET:
        b = _client().bucket(BUCKET); b.blob(path).upload_from_string(data, content_type=content_type)
    else:
        full = os.path.join(LOCAL_OUT, path); _ensure_local_dir(full)
        with open(full, "wb") as f: f.write(data)

def list_reports(prefix="reports/"):
    if BUCKET:
        b = _client().bucket(BUCKET)
        return [blob.name for blob in b.list_blobs(prefix=prefix)]
    else:
        base = os.path.join(LOCAL_OUT, prefix)
        acc = []
        for root, _, files in os.walk(base):
            for fn in files:
                acc.append(os.path.relpath(os.path.join(root, fn), LOCAL_OUT))
        return acc

# ← 新增：讀回 meta.json 的幫手
def read_json(path: str) -> dict:
    if BUCKET:
        b = _client().bucket(BUCKET)
        data = b.blob(path).download_as_bytes()
        return json.loads(data.decode("utf-8"))
    else:
        full = os.path.join(LOCAL_OUT, path)
        with open(full, "r", encoding="utf-8") as f:
            return json.load(f)
