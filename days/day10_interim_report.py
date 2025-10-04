import argparse
import json

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 10: Ara rapor (Day 05 + 07 + 09 özet)")
    parser.add_argument("--clean", default="data/processed/day04_clean.csv")
    parser.add_argument("--top_terms", default="outputs/day07_top_terms.json")
    parser.add_argument("--suggestions", default="outputs/day09_suggestions.txt")
    parser.add_argument("--out", default="outputs/day10_interim_report.md")
    args = parser.parse_args()

    df = pd.read_csv(args.clean)
    price_col = "price_value" if "price_value" in df.columns else "price"
    desc = df[price_col].describe(percentiles=[0.25, 0.5, 0.75])

    try:
        with open(args.top_terms, "r", encoding="utf-8") as f:
            top_terms = json.load(f).get("top_terms", [])
    except FileNotFoundError:
        top_terms = []

    try:
        with open(args.suggestions, "r", encoding="utf-8") as f:
            suggestions = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        suggestions = []

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("# Day 10: Ara Rapor\n\n")
        f.write("## Fiyat Özeti\n\n")
        f.write(desc.to_markdown())
        f.write("\n\n## TF-IDF En Önemli Kelimeler\n\n")
        if top_terms:
            f.write("| Kelime | Skor |\n|---|---|\n")
            for w, s in top_terms[:50]:
                f.write(f"| {w} | {s:.4f} |\n")
        else:
            f.write("(Veri bulunamadı)\n")
        f.write("\n\n## Başlık Önerileri\n\n")
        if suggestions:
            for s in suggestions[:10]:
                f.write(f"- {s}\n")
        else:
            f.write("(Öneri bulunamadı)\n")

    print(f"Saved interim report to {args.out}")


if __name__ == "__main__":
    main()

