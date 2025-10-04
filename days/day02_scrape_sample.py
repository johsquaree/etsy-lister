import argparse
from typing import Dict, List

from bs4 import BeautifulSoup

from src.utils.io import write_csv
from src.utils.scrape import extract_text, get_soup


def parse_listing_cards(soup: BeautifulSoup) -> List[Dict[str, str]]:
    items: List[Dict[str, str]] = []
    if not soup:
        return items

    # Etsy DOM değişebilir; yaygın seçicilerle esnek topla
    for card in soup.select("li.wt-list-unstyled, li[data-listing-id], li[data-logger-id]"):
        title_el = card.select_one("h3") or card.select_one(".wt-text-truncate")
        price_el = card.select_one(".currency-value") or card.select_one(".wt-text-title-01")
        link_el = card.select_one("a")
        link = link_el.get("href") if link_el else ""

        title = extract_text(title_el)
        price = extract_text(price_el)

        if title or price or link:
            items.append({
                "title": title,
                "price": price,
                "url": link,
            })
    return items


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 02: Tek sayfa Etsy kategori örnek çekimi")
    parser.add_argument("--category_url", required=True, help="Etsy kategori veya arama URL")
    parser.add_argument("--delay", type=float, default=1.0, help="İstekler arası bekleme (s)")
    args = parser.parse_args()

    soup = get_soup(args.category_url, delay_seconds=args.delay)
    rows = parse_listing_cards(soup)

    out_path = "data/raw/day02_sample.csv"
    write_csv(out_path, rows, ["title", "price", "url"])
    print(f"Saved {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()

