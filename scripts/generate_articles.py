import json
import os
import textwrap
import uuid
from datetime import datetime, timezone
import requests

CATEGORIES = [
    ("gold", "Gold / Commodities"),
    ("bitcoin", "Bitcoin"),
    ("ethereum", "Ethereum"),
    ("altcoins", "Altcoins / DeFi"),
    ("forex", "Forex"),
    ("strategies", "Strategies"),
    ("indicators", "Indicators"),
    ("airdrops", "Airdrops"),
]

POSTS_DIR = os.path.join(os.path.dirname(__file__), "..", "posts")
INDEX_JSON = os.path.join(POSTS_DIR, "index.json")

API_KEY = os.environ.get("KIMI_API_KEY") or os.environ.get("AI_API_KEY")
API_BASE = os.environ.get("KIMI_API_BASE", "https://api.moonshot.cn/v1")
MODEL = os.environ.get("KIMI_MODEL", "moonshot-v1-8k")


def ensure_dirs():
    os.makedirs(POSTS_DIR, exist_ok=True)


def load_index():
    if not os.path.exists(INDEX_JSON):
        return []
    with open(INDEX_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def save_index(data):
    with open(INDEX_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def call_kimi(prompt):
    if not API_KEY:
        raise RuntimeError("Missing KIMI_API_KEY (or AI_API_KEY) in secrets.")
    url = f"{API_BASE}/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8,
        "max_tokens": 1200,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def build_prompt(category_label):
    return textwrap.dedent(
        f"""
        Write a 700-900 word English article for SEO about {category_label}.
        Requirements:
        - Unique, non-repetitive, human-readable.
        - Include a short intro, 3-5 H2/H3 subheadings, bullet lists where helpful.
        - Add one actionable checklist and one risk section.
        - Avoid external links; keep it self-contained.
        - Tone: analytical but concise.
        """
    ).strip()


def render_post_html(title, category_label, body_html):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    body{{margin:0;font-family:"Segoe UI","Inter",system-ui,-apple-system,sans-serif;background:#060a12;color:#e8eef7;line-height:1.7;padding:28px;}}
    .page{{max-width:880px;margin:0 auto;}}
    p{{color:#c2cee4;}}
    h1{{margin:0 0 12px;}}
    h2,h3{{color:#e8eef7;}}
    .tag{{display:inline-block;padding:4px 10px;border-radius:999px;border:1px solid rgba(255,255,255,0.12);color:#9ab7d6;font-size:13px;}}
    a{{color:#35c3ff;text-decoration:none;}}
    .ad-inline{{margin:24px 0;padding:12px;border:1px dashed rgba(255,255,255,0.25);border-radius:12px;color:#9ab7d6;text-align:center;}}
  </style>
</head>
<body>
  <div class="page">
    <a href="../">← Back to home</a>
    <p class="tag">{category_label}</p>
    <h1>{title}</h1>
    <div class="ad-inline">Ad slot — insert tag</div>
    {body_html}
    <div class="ad-inline">Ad slot — insert tag</div>
  </div>
</body>
</html>"""


def generate_article(cat_slug, cat_label):
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y%m%d%H%M")
    uid = uuid.uuid4().hex[:8]
    prompt = build_prompt(cat_label)
    content = call_kimi(prompt)
    # Simple safe replacements for markdown headings to HTML
    lines = []
    for line in content.splitlines():
        if line.startswith("### "):
            lines.append(f"<h3>{line[4:].strip()}</h3>")
        elif line.startswith("## "):
            lines.append(f"<h2>{line[3:].strip()}</h2>")
        elif line.startswith("- "):
            lines.append(f"<li>{line[2:].strip()}</li>")
        else:
            if line.strip() == "":
                lines.append("<p></p>")
            else:
                lines.append(f"<p>{line.strip()}</p>")
    body_html = "\n".join(lines)
    title = f"{cat_label} Insights {now.strftime('%Y-%m-%d %H:%M UTC')}"
    html = render_post_html(title, cat_label, body_html)
    filename = f"{ts}-{cat_slug}-{uid}.html"
    path = os.path.join(POSTS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return {
        "title": title,
        "category": cat_slug,
        "category_label": cat_label,
        "slug": filename,
        "created_at": now.isoformat(),
    }


def main():
    ensure_dirs()
    index = load_index()
    for slug, label in CATEGORIES:
        meta = generate_article(slug, label)
        index.append(meta)
    # keep newest first
    index.sort(key=lambda x: x["created_at"], reverse=True)
    save_index(index)


if __name__ == "__main__":
    main()
