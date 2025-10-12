"""Proxy management and advanced rate limiting for web scraping."""

import random
import time
from typing import List, Optional, Tuple
from dataclasses import dataclass
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

@dataclass
class ProxyConfig:
    """Proxy configuration."""
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    protocol: str = "http"

class ProxyManager:
    """Manage proxy rotation and validation."""
    
    def __init__(self, proxies: List[ProxyConfig] = None):
        self.proxies = proxies or []
        self.current_proxy_index = 0
        self.failed_proxies = set()
    
    def get_next_proxy(self) -> Optional[dict]:
        """Get next available proxy."""
        if not self.proxies:
            return None
        
        available_proxies = [p for i, p in enumerate(self.proxies) if i not in self.failed_proxies]
        if not available_proxies:
            # Reset failed proxies if all failed
            self.failed_proxies.clear()
            available_proxies = self.proxies
        
        proxy_config = available_proxies[self.current_proxy_index % len(available_proxies)]
        self.current_proxy_index += 1
        
        proxy_dict = {
            "http": f"{proxy_config.protocol}://{proxy_config.host}:{proxy_config.port}",
            "https": f"{proxy_config.protocol}://{proxy_config.host}:{proxy_config.port}",
        }
        
        if proxy_config.username and proxy_config.password:
            proxy_dict["http"] = f"{proxy_config.protocol}://{proxy_config.username}:{proxy_config.password}@{proxy_config.host}:{proxy_config.port}"
            proxy_dict["https"] = f"{proxy_config.protocol}://{proxy_config.username}:{proxy_config.password}@{proxy_config.host}:{proxy_config.port}"
        
        return proxy_dict
    
    def mark_proxy_failed(self, proxy_index: int):
        """Mark a proxy as failed."""
        self.failed_proxies.add(proxy_index)
    
    def test_proxy(self, proxy_dict: dict, test_url: str = "https://httpbin.org/ip") -> bool:
        """Test if proxy is working."""
        try:
            response = requests.get(test_url, proxies=proxy_dict, timeout=10)
            return response.status_code == 200
        except:
            return False

class RateLimiter:
    """Advanced rate limiting with adaptive delays."""
    
    def __init__(self, base_delay: float = 1.0, max_delay: float = 10.0):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.current_delay = base_delay
        self.consecutive_errors = 0
        self.last_request_time = 0
    
    def wait(self):
        """Wait with adaptive delay."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.current_delay:
            sleep_time = self.current_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def on_success(self):
        """Called on successful request."""
        self.consecutive_errors = 0
        # Gradually decrease delay on success
        self.current_delay = max(self.base_delay, self.current_delay * 0.9)
    
    def on_error(self, error_type: str = "generic"):
        """Called on failed request."""
        self.consecutive_errors += 1
        
        if error_type == "rate_limit":
            # Exponential backoff for rate limiting
            self.current_delay = min(self.max_delay, self.current_delay * 2)
        else:
            # Linear increase for other errors
            self.current_delay = min(self.max_delay, self.current_delay * 1.5)
        
        # Add random jitter
        jitter = random.uniform(0.1, 0.5)
        time.sleep(self.current_delay + jitter)

class RobustScraper:
    """Scraper with proxy support and advanced rate limiting."""
    
    def __init__(self, proxies: List[ProxyConfig] = None, rate_limit: RateLimiter = None):
        self.proxy_manager = ProxyManager(proxies)
        self.rate_limiter = rate_limit or RateLimiter()
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def get_page(self, url: str) -> Optional[requests.Response]:
        """Get page with proxy rotation and rate limiting."""
        max_attempts = 3
        
        for attempt in range(max_attempts):
            self.rate_limiter.wait()
            
            proxy = self.proxy_manager.get_next_proxy()
            if proxy:
                self.session.proxies.update(proxy)
            
            try:
                response = self.session.get(url, timeout=30)
                
                if response.status_code == 200:
                    self.rate_limiter.on_success()
                    return response
                elif response.status_code == 429:
                    self.rate_limiter.on_error("rate_limit")
                    continue
                else:
                    self.rate_limiter.on_error("http_error")
                    continue
                    
            except requests.RequestException as e:
                self.rate_limiter.on_error("request_error")
                if proxy:
                    # Mark current proxy as failed
                    self.proxy_manager.mark_proxy_failed(
                        self.proxy_manager.current_proxy_index - 1
                    )
                continue
        
        return None
