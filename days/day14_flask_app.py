import json
import os
import random

import joblib
from flask import Flask, render_template_string, request
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer

from src.utils.erank import top_keywords_only

HTML = """
<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Etsy Ürün Oluşturma</title>
  <style>
    :root { --bg:#0f172a; --card:#111827; --text:#e5e7eb; --muted:#94a3b8; --primary:#22c55e; --border:#1f2937; }
    *{ box-sizing:border-box }
    body { font-family: -apple-system, system-ui, Segoe UI, Roboto, sans-serif; margin:0; background:var(--bg); color:var(--text); }
    .container { max-width:980px; padding:24px; margin:0 auto; }
    .header { display:flex; align-items:center; justify-content:space-between; gap:16px; margin-bottom:16px; }
    .title { font-size:20px; font-weight:700; }
    .muted { color:var(--muted); font-size:14px; }
    .grid { display:grid; grid-template-columns: 1fr; gap:16px; }
    @media(min-width:900px){ .grid{ grid-template-columns: 380px 1fr; } }
    label { display:block; margin:8px 0 6px; font-weight:600; font-size:14px; }
    input, textarea, select { width:100%; padding:10px 12px; border-radius:10px; border:1px solid var(--border); background:#0b1220; color:var(--text); outline:none; }
    input::placeholder, textarea::placeholder { color:#64748b }
    textarea { resize: vertical; min-height:120px; }
    .btn { display:inline-flex; align-items:center; gap:8px; padding:10px 14px; border-radius:10px; border:1px solid #16a34a; background:var(--primary); color:#03281a; font-weight:700; cursor:pointer; }
    .btn:disabled{ opacity:.6; cursor:not-allowed }
    .card { border:1px solid var(--border); background:var(--card); padding:16px; border-radius:14px; }
    .row { display:flex; align-items:center; gap:8px; }
    .copy { border:1px solid var(--border); background:#0b1220; color:var(--text); padding:6px 10px; border-radius:8px; cursor:pointer; }
    .hint { font-size:12px; color:var(--muted); margin-top:4px; }
    .toast { position:fixed; right:16px; bottom:16px; background:#1e293b; color:#e2e8f0; padding:10px 14px; border-radius:10px; border:1px solid var(--border); opacity:0; transform:translateY(8px); transition:all .2s ease; }
    .toast.show { opacity:1; transform:translateY(0); }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div>
        <div class="title">Etsy Ürün Oluşturma</div>
        <div class="muted">Başlık ve tür gir; sistem Title / Description / Tags üretsin.</div>
      </div>
    </div>

    <div class="grid">
      <form method="post" class="card" id="genForm" onsubmit="return startGen()">
        <div>
          <label>Başlık</label>
          <input name="title" placeholder="Örn: Metal Tree of Life Wall Art" required />
          <div class="hint">Özgün anahtar kelimeleri eklemen önerilir.</div>
        </div>

        <div style="margin-top:12px">
          <label>Tür (kategori)</label>
          <select name="ptype" required>
            <option value="metal_wall_art">Metal Wall Art</option>
            <option value="poster">Poster</option>
            <option value="jewelry">Jewelry</option>
            <option value="bag">Bag</option>
            <option value="canvas">Canvas</option>
            <option value="mug">Mug</option>
            <option value="tshirt">T‑Shirt</option>
            <option value="sticker">Sticker</option>
          </select>
        </div>

        <div style="margin-top:16px">
          <button class="btn" type="submit">
            <span id="spinner" style="display:none">⏳</span>
            Önerileri Oluştur
          </button>
        </div>
      </form>

      {% if generated %}
      <div class="card">
        <div class="row">
          <div style="font-weight:700">Title</div>
          <button class="copy" type="button" onclick="copyText('titleField')">Kopyala</button>
        </div>
        <input id="titleField" value="{{ best_title }}" />

        <div class="row" style="margin-top:12px">
          <div style="font-weight:700">Description</div>
          <button class="copy" type="button" onclick="copyText('descField')">Kopyala</button>
        </div>
        <textarea id="descField" rows="8" placeholder="Ürün açıklaması">{{ description_suggestion }}</textarea>

        <div class="row" style="margin-top:12px">
          <div style="font-weight:700">Tags</div>
          <button class="copy" type="button" onclick="copyText('tagsField')">Kopyala</button>
        </div>
        <input id="tagsField" value="{{ ", ".join(tag_suggestions) }}" />

        {% if title_suggestions %}
          <div class="hint" style="margin-top:10px">Diğer başlık seçenekleri: {{ "; ".join(title_suggestions) }}</div>
        {% endif %}
      </div>
      {% endif %}
    </div>

    <div id="toast" class="toast">Kopyalandı</div>
  </div>

  <script>
    function startGen(){
      const btn = document.querySelector('.btn');
      const sp = document.getElementById('spinner');
      if(btn && sp){ btn.disabled = true; sp.style.display = 'inline-block'; }
      return true;
    }
    function showToast(msg){
      const t = document.getElementById('toast');
      if(!t) return;
      t.textContent = msg || 'Kopyalandı';
      t.classList.add('show');
      setTimeout(()=> t.classList.remove('show'), 1200);
    }
    function copyText(id){
      const el = document.getElementById(id);
      if(!el) return;
      const val = el.value || el.innerText || '';
      navigator.clipboard && navigator.clipboard.writeText(val).then(()=>showToast('Kopyalandı'));
    }
  </script>
</body>
</html>
"""


def load_artifacts():
    clf = joblib.load("models/day12_logreg.joblib")
    vec: TfidfVectorizer = joblib.load("models/day12_vectorizer.joblib")
    try:
        with open("outputs/day09_suggestions.txt", "r", encoding="utf-8") as f:
            suggestions = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        suggestions = []
    # load top terms for tags/title generation
    top_terms = []
    try:
        with open("outputs/day07_top_terms.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            top_terms = [t for t, _ in data.get("top_terms", [])]
    except FileNotFoundError:
        pass
    return clf, vec, suggestions, top_terms


def load_median_price(default_value: float = 0.0) -> float:
    try:
        import pandas as pd
        df = pd.read_csv("data/processed/day04_clean.csv")
        col = "price_value" if "price_value" in df.columns else "price"
        med = float(df[col].dropna().median())
        if med != med:  # NaN check
            return default_value
        return med
    except Exception:
        return default_value


app = Flask(__name__)
clf, vec, suggestions_pool, top_terms = load_artifacts()


def build_title_suggestions(k: int = 5, length: int = 6, ptype: str = "metal_wall_art"):
    pool = [t for t in top_terms if " " not in t]
    if not pool:
        pool = ["modern", "metal", "wall", "art", "decor", "custom", "gift"]
    # Prefer including a category token at the end (e.g., "Wall Art", "Poster")
    cat_word = {
        "metal_wall_art": "Wall Art",
        "poster": "Poster",
        "jewelry": "Jewelry",
        "bag": "Bag",
        "canvas": "Canvas",
        "mug": "Mug",
        "tshirt": "T-Shirt",
        "sticker": "Sticker",
    }.get(ptype, "Art")

    out = []
    for _ in range(k):
        n = max(3, min(7, length))
        chosen = random.sample(pool, min(n, len(pool)))
        phrase = (" ".join(chosen) + f" {cat_word}").title()
        out.append(phrase)
    return out


def build_tag_suggestions(limit: int = 13, ptype: str = "metal_wall_art"):
    # Build pool of short tokens
    uni = [t.strip().lower() for t in top_terms if " " not in t]
    # Enrichment via eRank CSV if present
    erank_path = "data/erank_keywords.csv"
    try:
        erank_terms = top_keywords_only(erank_path, min_volume=100, limit=150)
    except Exception:
        erank_terms = []
    for kw in erank_terms:
        k = kw.strip().lower()
        if " " not in k and k not in uni:
            uni.append(k)

    base_by_type = {
        "metal_wall_art": ["metal", "wall", "art", "decor", "custom", "gift", "modern", "home", "minimal"],
        "poster": ["poster", "print", "wall", "art", "decor", "digital", "download", "gift"],
        "jewelry": ["jewelry", "necklace", "ring", "gift", "handmade", "women"],
        "bag": ["bag", "tote", "leather", "gift", "handmade", "travel"],
        "canvas": ["canvas", "wall", "art", "decor", "print"],
        "mug": ["coffee", "mug", "gift", "kitchen"],
        "tshirt": ["tshirt", "tee", "graphic", "gift"],
        "sticker": ["sticker", "vinyl", "laptop", "waterproof"],
    }
    for t in base_by_type.get(ptype, []):
        if t not in uni:
            uni.append(t)

    # Compose multi-word tags (at least 2 words), max 13 letters (excluding spaces)
    def ok(tag: str) -> bool:
        letters = len(tag.replace(" ", ""))
        return (" " in tag) and (letters <= 13)

    tags: list[str] = []
    # Try bigrams of short tokens
    for a in uni:
        if len(tags) >= limit:
            break
        for b in uni:
            if a == b:
                continue
            candidate = f"{a} {b}"
            if ok(candidate) and candidate not in tags:
                tags.append(candidate)
                if len(tags) >= limit:
                    break

    # Fallback: trim longer tokens with a short connector
    if len(tags) < limit:
        for a in uni:
            candidate = f"{a} art"
            if ok(candidate) and candidate not in tags:
                tags.append(candidate)
            if len(tags) >= limit:
                break

    return tags[:limit]


def build_description_suggestion(title: str, price: float, tags: list, ptype: str):
    core = ", ".join(tags[:6])
    # Base description without any price info
    desc = (
        f"Discover our {title.strip()} {ptype.replace('_',' ')} — crafted with high-quality materials for a timeless look. "
        f"Perfect for living rooms, offices, and gift occasions. "
        f"Style highlights: {core}. Handmade with care. "
        f"Each piece is checked for quality and carefully packaged to arrive safely. "
        f"Choose the size that fits your space and elevate your decor."
    )
    # Ensure minimum length of 200 characters
    filler = (
        " Designed to be timeless and versatile, it blends with modern and minimalist interiors, "
        "making it a thoughtful gift for loved ones."
    )
    while len(desc) < 200:
        desc += filler
    return desc[: max(200, len(desc))]


def enforce_title_limit(s: str, limit: int = 140) -> str:
    if len(s) <= limit:
        return s
    # Cut at last space before limit when possible
    cut = s[:limit]
    if " " in cut:
        cut = cut[: cut.rfind(" ")]
    return cut.strip()


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    title_suggestions = []
    tag_suggestions = []
    description_suggestion = ""
    best_title = ""
    generated = False
    if request.method == "POST":
        title = request.form.get("title", "")
        ptype = request.form.get("ptype", "metal_wall_art")
        # Fiyat kullanıcıdan istenmiyor; veri seti medyanını kullan
        price = load_median_price(default_value=0.0)
        X_text = vec.transform([title])
        X = hstack([X_text, csr_matrix([[price]])])
        pred = clf.predict(X)[0]
        result = int(pred)
        title_suggestions = build_title_suggestions(k=5, length=6, ptype=ptype)
        tag_suggestions = build_tag_suggestions(limit=13, ptype=ptype)
        # If user-provided title has fewer than 2 words, prefer generated
        user_words = len([w for w in (title or "").split() if w.strip()])
        candidate = (title_suggestions[0] if (user_words < 2 and title_suggestions) else (title or title_suggestions[0]))
        best_title = enforce_title_limit(candidate or "Metal Wall Art", limit=140)
        description_suggestion = build_description_suggestion(title=best_title, price=price, tags=tag_suggestions, ptype=ptype)
        generated = True
    return render_template_string(
        HTML,
        result=result,
        title_suggestions=title_suggestions,
        tag_suggestions=tag_suggestions,
        description_suggestion=description_suggestion,
        best_title=best_title,
        generated=generated,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)

