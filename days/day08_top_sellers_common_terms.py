import argparse
from collections import Counter

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 08: En çok satan/tıklanan ortak kelimeler")
    parser.add_argument("--input", required=True, help="Ön işlenmiş CSV (Day 06)")
    parser.add_argument("--top_n", type=int, default=50, help="Listelenecek kelime sayısı")
    parser.add_argument("--sales_col", default="sales", help="Satış/tıklama sütun adı (varsa)")
    parser.add_argument("--threshold", type=float, default=None, help="Üst eşik (örn. satış >= eşik)")
    parser.add_argument("--out", default="outputs/day08_common_terms.md", help="Rapor çıktısı")
    parser.add_argument("--ptype", default=None, help="Kategori filtresi (poster, canvas, vb.)")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    has_sales = args.sales_col in df.columns and df[args.sales_col].notna().any()
    subset = df
    if has_sales and args.threshold is not None:
        subset = df[df[args.sales_col] >= args.threshold]
    if args.ptype and "ptype" in df.columns:
        subset = subset[subset["ptype"] == args.ptype]

    tokens = []
    if "title_clean" in subset.columns:
        tokens += " ".join(subset["title_clean"].fillna("").astype(str)).split()
    if "description_clean" in subset.columns:
        tokens += " ".join(subset["description_clean"].fillna("").astype(str)).split()

    freq = Counter(tokens)
    common = freq.most_common(args.top_n)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("# Day 08: Ortak Kelimeler\n\n")
        if has_sales and args.threshold is not None:
            f.write(f"Filtre: {args.sales_col} >= {args.threshold} (satır={len(subset)})\n\n")
        else:
            f.write(f"Filtre: Yok (satır={len(subset)})\n\n")
        f.write("| Kelime | Frekans |\n|---|---|\n")
        for w, c in common:
            f.write(f"| {w} | {c} |\n")

    print(f"Saved report to {args.out}")


if __name__ == "__main__":
    main()

