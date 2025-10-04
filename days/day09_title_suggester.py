import argparse
import json
import random


def load_top_terms(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # list[(term, score)]
    return [t for t, s in data.get("top_terms", [])]


def suggest_titles(terms, k=5, length=6):
    suggestions = []
    pool = [t for t in terms if " " not in t]  # use unigrams primarily
    for _ in range(k):
        chosen = random.sample(pool, min(length, len(pool)))
        title = " ".join(chosen).title()
        suggestions.append(title)
    return suggestions


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 09: Basit başlık öneri sistemi")
    parser.add_argument("--top_terms", required=True, help="Day 07 top terms JSON")
    parser.add_argument("--out", default="outputs/day09_suggestions.txt", help="Öneriler çıktısı")
    parser.add_argument("--k", type=int, default=10, help="Öneri sayısı")
    parser.add_argument("--length", type=int, default=6, help="Başlıktaki kelime sayısı")
    args = parser.parse_args()

    terms = load_top_terms(args.top_terms)
    suggestions = suggest_titles(terms, k=args.k, length=args.length)

    with open(args.out, "w", encoding="utf-8") as f:
        for s in suggestions:
            f.write(s + "\n")

    print(f"Saved {len(suggestions)} suggestions to {args.out}")


if __name__ == "__main__":
    main()

