#!/usr/bin/env python3
"""Gelişmiş Etsy scraper with enhanced data collection and error handling."""

import argparse
import asyncio
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.utils.advanced_scrape import EtsyScraper, AsyncEtsyScraper, save_products_json, save_products_csv
from src.utils.io import write_csv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

console = Console()

def display_results(products: List[Dict[str, Any]], category: str = "") -> None:
    """Display scraping results in a nice table."""
    if not products:
        console.print("[red]No products found![/red]")
        return
    
    table = Table(title=f"Scraped Products {f'from {category}' if category else ''}")
    table.add_column("Title", style="cyan", no_wrap=False)
    table.add_column("Price", style="green")
    table.add_column("Seller", style="blue")
    table.add_column("Rating", style="yellow")
    table.add_column("URL", style="dim")
    
    for product in products[:10]:  # Show first 10
        title = product.get("title", "")[:50] + "..." if len(product.get("title", "")) > 50 else product.get("title", "")
        price = product.get("price", "")
        seller = product.get("seller", "")
        rating = product.get("rating", "")
        url = product.get("url", "")[:30] + "..." if len(product.get("url", "")) > 30 else product.get("url", "")
        
        table.add_row(title, price, seller, rating, url)
    
    console.print(table)
    
    if len(products) > 10:
        console.print(f"[dim]... and {len(products) - 10} more products[/dim]")

def main() -> None:
    parser = argparse.ArgumentParser(description="Gelişmiş Etsy scraper")
    parser.add_argument("--url", required=True, help="Etsy search/category URL")
    parser.add_argument("--max-pages", type=int, default=5, help="Maximum pages to scrape")
    parser.add_argument("--delay", type=float, default=1.5, help="Delay between requests (seconds)")
    parser.add_argument("--output", default="data/raw/advanced_products", help="Output file prefix")
    parser.add_argument("--format", choices=["csv", "json", "both"], default="both", help="Output format")
    parser.add_argument("--async", action="store_true", dest="use_async", help="Use async scraping (faster)")
    parser.add_argument("--categories", help="YAML file with multiple categories")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    console.print(Panel.fit(
        "[bold blue]Etsy Advanced Scraper[/bold blue]\n"
        f"URL: {args.url}\n"
        f"Max Pages: {args.max_pages}\n"
        f"Delay: {args.delay}s\n"
        f"Format: {args.format}\n"
        f"Async: {args.use_async}",
        title="Configuration"
    ))
    
    # Ensure output directory exists
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    
    try:
        if args.categories:
            # Scrape multiple categories
            import yaml
            with open(args.categories, 'r', encoding='utf-8') as f:
                categories = yaml.safe_load(f)
            
            scraper = EtsyScraper(delay_range=(args.delay, args.delay + 1))
            all_products = []
            
            for name, url in categories.items():
                console.print(f"\n[bold]Scraping category: {name}[/bold]")
                products = scraper.scrape_multiple_pages(url, args.max_pages)
                all_products.extend(products)
                console.print(f"Found {len(products)} products in {name}")
            
            console.print(f"\n[bold green]Total products: {len(all_products)}[/bold green]")
            
        else:
            # Scrape single URL
            if args.use_async:
                # Async scraping
                console.print("[yellow]Using async scraping...[/yellow]")
                scraper = AsyncEtsyScraper(delay_range=(args.delay, args.delay + 0.5))
                
                # Generate URLs for all pages
                urls = []
                for page in range(1, args.max_pages + 1):
                    page_url = scraper._add_page_param(args.url, page)
                    urls.append(page_url)
                
                # Run async scraping
                all_products = asyncio.run(scraper.scrape_pages_async(urls))
                
            else:
                # Sync scraping
                scraper = EtsyScraper(delay_range=(args.delay, args.delay + 1))
                all_products = scraper.scrape_multiple_pages(args.url, args.max_pages)
        
        # Display results
        display_results(all_products, args.url)
        
        # Save results
        if args.format in ["csv", "both"]:
            csv_file = f"{args.output}.csv"
            save_products_csv(all_products, csv_file)
            console.print(f"[green]Saved CSV: {csv_file}[/green]")
        
        if args.format in ["json", "both"]:
            json_file = f"{args.output}.json"
            save_products_json(all_products, json_file)
            console.print(f"[green]Saved JSON: {json_file}[/green]")
        
        # Also save in the old format for compatibility
        if all_products:
            simple_data = []
            for product in all_products:
                simple_data.append({
                    "title": product.get("title", ""),
                    "price": product.get("price", ""),
                    "url": product.get("url", ""),
                })
            
            compat_file = f"{args.output}_compat.csv"
            write_csv(compat_file, simple_data, ["title", "price", "url"])
            console.print(f"[green]Saved compatibility CSV: {compat_file}[/green]")
        
        console.print(f"\n[bold green]✅ Successfully scraped {len(all_products)} products![/bold green]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Scraping interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        logger.exception("Scraping failed")
        raise

if __name__ == "__main__":
    main()
