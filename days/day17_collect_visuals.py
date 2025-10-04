import argparse

import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 17: Görselleri derleme (word cloud vs.)")
    parser.add_argument("--input", default="data/processed/day06_text.csv")
    parser.add_argument("--out_cloud", default="outputs/plots/day17_wordcloud.png")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    text = " ".join(df.get("title_clean", pd.Series(dtype=str)).fillna("").astype(str).tolist())

    wc = WordCloud(width=1000, height=600, background_color="white").generate(text)
    plt.figure(figsize=(10, 6))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(args.out_cloud, dpi=150)
    plt.close()

    print(f"Saved word cloud to {args.out_cloud}")


if __name__ == "__main__":
    main()

