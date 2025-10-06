import argparse, os, sys, time, pathlib
from datetime import datetime, timedelta

IGNORE_DIRS = {"assets", "css", "js", "img", "images", "static"}
KEEP_ALWAYS = {"index.html", "404.html", "sitemap.xml", "robots.txt"}

def _is_html(p: pathlib.Path) -> bool:
    return p.is_file() and p.suffix.lower() == ".html" and p.name not in KEEP_ALWAYS

def collect_html(root: pathlib.Path):
    for p in root.rglob("*.html"):
        if any(part in IGNORE_DIRS for part in p.parts):
            continue
        if p.name in KEEP_ALWAYS:
            continue
        yield p

def by_mtime(p: pathlib.Path):
    try:
        return p.stat().st_mtime
    except FileNotFoundError:
        return 0.0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="out", help="site output root (default: out)")
    ap.add_argument("--max", dest="max_keep", type=int, default=None, help="keep latest N html pages")
    ap.add_argument("--days", dest="days_keep", type=int, default=None, help="keep pages newer than DAYS")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = pathlib.Path(args.root).resolve()
    if not root.exists():
        print(f"[retention] root not found: {root}", file=sys.stderr)
        return 0

    pages = sorted(list(collect_html(root)), key=by_mtime, reverse=True)

    to_keep = set()
    now = time.time()

    if args.days_keep:
        cutoff = now - args.days_keep * 86400
        for p in pages:
            if by_mtime(p) >= cutoff:
                to_keep.add(p)

    if args.max_keep:
        for p in pages[:args.max_keep]:
            to_keep.add(p)

    if not args.days_keep and not args.max_keep:
        print("[retention] no policy specified; nothing to do.", file=sys.stderr)
        return 0

    to_delete = [p for p in pages if p not in to_keep]
    print(f"[retention] pages={len(pages)} keep={len(to_keep)} delete={len(to_delete)}")

    for p in to_delete:
        rel = p.relative_to(root)
        if args.dry_run:
            print(f"DRY-RUN delete: {rel}")
        else:
            try:
                p.unlink()
                parent = p.parent
                while parent != root and not any(parent.iterdir()):
                    parent.rmdir()
                    parent = parent.parent
                print(f"deleted: {rel}")
            except Exception as e:
                print(f"failed delete {rel}: {e}", file=sys.stderr)
    return 0

if __name__ == "__main__":
    sys.exit(main())
