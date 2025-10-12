"""Gelişmiş web scraping utilities for Etsy product collection."""

import asyncio
import json
import logging
import random
import time
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import aiohttp
import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

console = Console()

# Gelişmiş User-Agent rotasyonu
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
]

class EtsyScraper:
    """Gelişmiş Etsy scraper with retry, rate limiting, and async support."""
    
    def __init__(self, delay_range: Tuple[float, float] = (1.0, 3.0), max_retries: int = 3):
        self.delay_range = delay_range
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update(self._get_random_headers())
        
    def _get_random_headers(self) -> Dict[str, str]:
        """Random headers for better stealth."""
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0",
        }
    
    def _random_delay(self) -> None:
        """Random delay between requests."""
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)
    
    def get_page(self, url: str, retries: int = None) -> Optional[BeautifulSoup]:
        """Get page with retry logic and error handling."""
        if retries is None:
            retries = self.max_retries
            
        for attempt in range(retries + 1):
            try:
                self._random_delay()
                response = self.session.get(url, timeout=30)
                
                if response.status_code == 200:
                    return BeautifulSoup(response.text, "html.parser")
                elif response.status_code == 429:  # Rate limited
                    wait_time = 2 ** attempt
                    logger.warning(f"Rate limited. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.warning(f"HTTP {response.status_code} for {url}")
                    
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt < retries:
                    time.sleep(2 ** attempt)
                    
        return None
    
    def parse_product_card(self, card) -> Dict[str, Any]:
        """Parse individual product card with more data fields."""
        data = {
            "title": "",
            "price": "",
            "url": "",
            "image_url": "",
            "seller": "",
            "rating": "",
            "review_count": "",
            "favorites": "",
            "location": "",
            "shipping": "",
            "tags": "",
            "description": "",
        }
        
        # Title
        title_el = card.select_one("h3, .wt-text-truncate, [data-test-id='listing-card-title']")
        if title_el:
            data["title"] = title_el.get_text(strip=True)
        
        # Price
        price_el = card.select_one(".currency-value, .wt-text-title-01, [data-test-id='price']")
        if price_el:
            data["price"] = price_el.get_text(strip=True)
        
        # URL
        link_el = card.select_one("a")
        if link_el:
            href = link_el.get("href", "")
            if href:
                data["url"] = urljoin("https://www.etsy.com", href)
        
        # Image
        img_el = card.select_one("img")
        if img_el:
            data["image_url"] = img_el.get("src", "") or img_el.get("data-src", "")
        
        # Seller
        seller_el = card.select_one(".shop-name, [data-test-id='shop-name']")
        if seller_el:
            data["seller"] = seller_el.get_text(strip=True)
        
        # Rating
        rating_el = card.select_one(".rating, [data-test-id='rating']")
        if rating_el:
            data["rating"] = rating_el.get_text(strip=True)
        
        # Review count
        review_el = card.select_one(".review-count, [data-test-id='review-count']")
        if review_el:
            data["review_count"] = review_el.get_text(strip=True)
        
        # Favorites
        fav_el = card.select_one(".favorite-count, [data-test-id='favorite-count']")
        if fav_el:
            data["favorites"] = fav_el.get_text(strip=True)
        
        # Location
        loc_el = card.select_one(".shop-location, [data-test-id='shop-location']")
        if loc_el:
            data["location"] = loc_el.get_text(strip=True)
        
        # Shipping
        ship_el = card.select_one(".shipping-info, [data-test-id='shipping-info']")
        if ship_el:
            data["shipping"] = ship_el.get_text(strip=True)
        
        return data
    
    def scrape_search_page(self, url: str) -> List[Dict[str, Any]]:
        """Scrape a single search page with enhanced data extraction."""
        soup = self.get_page(url)
        if not soup:
            return []
        
        products = []
        
        # Multiple selectors for different Etsy layouts
        selectors = [
            "li.wt-list-unstyled",
            "li[data-listing-id]",
            "li[data-logger-id]",
            ".listing-card",
            "[data-test-id='listing-card']",
        ]
        
        for selector in selectors:
            cards = soup.select(selector)
            if cards:
                logger.info(f"Found {len(cards)} products with selector: {selector}")
                for card in cards:
                    product_data = self.parse_product_card(card)
                    if product_data.get("title") or product_data.get("url"):
                        products.append(product_data)
                break
        
        return products
    
    def scrape_multiple_pages(self, base_url: str, max_pages: int = 5) -> List[Dict[str, Any]]:
        """Scrape multiple pages with progress tracking."""
        all_products = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Scraping pages...", total=max_pages)
            
            for page in range(1, max_pages + 1):
                page_url = self._add_page_param(base_url, page)
                products = self.scrape_search_page(page_url)
                
                if not products:
                    logger.warning(f"No products found on page {page}")
                    break
                
                all_products.extend(products)
                progress.update(task, advance=1, description=f"Page {page}: {len(products)} products")
                
                # Break if we got fewer products than expected (might be last page)
                if len(products) < 20:  # Etsy typically shows 20+ products per page
                    logger.info("Reached end of results")
                    break
        
        return all_products
    
    def _add_page_param(self, url: str, page: int) -> str:
        """Add page parameter to URL."""
        from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
        
        parts = urlparse(url)
        query = parse_qs(parts.query)
        query["page"] = [str(page)]
        new_query = urlencode(query, doseq=True)
        return urlunparse((parts.scheme, parts.netloc, parts.path, parts.params, new_query, parts.fragment))
    
    def scrape_categories(self, categories: List[str], max_pages_per_category: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """Scrape multiple categories."""
        results = {}
        
        for category in categories:
            logger.info(f"Scraping category: {category}")
            products = self.scrape_multiple_pages(category, max_pages_per_category)
            results[category] = products
            logger.info(f"Found {len(products)} products in {category}")
        
        return results


class AsyncEtsyScraper:
    """Async version of Etsy scraper for better performance."""
    
    def __init__(self, delay_range: Tuple[float, float] = (0.5, 1.5), max_concurrent: int = 5):
        self.delay_range = delay_range
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def get_page_async(self, session: aiohttp.ClientSession, url: str) -> Optional[BeautifulSoup]:
        """Async page fetching."""
        async with self.semaphore:
            try:
                await asyncio.sleep(random.uniform(*self.delay_range))
                
                headers = {
                    "User-Agent": random.choice(USER_AGENTS),
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                }
                
                async with session.get(url, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        html = await response.text()
                        return BeautifulSoup(html, "html.parser")
                    else:
                        logger.warning(f"HTTP {response.status} for {url}")
                        return None
                        
            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
                return None
    
    async def scrape_pages_async(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Scrape multiple pages concurrently."""
        async with aiohttp.ClientSession() as session:
            tasks = [self.get_page_async(session, url) for url in urls]
            soups = await asyncio.gather(*tasks, return_exceptions=True)
            
            all_products = []
            scraper = EtsyScraper()
            
            for soup in soups:
                if isinstance(soup, BeautifulSoup):
                    products = scraper.scrape_search_page_from_soup(soup)
                    all_products.extend(products)
            
            return all_products


def save_products_json(products: List[Dict[str, Any]], filename: str) -> None:
    """Save products to JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved {len(products)} products to {filename}")


def save_products_csv(products: List[Dict[str, Any]], filename: str) -> None:
    """Save products to CSV file."""
    import pandas as pd
    
    if not products:
        logger.warning("No products to save")
        return
    
    df = pd.DataFrame(products)
    df.to_csv(filename, index=False, encoding='utf-8')
    logger.info(f"Saved {len(products)} products to {filename}")
