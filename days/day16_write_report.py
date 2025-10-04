import argparse

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 16: Rapor metni (taslak)")
    parser.add_argument("--clean", default="data/processed/day04_clean.csv")
    parser.add_argument("--out", default="outputs/day16_report.md")
    args = parser.parse_args()

    df = pd.read_csv(args.clean)
    n = len(df)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("# Proje Raporu (Taslak)\n\n")
        f.write("Bu rapor, veri toplama, temizleme, NLP, makine öğrenmesi ve web arayüzü adımlarını özetler.\n\n")
        f.write(f"Toplam ürün: {n}\n\n")
        f.write("## Kütüphaneler\n- pandas, numpy\n- requests, beautifulsoup4\n- scikit-learn, matplotlib, wordcloud\n- flask\n\n")
        f.write("## Veri Toplama\nKategori sayfalarından başlık, fiyat ve URL alanları çekildi.\n\n")
        f.write("## Temizleme\nFiyatlar sayısal formata çevrildi, boş kayıtlar çıkarıldı.\n\n")
        f.write("## NLP\nMetinler küçük harfe çevrilip noktalama ve stopwords temizlendi; TF-IDF ile önemli kelimeler bulundu.\n\n")
        f.write("## Model\nLogistic Regression ile basit bir sınıflandırma yapıldı ve doğruluk raporlandı.\n\n")
        f.write("## Web Uygulaması\nFlask ile başlık/fiyat girdisine göre satış potansiyeli tahmini yapıldı.\n")

    print(f"Saved report draft to {args.out}")


if __name__ == "__main__":
    main()

