import csv
import os
import random
import json
from typing import List

from src.utils.erank import top_keywords_only


def load_top_terms(path: str) -> List[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [t for t, _ in data.get("top_terms", [])]
    except FileNotFoundError:
        return []


def main() -> None:
    # Create minimal dataset with title, price, url
    os.makedirs("data/processed", exist_ok=True)

    top_terms = load_top_terms("outputs/day07_top_terms.json")
    uni = [t for t in top_terms if " " not in t]
    erank = top_keywords_only("data/erank_keywords.csv", min_volume=0, limit=200)
    for k in erank:
        if " " not in k and k not in uni:
            uni.append(k)
    if not uni:
        uni = ["metal", "wall", "art", "decor", "custom", "gift", "poster"]

    out_path = "data/processed/day04_clean.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["title", "price", "url", "price_value"])
        w.writeheader()
        for i in range(60):
            n = random.randint(3, 6)
            chosen = random.sample(uni, min(n, len(uni)))
            title = (" ".join(chosen) + " Wall Art").title()
            price = round(random.uniform(29.0, 199.0), 2)
            url = f"https://example.com/demo-{i}"
            w.writerow({
                "title": title,
                "price": f"${price}",
                "url": url,
                "price_value": price,
            })
    print(f"Wrote demo dataset: {out_path}")


if __name__ == "__main__":
    main()


