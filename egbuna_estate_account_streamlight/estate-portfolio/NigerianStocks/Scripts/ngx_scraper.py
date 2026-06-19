#!/usr/bin/env python3
"""
NGX Website Scraper - Nigerian Stock Price Updater
Scrapes prices directly from NGX Group website
"""

import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup

# Configuration
VAULT_PATH = Path("/home/zubbyik/ObsidianVault/NigerianStocks")
COMPANIES_DIR = VAULT_PATH / "Companies"
PRICES_DIR = VAULT_PATH / "Prices"
LOG_FILE = VAULT_PATH / "price_update.log"

# NGX URLs
NGX_BASE = "https://ngxgroup.com"
NGX_EQUITIES = f"{NGX_BASE}/exchange/data/equities-price-list/"
REQUEST_DELAY = 2  # Be nice to their servers

# Ticker mapping (NGX website uses different names sometimes)
TICKER_MAPPING = {
    "NESTLE": "NESTLE",
    "DANGCEM": "DANGCEM", 
    "ACCESSCORP": "ACCESSCORP",
    "FBNH": "FBNH",
    "ZENITHBANK": "ZENITHBANK",
    "GTCO": "GTCO",
    "UBA": "UBA",
    "NB": "NB",
    "FLOURMILL": "FLOURMILL",
    "OKOMUOIL": "OKOMUOIL",
    # Add more as needed
}


class NGXScraper:
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.companies_dir = vault_path / "Companies"
        self.prices_dir = vault_path / "Prices"
        self.log_file = vault_path / "price_update.log"
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        
        self.stats = {
            "updated": 0,
            "failed": 0,
            "not_found": 0
        }
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [{level}] {message}"
        print(log_msg)
        with open(self.log_file, "a") as f:
            f.write(log_msg + "\n")
    
    def read_frontmatter(self, filepath: Path) -> Dict:
        """Extract YAML frontmatter"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if match:
                frontmatter = {}
                for line in match.group(1).split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if value and value not in ['""', "''"]:
                            frontmatter[key] = value
                return frontmatter
            return {}
        except Exception as e:
            self.log(f"Error reading {filepath}: {e}", "ERROR")
            return {}
    
    def update_frontmatter(self, filepath: Path, updates: Dict) -> bool:
        """Update YAML frontmatter"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
            if not match:
                return False
            
            frontmatter_lines = match.group(1).split('\n')
            body = match.group(2)
            
            new_lines = []
            for line in frontmatter_lines:
                if ':' in line:
                    key = line.split(':')[0].strip()
                    if key in updates:
                        value = updates[key]
                        if isinstance(value, str) and not value.replace('.', '').replace('-', '').isdigit():
                            new_lines.append(f'{key}: "{value}"')
                        else:
                            new_lines.append(f'{key}: {value}')
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            
            new_content = f"---\n{chr(10).join(new_lines)}\n---\n{body}"
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            return True
        except Exception as e:
            self.log(f"Error updating {filepath}: {e}", "ERROR")
            return False
    
    def fetch_ngx_prices(self) -> Dict[str, float]:
        """Fetch all stock prices from NGX website"""
        self.log("Fetching price list from NGX website...")
        
        try:
            response = self.session.get(NGX_EQUITIES, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            prices = {}
            
            # Try to find the price table
            # NGX website structure may vary, trying multiple selectors
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) >= 3:
                        # Typical structure: Symbol | Name | Price | ...
                        try:
                            symbol = cells[0].get_text(strip=True).upper()
                            price_text = cells[2].get_text(strip=True)
                            
                            # Clean price text
                            price_text = price_text.replace(',', '').replace('₦', '')
                            price = float(price_text)
                            
                            if symbol and price > 0:
                                prices[symbol] = price
                                
                        except (ValueError, IndexError):
                            continue
            
            if prices:
                self.log(f"Successfully fetched {len(prices)} stock prices from NGX")
            else:
                self.log("Warning: No prices found in NGX page. Website structure may have changed.", "WARNING")
                
            return prices
            
        except Exception as e:
            self.log(f"Error fetching NGX prices: {e}", "ERROR")
            return {}
    
    def get_listed_companies(self) -> List[Dict]:
        """Get list of listed companies from vault"""
        companies = []
        
        if not self.companies_dir.exists():
            return companies
        
        for filepath in self.companies_dir.glob("*.md"):
            if "Special-Entities" in filepath.name:
                continue
                
            frontmatter = self.read_frontmatter(filepath)
            if frontmatter.get("type") != "company":
                continue
            
            if frontmatter.get("status") == "listed":
                companies.append({
                    "filepath": filepath,
                    "name": frontmatter.get("name", ""),
                    "ticker": frontmatter.get("ticker", ""),
                })
        
        return companies
    
    def create_price_log(self, ticker: str, price: float, date: str):
        """Create daily price log"""
        ticker_dir = self.prices_dir / ticker
        ticker_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = ticker_dir / f"{date}.md"
        
        if log_file.exists():
            return
        
        content = f"""---
type: price-log
ticker: "{ticker}"
date: {date}
close: {price}
source: "NGX Website"
---

# {ticker} - {date}

**Close:** ₦{price:,.2f}  
**Source:** NGX Group Website  
**Last Updated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(content)
    
    def run(self):
        """Main execution"""
        self.log("=" * 70)
        self.log("NGX Website Scraper - Price Update")
        self.log("=" * 70)
        
        # Fetch all prices from NGX
        ngx_prices = self.fetch_ngx_prices()
        
        if not ngx_prices:
            self.log("No prices fetched. Exiting.", "ERROR")
            return
        
        # Get companies to update
        companies = self.get_listed_companies()
        self.log(f"Found {len(companies)} listed companies in vault")
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        for company in companies:
            ticker = company["ticker"]
            if not ticker:
                continue
            
            # Try to find price
            price = None
            
            # Try exact match first
            if ticker in ngx_prices:
                price = ngx_prices[ticker]
            # Try common variations
            elif ticker.replace(".", "") in ngx_prices:
                price = ngx_prices[ticker.replace(".", "")]
            
            if price:
                # Update company file
                if self.update_frontmatter(company["filepath"], {
                    "latest_price": price,
                    "latest_price_date": today
                }):
                    self.log(f"✓ Updated {ticker}: ₦{price:,.2f}", "SUCCESS")
                    self.create_price_log(ticker, price, today)
                    self.stats["updated"] += 1
                else:
                    self.log(f"✗ Failed to update file for {ticker}", "ERROR")
                    self.stats["failed"] += 1
            else:
                self.log(f"⚠ Price not found on NGX for {ticker}", "WARNING")
                self.stats["not_found"] += 1
            
            time.sleep(0.5)  # Small delay between updates
        
        # Summary
        self.log("=" * 70)
        self.log("UPDATE SUMMARY")
        self.log("=" * 70)
        self.log(f"Successfully updated: {self.stats['updated']}")
        self.log(f"Not found on NGX: {self.stats['not_found']}")
        self.log(f"Failed to update: {self.stats['failed']}")
        self.log("=" * 70)


def main():
    scraper = NGXScraper(VAULT_PATH)
    scraper.run()


if __name__ == "__main__":
    main()
