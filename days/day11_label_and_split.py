import argparse

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 11: Basit etiket oluşturma ve kayıt")
    parser.add_argument("--input", required=True, help="Temiz/ön işlenmiş CSV")
    parser.add_argument("--sales_col", default="sales", help="Satış/tıklama sütunu (varsa)")
    parser.add_argument("--label_col", default="label_high_sales", help="Çıktı etiket sütunu")
    parser.add_argument("--out", default="data/processed/day11_labeled.csv")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    if args.sales_col in df.columns and df[args.sales_col].notna().any():
        thr = df[args.sales_col].median()
        df[args.label_col] = (df[args.sales_col] >= thr).astype(int)
    else:
        # veri yoksa: fiyatın medyan altı=1 gibi basit bir kural (örnek)
        price_col = "price_value" if "price_value" in df.columns else "price"
        thr = df[price_col].median()
        df[args.label_col] = (df[price_col] <= thr).astype(int)

    df.to_csv(args.out, index=False)
    print(f"Saved labeled data to {args.out} (label_col={args.label_col})")


if __name__ == "__main__":
    main()

