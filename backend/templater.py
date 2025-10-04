import os, re
from jinja2 import Environment, FileSystemLoader, select_autoescape

TPL_DIR = os.getenv("TPL_DIR", os.path.join("frontend", "templates"))

env = Environment(
    loader=FileSystemLoader(TPL_DIR),
    autoescape=select_autoescape(["html"])
)

def slugify(s: str) -> str:
    """
    友善中文的 slug：
    - 空白 -> -
    - 僅保留 英數 / - / 常用中日韓統一表意文字 (U+4E00–U+9FFF)
    - 收斂多個連字號，去頭尾 -
    - 若仍為空字串，退回隨機短碼避免撞名
    """
    from uuid import uuid4
    s = s.strip()
    s = re.sub(r"\s+", "-", s)                       # 空白 -> -
    s = re.sub(r"[^0-9A-Za-z\u4E00-\u9FFF-]", "", s) # 保留英數/CJK/- 其餘移除
    s = re.sub(r"-{2,}", "-", s).strip("-")          # 收斂 ----
    s = s.lower()                                     # 英文字母轉小寫（不影響 CJK）
    return s if s else uuid4().hex[:8]

def render_report(template: str, ctx: dict) -> str:
    tpl = env.get_template(f"{template}.html")
    return tpl.render(**ctx)
