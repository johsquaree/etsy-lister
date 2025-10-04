import argparse

import matplotlib.pyplot as plt
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 05: Temel istatistikler ve görselleştirme")
    parser.add_argument("--input", required=True, help="Temiz CSV (Day 04)")
    parser.add_argument("--plots_dir", default="outputs/plots", help="Grafik çıktıları")
    parser.add_argument("--summary", default="outputs/day05_summary.md", help="Özet rapor")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    price_col = "price_value" if "price_value" in df.columns else "price"

    price_series = df[price_col].dropna()
    if price_series.empty:
        with open(args.summary, "w", encoding="utf-8") as f:
            f.write("# Day 05 Özet\n\n")
            f.write("Veri bulunamadı veya fiyat sütunu boş. Lütfen scraping adımını doğrulayın.\n")
        print(f"Saved summary to {args.summary} (no data)")
        return

    desc = price_series.describe(percentiles=[0.25, 0.5, 0.75])
    top5 = df.sort_values(price_col, ascending=False).head(5)
    low5 = df.sort_values(price_col, ascending=True).head(5)

    # Price histogram
    plt.figure(figsize=(8, 5))
    price_series.plot(kind="hist", bins=30, alpha=0.7)
    plt.title("Fiyat Dağılımı")
    plt.xlabel("Fiyat")
    plt.ylabel("Frekans")
    plt.tight_layout()
    price_hist_path = f"{args.plots_dir}/day05_price_hist.png"
    plt.savefig(price_hist_path, dpi=140)
    plt.close()

    with open(args.summary, "w", encoding="utf-8") as f:
        f.write("# Day 05 Özet\n\n")
        f.write("## Fiyat İstatistikleri\n\n")
        f.write(desc.to_frame().to_markdown())
        f.write("\n\n## En Pahalı 5 Ürün\n\n")
        f.write(top5[["title", price_col, "url"]].to_markdown(index=False))
        f.write("\n\n## En Ucuz 5 Ürün\n\n")
        f.write(low5[["title", price_col, "url"]].to_markdown(index=False))
        f.write(f"\n\n## Grafikler\n\n- Fiyat histogramı: {price_hist_path}\n")

    print(f"Saved summary to {args.summary} and plots to {args.plots_dir}")


if __name__ == "__main__":
    main()

