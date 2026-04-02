import os
import re
import html
import requests
import feedparser
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import google.generativeai as genai

ROOT = Path(__file__).resolve().parent.parent.parent
OUT = ROOT / "index.html"

META_TOKEN = '1d7555627c6e58b3d3aaaf4b622bd79b7fd13167'
AD_INJECT_URL = "https://frivolous-priest.com/bb3.Vb0nPT3VpQvMbWm/VdJ_Z/DQ0b2wOvTxI/xrO/DxMx3/LJTjYz5/MqjpEi4dN/D/ED"

TOPICS = [
    ("Gold / Commodities", ["gold price forecast", "xauusd", "gold hedge"]),
    ("Bitcoin", ["bitcoin etf", "btc funding rate", "bitcoin price"]),
    ("Ethereum", ["ethereum staking", "rollup gas fee", "eth price"]),
    ("Altcoins / DeFi", ["altcoin season", "defi narrative", "airdrop crypto"]),
    ("Forex", ["dxy index", "carry trade", "forex market"]),
    ("Strategies", ["trading strategy risk management", "position sizing"]),
    ("Indicators", ["trading indicators momentum volatility breadth"]),
    ("Airdrops", ["crypto airdrop", "testnet airdrop eligibility"]),
]


def gnews_feed(query: str) -> str:
    return f"https://news.google.com/rss/search?q={requests.utils.quote(query)}+when:7d&hl=en-US&gl=US&ceid=US:en"


def fetch_items(queries: List[str], max_items: int = 5) -> List[Dict]:
    items = []
    for q in queries:
        url = gnews_feed(q)
        try:
            parsed = feedparser.parse(url)
            for entry in parsed.entries[:max_items]:
                title = html.unescape(entry.title)
                summary = html.unescape(getattr(entry, "summary", ""))[:400]
                link = entry.link
                image = None
                if hasattr(entry, "media_content") and entry.media_content:
                    image = entry.media_content[0].get("url")
                items.append({"title": title, "summary": summary, "link": link, "image": image})
        except Exception as e:
            print("feed error", q, e)
    return items[:max_items]


def rewrite(text: str, api_key: str) -> str:
    if not api_key or not text.strip():
        return text
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"Rewrite concisely in English, keep key facts, 2-3 sentences: {text}"
        resp = model.generate_content(prompt, generation_config={"temperature": 0.3})
        if resp.text:
            return resp.text.strip()
    except Exception as e:
        print("rewrite failed", e)
    return text


def render(topic, cards_html):
    slug = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")
    return f"""
    <section id="{slug}">
      <div class="section-title"><span>{topic}</span></div>
      <div class="grid">
        {cards_html}
      </div>
    </section>
    """


def render_card(item):
    img = item.get("image") or "https://images.unsplash.com/photo-1508387020794-1c76e43a90d1?auto=format&fit=crop&w=900&q=80"
    return f"""
      <div class="card">
        <div class="img-thumb" style="background-image:url('{img}');"></div>
        <h3>{html.escape(item['title'])}</h3>
        <p>{html.escape(item.get('summary',''))}</p>
        <div class="links"><ul><li><a href="{item.get('link','#')}" target="_blank" rel="noopener">Read source</a></li></ul></div>
      </div>
    """


def build_html(sections_html: str):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="{META_TOKEN}" content="{META_TOKEN}">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Market Intelligence Hub</title>
  <script src="{AD_INJECT_URL}"></script>
  <style>
    :root {{
      --bg: #050913;
      --card: #0c1424;
      --accent: #19b4ff;
      --accent2: #f9c23c;
      --muted: #a9b7d0;
      --text: #e8edf7;
      --radius: 14px;
      --shadow: 0 18px 50px rgba(0,0,0,0.35);
      --glass: rgba(255,255,255,0.03);
      --grid-gap: 18px;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: radial-gradient(circle at 20% 20%, #0f1c38 0, #050913 42%), #050913;
      color: var(--text);
      font-family: "Segoe UI","Inter",system-ui,-apple-system,sans-serif;
      line-height: 1.7;
      padding: 24px;
    }}
    .page {{ max-width: 1200px; margin: 0 auto; }}
    header.hero {{
      padding: 32px;
      border-radius: var(--radius);
      background: linear-gradient(120deg, rgba(25,180,255,0.08), rgba(249,194,60,0.08));
      border: 1px solid rgba(255,255,255,0.06);
      box-shadow: var(--shadow);
    }}
    .hero h1 {{ margin: 0 0 12px; font-size: 32px; letter-spacing: -0.5px; }}
    .hero p {{ margin: 0; color: var(--muted); }}
    .chips {{ margin-top: 18px; display: flex; flex-wrap: wrap; gap: 8px; }}
    .chip {{
      padding: 6px 12px; border-radius: 999px; border: 1px solid rgba(255,255,255,0.08);
      background: var(--glass); color: var(--muted); font-size: 13px;
    }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: var(--grid-gap); }}
    .card {{
      background: var(--card); border-radius: var(--radius); padding: 16px;
      border: 1px solid rgba(255,255,255,0.06); box-shadow: var(--shadow);
    }}
    .card h3 {{ margin: 0 0 8px; font-size: 18px; }}
    .card p {{ margin: 0 0 10px; color: var(--muted); font-size: 14px; }}
    .links ul {{ padding-left: 18px; margin: 0; }}
    .links li {{ margin: 4px 0; }}
    .img-thumb {{
      width: 100%; height: 140px; border-radius: 10px; background-size: cover; background-position: center;
      margin-bottom: 12px; border: 1px solid rgba(255,255,255,0.05);
    }}
    .section-title {{ margin: 28px 0 12px; font-weight: 700; letter-spacing: 0.2px; }}
    .ads {{
      margin-top: 20px; padding: 14px; border-radius: var(--radius);
      border: 1px dashed rgba(255,255,255,0.25); background: rgba(255,255,255,0.03); color: var(--muted);
      text-align: center;
    }}
    a {{ color: var(--accent); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <!-- AADS sticky popup -->
  <script src="https://pl29040349.profitablecpmratenetwork.com/97/1f/d0/971fd0b7989a08decf43933949b5884f.js"></script>
  <div class="page">
    <header class="hero">
      <h1>Market Intelligence Hub</h1>
      <p>Auto-updated multi-asset intel: gold, BTC/ETH, altcoins, FX, strategies, indicators, airdrops.</p>
      <div class="chips">
        <a class="chip" href="#gold-commodities">Gold</a>
        <a class="chip" href="#bitcoin">Bitcoin</a>
        <a class="chip" href="#ethereum">Ethereum</a>
        <a class="chip" href="#altcoins-defi">Altcoins</a>
        <a class="chip" href="#forex">Forex</a>
        <a class="chip" href="#strategies">Strategies</a>
        <a class="chip" href="#indicators">Indicators</a>
        <a class="chip" href="#airdrops">Airdrops</a>
      </div>
    </header>

    {sections_html}

    <section>
      <div class="section-title"><span>Ad Slots</span></div>
      <div class="ads">Top sticky (AADS 2432692) loaded; mid-content ad appears within each article; footer reserved.</div>
    </section>
  </div>
</body>
</html>"""


def main():
    api_key = os.environ.get("AI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    sections = []
    for topic, queries in TOPICS:
        items = fetch_items(queries, max_items=4)
        cards = []
        for it in items:
            rewritten = rewrite(f"{it['title']}. {it.get('summary','')}", api_key)
            it["summary"] = rewritten
            cards.append(render_card(it))
        sections.append(render(topic, "".join(cards)))
    html_out = build_html("\n".join(sections))
    OUT.write_text(html_out, encoding="utf-8")
    print("Generated", OUT)


if __name__ == "__main__":
    main()
