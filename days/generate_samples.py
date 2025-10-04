import argparse
import csv
import json
import random
from typing import List

from src.utils.erank import top_keywords_only


def enforce_title_limit(s: str, limit: int = 140) -> str:
    if len(s) <= limit:
        return s
    cut = s[:limit]
    if " " in cut:
        cut = cut[: cut.rfind(" ")]
    return cut.strip()


def build_tag_suggestions(top_terms: List[str], erank_path: str, limit: int = 13, ptype: str = "poster") -> List[str]:
    uni = [t.strip().lower() for t in top_terms if " " not in t]
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

    def ok(tag: str) -> bool:
        letters = len(tag.replace(" ", ""))
        return (" " in tag) and (letters <= 13)

    tags: List[str] = []
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
    if len(tags) < limit:
        for a in uni:
            candidate = f"{a} art"
            if ok(candidate) and candidate not in tags:
                tags.append(candidate)
            if len(tags) >= limit:
                break
    return tags[:limit]


def build_description(title: str, tags: List[str], ptype: str) -> str:
    core = ", ".join(tags[:6])
    desc = (
        f"Discover our {title.strip()} {ptype.replace('_',' ')} — crafted with high-quality materials for a timeless look. "
        f"Perfect for living rooms, offices, and gift occasions. "
        f"Style highlights: {core}. Handmade with care. "
        f"Each piece is checked for quality and carefully packaged to arrive safely. "
        f"Choose the size that fits your space and elevate your decor."
    )
    filler = (
        " Designed to be timeless and versatile, it blends with modern and minimalist interiors, "
        "making it a thoughtful gift for loved ones."
    )
    while len(desc) < 200:
        desc += filler
    return desc


def load_top_terms(path: str) -> List[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [t for t, _ in data.get("top_terms", [])]
    except FileNotFoundError:
        return ["modern", "metal", "wall", "art", "decor", "custom", "gift"]


def main() -> None:
    p = argparse.ArgumentParser(description="Generate example listings based on TF-IDF and eRank")
    p.add_argument("--top_terms", default="outputs/day07_top_terms.json")
    p.add_argument("--erank_csv", default="data/erank_keywords.csv")
    p.add_argument("--ptype", default="poster")
    p.add_argument("--count", type=int, default=10)
    p.add_argument("--out", default="outputs/samples/examples.csv")
    args = p.parse_args()

    top_terms = load_top_terms(args.top_terms)
    uni = [t for t in top_terms if " " not in t]

    rows = []
    for _ in range(args.count):
        chosen = random.sample(uni, min(6, len(uni)))
        raw_title = " ".join(chosen).title()
        title = enforce_title_limit(raw_title, limit=140)
        tags = build_tag_suggestions(top_terms, args.erank_csv, limit=13, ptype=args.ptype)
        description = build_description(title, tags, args.ptype)
        rows.append({"title": title, "description": description, "tags": ", ".join(tags)})

    # write csv
    import os
    os.makedirs("outputs/samples", exist_ok=True)
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["title", "description", "tags"])
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print(f"Saved {len(rows)} examples to {args.out}")


if __name__ == "__main__":
    main()


