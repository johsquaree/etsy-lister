import argparse

import pandas as pd

from src.utils.text import preprocess_text


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 06: Metin ön işleme (title/description)")
    parser.add_argument("--input", required=True, help="Temiz CSV (Day 04)")
    parser.add_argument("--output", default="data/processed/day06_text.csv", help="Ön işlenmiş CSV")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    if "title" in df.columns:
        df["title_clean"] = df["title"].fillna("").astype(str).apply(preprocess_text)
    if "description" in df.columns:
        df["description_clean"] = df["description"].fillna("").astype(str).apply(preprocess_text)

    df.to_csv(args.output, index=False)
    print(f"Saved preprocessed text to {args.output}")


if __name__ == "__main__":
    main()

