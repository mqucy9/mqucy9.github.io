import json
import os
from collections import defaultdict
import re

ROOT = os.path.dirname(os.path.dirname(__file__))
POSTS_DIR = os.path.join(ROOT, "posts")
INDEX_JSON = os.path.join(POSTS_DIR, "index.json")
INDEX_HTML = os.path.join(ROOT, "index.html")

CATEGORIES = [
    ("gold", "Gold"),
    ("bitcoin", "Bitcoin"),
    ("ethereum", "Ethereum"),
    ("altcoins", "Altcoins"),
    ("forex", "Forex"),
    ("strategies", "Strategies"),
    ("indicators", "Indicators"),
    ("airdrops", "Airdrops"),
]

SITE_NAME = "Quantum Market Pulse"
SITE_DESC = (
    "Quantum Market Pulse delivers 5-hour refreshed insights on gold, bitcoin, "
    "ethereum, altcoins, forex, strategies, indicators, and airdrops with clean "
    "on-site articles optimized for SEO."
)
SITE_KEYWORDS = (
    "gold forecast, bitcoin analysis, ethereum staking, altcoin research, forex strategy, "
    "trading indicators, airdrop guide, market insights, crypto news, commodities outlook"
)
HERO_LINE = (
    "AI-assisted, editor-polished briefs refreshed every 5 hours across gold, crypto, "
    "forex, strategies, indicators, and airdrops—structured for fast reading and strong SEO."
)


def load_index():
    if not os.path.exists(INDEX_JSON):
        return []
    with open(INDEX_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def rebuild_index_from_files():
    items = []
    tag_to_slug = {
        "Gold": "gold",
        "Gold / Commodities": "gold",
        "Bitcoin": "bitcoin",
        "Ethereum": "ethereum",
        "Altcoins / DeFi": "altcoins",
        "Altcoins": "altcoins",
        "Forex": "forex",
        "Strategies": "strategies",
        "Indicators": "indicators",
        "Airdrops": "airdrops",
    }
    for fname in os.listdir(POSTS_DIR):
        if not fname.endswith(".html"):
            continue
        fpath = os.path.join(POSTS_DIR, fname)
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            data = f.read()
        title = re.search(r"<h1>(.*?)</h1>", data, re.S)
        tag = re.search(r'<p class="tag">(.*?)</p>', data, re.S)
        hero = re.search(r"hero-img\" style=\"background-image:url\('([^']+)'", data)
        created = os.path.getmtime(fpath)
        created_iso = f"{created}"
        title = title.group(1).strip() if title else fname
        label = tag.group(1).strip() if tag else "Misc"
        slug = fname
        category = tag_to_slug.get(label, "misc")
        img = hero.group(1) if hero else "https://source.unsplash.com/featured/900x600/?market"
        items.append(
            {
                "title": title,
                "category": category,
                "category_label": label,
                "slug": slug,
                "created_at": created_iso,
                "image": img,
            }
        )
    # newest first
    items = sorted(items, key=lambda x: x["created_at"], reverse=True)
    return items


def chunk_cards(items):
    cards = []
    for meta in items:
        img = meta.get("image") or "https://images.unsplash.com/photo-1508387020794-1c76e43a90d1?auto=format&fit=crop&w=900&q=80"
        cards.append(
            f"""
        <div class="card">
          <div class="img-thumb" style="background-image:url('{img}');"></div>
          <h3>{meta['title']}</h3>
          <p>Fresh insight published {meta['created_at'][:16].replace('T',' ')}.</p>
          <a href="posts/{meta['slug']}">Read article</a>
        </div>
            """
        )
    return "\n".join(cards)


def build_body(grouped):
    sections = []
    for slug, label in CATEGORIES:
        cards = chunk_cards(grouped.get(slug, []))
        sections.append(
            f"""
    <section id="{slug}">
      <div class="section-title"><span>{label}</span></div>
      <div class="grid">
        {cards}
      </div>
    </section>
            """
        )
    return "\n".join(sections)


def render_page(sections_html):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="1d7555627c6e58b3d3aaaf4b622bd79b7fd13167" content="1d7555627c6e58b3d3aaaf4b622bd79b7fd13167">
  <title>{SITE_NAME}</title>
  <meta name="description" content="{SITE_DESC}">
  <meta name="keywords" content="{SITE_KEYWORDS}">
  <style>
    :root {{
      --bg: #060a12;
      --panel: #0d1524;
      --border: rgba(255,255,255,0.07);
      --text: #e8eef7;
      --muted: #9aabc7;
      --accent: #35c3ff;
      --radius: 14px;
      --shadow: 0 18px 50px rgba(0,0,0,0.35);
      --glass: rgba(255,255,255,0.03);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI","Inter",system-ui,-apple-system,sans-serif;
      background: radial-gradient(circle at 20% 20%, #122347 0, #060a12 42%), #060a12;
      color: var(--text);
      line-height: 1.7;
      padding: 28px;
    }}
    .page {{ max-width: 1220px; margin: 0 auto; }}
    header.hero {{
      padding: 32px;
      border-radius: var(--radius);
      background: linear-gradient(120deg, rgba(53,195,255,0.10), rgba(255,218,106,0.09));
      border: 1px solid var(--border);
      box-shadow: var(--shadow);
    }}
    .hero h1 {{ margin: 0 0 12px; font-size: 32px; letter-spacing: -0.4px; }}
    .hero p {{ margin: 0; color: var(--muted); }}
    nav.chips {{ margin-top: 18px; display: flex; flex-wrap: wrap; gap: 10px; }}
    nav.chips a {{
      padding: 7px 14px;
      border-radius: 999px;
      border: 1px solid var(--border);
      background: var(--glass);
      color: var(--muted);
      font-size: 13px;
      text-decoration: none;
    }}
    nav.chips a:hover {{ color: var(--text); border-color: rgba(255,255,255,0.2); }}
    .section-title {{
      margin: 26px 0 12px;
      font-weight: 700;
      letter-spacing: 0.2px;
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .section-title span {{
      padding: 6px 10px;
      border-radius: 10px;
      background: var(--glass);
      border: 1px solid var(--border);
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
      gap: 18px;
    }}
    .card {{
      background: var(--panel);
      border-radius: var(--radius);
      border: 1px solid var(--border);
      padding: 14px;
      box-shadow: var(--shadow);
      display: flex;
      flex-direction: column;
      gap: 10px;
      min-height: 260px;
    }}
    .card .img-thumb {{
      width: 100%;
      height: 140px;
      border-radius: 10px;
      background-size: cover;
      background-position: center;
      border: 1px solid var(--border);
    }}
    .card h3 {{ margin: 0; font-size: 17px; line-height: 1.4; }}
    .card p {{ margin: 0; color: var(--muted); font-size: 14px; }}
    .card a {{
      margin-top: auto;
      color: var(--accent);
      text-decoration: none;
      font-weight: 600;
      font-size: 14px;
    }}
    .card a:hover {{ text-decoration: underline; }}
    .ads-placeholder {{
      margin: 30px 0;
      padding: 16px;
      border: 1px dashed rgba(255,255,255,0.25);
      border-radius: var(--radius);
      color: var(--muted);
      background: var(--glass);
      text-align: center;
    }}
    .sticky-ad {{
      position: fixed;
      top: 140px;
      width: 160px;
      padding: 10px;
      background: var(--panel);
      border: 1px dashed rgba(255,255,255,0.25);
      color: var(--muted);
      border-radius: 10px;
      text-align: center;
      box-shadow: var(--shadow);
      z-index: 50;
    }}
    .sticky-ad.left {{ left: 12px; }}
    .sticky-ad.right {{ right: 12px; }}
    .bottom-ad {{
      position: fixed;
      bottom: 12px;
      left: 50%;
      transform: translateX(-50%);
      width: min(760px, 92vw);
      padding: 12px;
      background: var(--panel);
      border: 1px dashed rgba(255,255,255,0.25);
      border-radius: 12px;
      text-align: center;
      box-shadow: var(--shadow);
      z-index: 60;
    }}
    footer {{
      margin: 40px 0 10px;
      color: var(--muted);
      font-size: 13px;
      text-align: center;
    }}
    @media (max-width: 640px) {{
      body {{ padding: 18px; }}
      .hero h1 {{ font-size: 26px; }}
      .sticky-ad {{ display: none; }}
      .bottom-ad {{ width: 100%; left: 0; transform: none; border-radius: 0; }}
    }}
  </style>
</head>
<body>
  <div class="sticky-ad left">Side Ad (160x600)<br>Paste tag</div>
  <div class="sticky-ad right">Side Ad (160x600)<br>Paste tag</div>
  <div class="bottom-ad">Bottom Ad Slot — add your script/tag</div>

  <div class="page">
    <header class="hero">
      <h1>{SITE_NAME}</h1>
      <p>{HERO_LINE}</p>
      <nav class="chips">
        <a href="#gold">Gold</a>
        <a href="#bitcoin">Bitcoin</a>
        <a href="#ethereum">Ethereum</a>
        <a href="#altcoins">Altcoins</a>
        <a href="#forex">Forex</a>
        <a href="#strategies">Strategies</a>
        <a href="#indicators">Indicators</a>
        <a href="#airdrops">Airdrops</a>
      </nav>
    </header>

    <div class="ads-placeholder">Ad slot reserved (top). Add your tag when ready.</div>

    {sections_html}

    <div class="ads-placeholder">Ad slot reserved (mid page). Paste your ad tag here when ready.</div>

    <footer>Built for fast loads and clean SEO. All content is first-party and kept on this domain.</footer>
  </div>
</body>
</html>"""


def main():
    index = load_index()
    if not index:
        index = rebuild_index_from_files()
    grouped = defaultdict(list)
    for item in index:
        grouped[item["category"]].append(item)
    # keep top 6 per category
    for k in grouped:
        grouped[k] = sorted(grouped[k], key=lambda x: x["created_at"], reverse=True)[:6]
    sections = build_body(grouped)
    html = render_page(sections)
    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
