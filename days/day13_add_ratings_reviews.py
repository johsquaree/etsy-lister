import argparse

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 13: Rating ve review sayısını özelliklere ekleme")
    parser.add_argument("--input", required=True, help="Etiketli CSV (Day 11)")
    parser.add_argument("--ratings_col", default="rating", help="Puan sütunu (varsa)")
    parser.add_argument("--reviews_col", default="reviews", help="Yorum sayısı sütunu (varsa)")
    parser.add_argument("--out", default="data/processed/day13_features.csv")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    # Normalize potential missing columns
    if args.ratings_col not in df.columns:
        df[args.ratings_col] = 0.0
    if args.reviews_col not in df.columns:
        df[args.reviews_col] = 0

    # Simple impute
    df[args.ratings_col] = df[args.ratings_col].fillna(df[args.ratings_col].median())
    df[args.reviews_col] = df[args.reviews_col].fillna(0).astype(int)

    df.to_csv(args.out, index=False)
    print(f"Saved feature-augmented data to {args.out}")


if __name__ == "__main__":
    main()

