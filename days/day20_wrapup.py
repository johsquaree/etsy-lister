import argparse
from typing import List, Dict, Any

from src.utils.advanced_scrape import EtsyScraper, save_products_csv, save_products_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 20: Gelişmiş scraping ile kapanış")
    parser.add_argument("--url", required=True, help="Etsy arama/kategori URL")
    parser.add_argument("--max-pages", type=int, default=5, help="Toplanacak sayfa sayısı")
    parser.add_argument("--delay", type=float, default=1.5, help="İstekler arası bekleme (s)")
    parser.add_argument("--out-prefix", default="data/raw/day20_products", help="Çıktı dosya ön eki (uzantısız)")
    parser.add_argument("--summary", default="outputs/day20_wrapup.md", help="Özet rapor yolu")
    parser.add_argument("--format", choices=["csv", "json", "both"], default="both", help="Çıktı formatı")
    args = parser.parse_args()

    # Scrape
    scraper = EtsyScraper(delay_range=(args.delay, args.delay + 1.0))
    products: List[Dict[str, Any]] = scraper.scrape_multiple_pages(args.url, args.max_pages)

    # Save products
    saved_paths: List[str] = []
    if args.format in ("csv", "both") and products:
        csv_path = f"{args.out_prefix}.csv"
        save_products_csv(products, csv_path)
        saved_paths.append(csv_path)
    if args.format in ("json", "both") and products:
        json_path = f"{args.out_prefix}.json"
        save_products_json(products, json_path)
        saved_paths.append(json_path)

    # Summary
    with open(args.summary, "w", encoding="utf-8") as f:
        f.write("# Day 20 Kapanış\n\n")
        f.write(f"- Kaynak URL: {args.url}\n")
        f.write(f"- Toplanan sayfa: {args.max_pages}\n")
        f.write(f"- Toplanan ürün: {len(products)}\n")
        f.write(f"- Çıkış dosyaları: {', '.join(saved_paths) if saved_paths else '—'}\n")
        f.write("- Alanlar: title, price, url, image_url, seller, rating, review_count (mümkün olduğunda)\n")

    print(f"Saved {len(products)} products. Summary -> {args.summary}")


if __name__ == "__main__":
    main()

