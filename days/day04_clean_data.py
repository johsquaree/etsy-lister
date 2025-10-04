import argparse
import re

import pandas as pd


def parse_price_to_float(price_str: str) -> float:
    if not isinstance(price_str, str):
        return float("nan")
    # Keep digits and dot/comma, convert comma to dot if needed
    cleaned = re.sub(r"[^0-9.,]", "", price_str)
    cleaned = cleaned.replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return float("nan")


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 04: Veri temizleme")
    parser.add_argument("--input", required=True, help="Ham CSV yolu (Day 02/03 çıktısı)")
    parser.add_argument("--output", default="data/processed/day04_clean.csv", help="Temiz CSV çıktısı")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    # Drop completely empty rows
    df = df.dropna(how="all")
    # Basic trims
    df["title"] = df["title"].fillna("").astype(str).str.strip()
    df["url"] = df["url"].fillna("").astype(str).str.strip()
    # Price to float
    df["price_value"] = df["price"].apply(parse_price_to_float)
    # Remove rows without title or url
    df = df[(df["title"] != "") & (df["url"] != "")]
    # Drop duplicates by url
    df = df.drop_duplicates(subset=["url"]) 

    df.to_csv(args.output, index=False)
    print(f"Saved cleaned data: {args.output} (rows={len(df)})")


if __name__ == "__main__":
    main()

