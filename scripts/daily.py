import json, os
from datetime import datetime
from backend.app import create_report, rebuild_archive
from backend.models import ReportRequest

CONFIG = os.getenv("TOPICS_JSON", "config/topics.json")

def load_topics(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            items = json.load(f)
            assert isinstance(items, list)
            return [(it["topic"], it.get("tags", [])) for it in items]
    except Exception:
        # fallback：避免排程失敗
        return [("每日報告", ["fallback"])]

def main():
    for topic, tags in load_topics(CONFIG):
        req = ReportRequest(
            topic=topic,
            tags=tags,
            template="report_v1_sections",
            data={
                "subtitle": f"自動產生於 {datetime.utcnow().strftime('%Y-%m-%d')}",
                "sections": [
                    {"heading": "目標", "body": "每天自動產出報告並更新索引。"},
                    {"heading": "狀態", "body": "Actions 排程執行。"}
                ]
            }
        )
        print(create_report(req))
    print(rebuild_archive())

if __name__ == "__main__":
    main()
