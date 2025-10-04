from backend.app import create_report, rebuild_archive
from backend.models import ReportRequest
from datetime import datetime

# 今日要產生的主題（先用示範，之後可換成你自己的清單/資料來源）
TOPICS = [
    ("我的第一份 SDD 報告", ["demo", "sdd"]),
    ("中文標題驗證", ["check"]),
    ("研究流程自動化", ["automation"])
]

def main():
    for topic, tags in TOPICS:
        req = ReportRequest(
            topic=topic,
            tags=tags,
            template="report_v1_sections",
            data={
                "subtitle": f"自動產生於 {datetime.utcnow().strftime('%Y-%m-%d')}",
                "sections": [
                    {"heading": "目標", "body": "每天自動產出報告並更新索引。"},
                    {"heading": "狀態", "body": "本地腳本驗證成功後，改由 GitHub Actions 排程。"}
                ]
            }
        )
        print(create_report(req))
    print(rebuild_archive())

if __name__ == "__main__":
    main()
