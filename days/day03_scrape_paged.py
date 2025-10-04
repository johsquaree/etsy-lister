import argparse
from typing import Dict, List
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from bs4 import BeautifulSoup

from src.utils.io import write_csv
from src.utils.scrape import extract_text, get_soup


def set_url_page(url: str, page: int) -> str:
    parts = urlparse(url)
    q = parse_qs(parts.query)
    q["page"] = [str(page)]
    new_query = urlencode(q, doseq=True)
    return urlunparse((parts.scheme, parts.netloc, parts.path, parts.params, new_query, parts.fragment))


def parse_listing_cards(soup: BeautifulSoup) -> List[Dict[str, str]]:
    items: List[Dict[str, str]] = []
    if not soup:
        return items
    for card in soup.select("li.wt-list-unstyled, li[data-listing-id], li[data-logger-id]"):
        title_el = card.select_one("h3") or card.select_one(".wt-text-truncate")
        price_el = card.select_one(".currency-value") or card.select_one(".wt-text-title-01")
        link_el = card.select_one("a")
        link = link_el.get("href") if link_el else ""
        title = extract_text(title_el)
        price = extract_text(price_el)
        if title or price or link:
            items.append({"title": title, "price": price, "url": link})
    return items


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 03: Etsy sayfalı çekim")
    parser.add_argument("--category_url", required=False, help="Etsy kategori veya arama URL")
    parser.add_argument("--categories_yaml", required=False, help="categories.yaml ile çoklu kategori")
    parser.add_argument("--max_pages", type=int, default=5, help="Toplanacak sayfa sayısı")
    parser.add_argument("--delay", type=float, default=1.0, help="İstekler arası bekleme (s)")
    args = parser.parse_args()

    all_rows: List[Dict[str, str]] = []
    targets: List[str] = []
    if args.categories_yaml:
        import yaml
        with open(args.categories_yaml, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        targets = list(cfg.values())
    elif args.category_url:
        targets = [args.category_url]
    else:
        raise SystemExit("Provide --category_url or --categories_yaml")

    for url in targets:
        print(f"Category: {url}")
        for page in range(1, args.max_pages + 1):
            page_url = set_url_page(url, page)
            soup = get_soup(page_url, delay_seconds=args.delay)
            rows = parse_listing_cards(soup)
            print(f"  Page {page}: {len(rows)} items")
            all_rows.extend(rows)

    out_path = "data/raw/day03_products.csv"
    write_csv(out_path, all_rows, ["title", "price", "url"])
    print(f"Saved {len(all_rows)} rows to {out_path}")


if __name__ == "__main__":
    main()

