import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 20: Kapanış ve değerlendirme notları")
    parser.add_argument("--out", default="outputs/day20_wrapup.md")
    args = parser.parse_args()

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("# Staj Değerlendirme\n\n")
        f.write("- Veri analizi, NLP, makine öğrenmesi ve web geliştirme adımları tamamlandı.\n")
        f.write("- Öğrenilenler: requests/BS4, pandas, TF-IDF, Logistic Regression, Flask.\n")
        f.write("- Gelecek: Gelişmiş modelleme (XGBoost), daha sağlam scraping (API), etiket önerici geliştirme.\n")

    print(f"Saved wrap-up to {args.out}")


if __name__ == "__main__":
    main()

