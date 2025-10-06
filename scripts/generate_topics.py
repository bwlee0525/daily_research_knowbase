import os, json, sys, datetime
from typing import List

def fallback_topics(today: str) -> List[str]:
    base = [
        "Direct Liquid Cooling supply risk map",
        "Multi-output regression reliability in industrial prediction",
        "Data lakehouse architecture trends",
        "QuietPower Index benchmarking method",
        "FFT-based steady-state sound classification",
        "Thermal-Reliability co-design patterns",
        "Spec-Driven Development in MLOps pipelines",
        "Fan curve auto-generation sanity checks",
        "Edge AI for acoustic anomaly detection",
        "Power/Noise efficiency frontier mapping"
    ]
    return [f"{today} · {t}" for t in base]

def main():
    today = datetime.date.today().isoformat()
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        print(json.dumps(fallback_topics(today), ensure_ascii=False))
        return 0

    try:
        import google.generativeai as genai
    except Exception:
        import subprocess, sys as _sys
        subprocess.check_call([_sys.executable, "-m", "pip", "install", "google-generativeai==0.8.3"])
        import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model="gemini-1.5-flash",
        generation_config={"temperature": 0.7, "max_output_tokens": 512, "top_p": 0.9, "top_k": 40}
    )
    prompt = f"""
You are a research editor generating concise daily tech/business research topics for an engineer-manager in thermal, acoustics, and ML systems.
Date: {today}.
Requirements:
- Return exactly 10 short, actionable topics (8-12 words each), no numbering.
- Focus mix: (1) thermal/DLC, (2) acoustics/audio ML, (3) MLOps/SDD, (4) data architecture/lakehouse, (5) HW-SW co-design/product ops.
- Avoid hype, avoid vague titles. Each must be specific and researchable.
- Output: JSON array of strings (no commentary).
"""
    try:
        rsp = model.generate_content(prompt)
        text = rsp.text.strip()
        topics = json.loads(text)
        assert isinstance(topics, list) and len(topics) == 10
        topics = [str(x) for x in topics]
        print(json.dumps(topics, ensure_ascii=False))
    except Exception:
        print(json.dumps(fallback_topics(today), ensure_ascii=False))
    return 0

if __name__ == "__main__":
    sys.exit(main())
