#!/usr/bin/env python3
"""Test the advanced scraper functionality."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.advanced_scrape import EtsyScraper, AsyncEtsyScraper
from rich.console import Console

console = Console()

def test_basic_scraper():
    """Test basic scraper functionality."""
    console.print("[bold blue]Testing Basic Scraper[/bold blue]")
    
    scraper = EtsyScraper(delay_range=(0.5, 1.0))
    
    # Test URL
    test_url = "https://www.etsy.com/search?q=poster"
    
    console.print(f"Testing URL: {test_url}")
    
    # Test single page
    products = scraper.scrape_search_page(test_url)
    
    console.print(f"[green]Found {len(products)} products[/green]")
    
    if products:
        console.print("Sample product:")
        sample = products[0]
        for key, value in sample.items():
            if value:
                console.print(f"  {key}: {value}")
    
    return len(products) > 0

async def test_async_scraper():
    """Test async scraper functionality."""
    console.print("[bold blue]Testing Async Scraper[/bold blue]")
    
    scraper = AsyncEtsyScraper(delay_range=(0.3, 0.7))
    
    # Test URLs
    test_urls = [
        "https://www.etsy.com/search?q=poster",
        "https://www.etsy.com/search?q=wall+art",
    ]
    
    console.print(f"Testing {len(test_urls)} URLs")
    
    # Test async scraping
    products = await scraper.scrape_pages_async(test_urls)
    
    console.print(f"[green]Found {len(products)} products total[/green]")
    
    return len(products) > 0

def test_data_analysis():
    """Test data analysis functionality."""
    console.print("[bold blue]Testing Data Analysis[/bold blue]")
    
    try:
        import pandas as pd
        from utils.advanced_scrape import save_products_csv, save_products_json
        
        # Create sample data
        sample_data = [
            {
                "title": "Vintage Poster",
                "price": "$25.99",
                "url": "https://example.com/1",
                "seller": "VintageShop",
                "rating": "4.5",
                "review_count": "120",
            },
            {
                "title": "Modern Art Print",
                "price": "$45.00",
                "url": "https://example.com/2",
                "seller": "ArtGallery",
                "rating": "4.8",
                "review_count": "89",
            },
        ]
        
        # Test CSV saving
        csv_file = "test_output.csv"
        save_products_csv(sample_data, csv_file)
        console.print(f"[green]Saved CSV: {csv_file}[/green]")
        
        # Test JSON saving
        json_file = "test_output.json"
        save_products_json(sample_data, json_file)
        console.print(f"[green]Saved JSON: {json_file}[/green]")
        
        # Clean up
        Path(csv_file).unlink(missing_ok=True)
        Path(json_file).unlink(missing_ok=True)
        
        return True
        
    except Exception as e:
        console.print(f"[red]Data analysis test failed: {e}[/red]")
        return False

def main():
    """Run all tests."""
    console.print("[bold]🧪 Testing Advanced Scraper[/bold]")
    
    tests = [
        ("Basic Scraper", test_basic_scraper),
        ("Data Analysis", test_data_analysis),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        console.print(f"\n[bold yellow]Running {test_name}...[/bold yellow]")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                console.print(f"[green]✅ {test_name} passed[/green]")
            else:
                console.print(f"[red]❌ {test_name} failed[/red]")
        except Exception as e:
            console.print(f"[red]❌ {test_name} error: {e}[/red]")
            results.append((test_name, False))
    
    # Test async scraper
    console.print(f"\n[bold yellow]Running Async Scraper...[/bold yellow]")
    try:
        result = asyncio.run(test_async_scraper())
        results.append(("Async Scraper", result))
        if result:
            console.print(f"[green]✅ Async Scraper passed[/green]")
        else:
            console.print(f"[red]❌ Async Scraper failed[/red]")
    except Exception as e:
        console.print(f"[red]❌ Async Scraper error: {e}[/red]")
        results.append(("Async Scraper", False))
    
    # Summary
    console.print(f"\n[bold]📊 Test Results:[/bold]")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        console.print(f"  {test_name}: {status}")
    
    console.print(f"\n[bold]Total: {passed}/{total} tests passed[/bold]")
    
    if passed == total:
        console.print("[bold green]🎉 All tests passed![/bold green]")
    else:
        console.print("[bold red]⚠️  Some tests failed[/bold red]")

if __name__ == "__main__":
    main()
