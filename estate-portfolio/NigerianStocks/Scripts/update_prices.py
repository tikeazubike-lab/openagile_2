#!/usr/bin/env python3
"""
Enhanced Nigerian Stock Exchange Price Updater for Obsidian
Status-aware: Only updates prices for listed companies
"""

import os
import re
from datetime import datetime
from pathlib import Path
import requests
from typing import Dict, List, Optional, Tuple
import time

# Configuration
VAULT_PATH = Path("/home/zubbyik/ObsidianVault/NigerianStocks")
COMPANIES_DIR = VAULT_PATH / "Companies"
PRICES_DIR = VAULT_PATH / "Prices"
LOG_FILE = VAULT_PATH / "price_update.log"

# Yahoo Finance configuration
YAHOO_BASE = "https://query1.finance.yahoo.com/v8/finance/chart/"
TICKER_SUFFIX = ".LG"
REQUEST_DELAY = 1  # seconds between requests

# Status categories
TRADEABLE_STATUS = ["listed"]

class StockPriceUpdater:
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.companies_dir = vault_path / "Companies"
        self.prices_dir = vault_path / "Prices"
        self.log_file = vault_path / "price_update.log"
        
        self.stats = {
            "listed_updated": 0,
            "listed_failed": 0,
            "skipped": 0,
            "total_processed": 0
        }
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages to file and console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [{level}] {message}"
        print(log_msg)
        with open(self.log_file, "a") as f:
            f.write(log_msg + "\n")
    
    def read_frontmatter(self, filepath: Path) -> Dict:
        """Extract YAML frontmatter from markdown file"""
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
                        if value and value != '""' and value != "''":
                            frontmatter[key] = value
                return frontmatter
            return {}
        except Exception as e:
            self.log(f"Error reading {filepath}: {e}", "ERROR")
            return {}
    
    def update_frontmatter(self, filepath: Path, updates: Dict):
        """Update YAML frontmatter in markdown file"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
            if not match:
                self.log(f"No frontmatter found in {filepath}", "WARNING")
                return False
            
            frontmatter_lines = match.group(1).split('\n')
            body = match.group(2)
            
            # Update specific fields
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
    
    def fetch_yahoo_price(self, ticker: str) -> Optional[Dict]:
        """Fetch stock price from Yahoo Finance"""
        yahoo_ticker = ticker + TICKER_SUFFIX
        url = f"{YAHOO_BASE}{yahoo_ticker}"
        
        params = {"interval": "1d", "range": "5d"}
        headers = {"User-Agent": "Mozilla/5.0"}
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            chart = data["chart"]["result"][0]
            quote = chart["indicators"]["quote"][0]
            timestamps = chart["timestamp"]
            
            if not timestamps:
                return None
            
            latest_idx = -1
            latest_date = datetime.fromtimestamp(timestamps[latest_idx])
            
            prev_close = 0
            if len(quote["close"]) > 1:
                for i in range(len(quote["close"]) - 2, -1, -1):
                    if quote["close"][i]:
                        prev_close = round(quote["close"][i], 2)
                        break
            
            return {
                "date": latest_date.strftime("%Y-%m-%d"),
                "open": round(quote["open"][latest_idx], 2) if quote["open"][latest_idx] else 0,
                "high": round(quote["high"][latest_idx], 2) if quote["high"][latest_idx] else 0,
                "low": round(quote["low"][latest_idx], 2) if quote["low"][latest_idx] else 0,
                "close": round(quote["close"][latest_idx], 2) if quote["close"][latest_idx] else 0,
                "volume": int(quote["volume"][latest_idx]) if quote["volume"][latest_idx] else 0,
                "prev_close": prev_close,
            }
        except Exception as e:
            self.log(f"Error fetching {ticker}: {e}", "ERROR")
            return None
    
    def get_tradeable_companies(self) -> List[Dict]:
        """Get list of companies that can be traded (listed status)"""
        tradeable = []
        
        if not self.companies_dir.exists():
            self.log(f"Companies directory not found: {self.companies_dir}", "ERROR")
            return tradeable
        
        for filepath in self.companies_dir.glob("*.md"):
            if "Special-Entities" in filepath.name:
                continue
                
            frontmatter = self.read_frontmatter(filepath)
            if frontmatter.get("type") != "company":
                continue
            
            status = frontmatter.get("status", "unknown")
            
            if status in TRADEABLE_STATUS:
                tradeable.append({
                    "filepath": filepath,
                    "name": frontmatter.get("name", ""),
                    "ticker": frontmatter.get("ticker", ""),
                    "status": status,
                })
        
        return tradeable
    
    def create_price_log(self, ticker: str, price_data: Dict):
        """Create daily price log file"""
        ticker_dir = self.prices_dir / ticker
        ticker_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = ticker_dir / f"{price_data['date']}.md"
        
        if log_file.exists():
            return
        
        change = price_data['close'] - price_data['prev_close']
        change_pct = round((change / price_data['prev_close'] * 100), 2) if price_data['prev_close'] > 0 else 0
        
        content = f"""---
type: price-log
ticker: "{ticker}"
date: {price_data['date']}
close: {price_data['close']}
open: {price_data['open']}
high: {price_data['high']}
low: {price_data['low']}
volume: {price_data['volume']}
prev_close: {price_data['prev_close']}
change: {change}
change_pct: {change_pct}
---

# {ticker} - {price_data['date']}

**Close:** ₦{price_data['close']:,.2f}  
**Change:** ₦{change:,.2f} ({change_pct:+.2f}%)  
**Range:** ₦{price_data['low']:,.2f} - ₦{price_data['high']:,.2f}  
**Volume:** {price_data['volume']:,}
"""
        
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(content)
    
    def run(self):
        """Main execution"""
        self.log("=" * 70)
        self.log("NGX Stock Price Update - Fedora Edition")
        self.log("=" * 70)
        
        tradeable = self.get_tradeable_companies()
        
        self.log(f"Found {len(tradeable)} listed companies to update")
        
        for company in tradeable:
            ticker = company["ticker"]
            if not ticker:
                self.log(f"Skipping {company['name']}: No ticker", "WARNING")
                continue
            
            self.log(f"Fetching price for {ticker} ({company['name']})...")
            self.stats["total_processed"] += 1
            
            price_data = self.fetch_yahoo_price(ticker)
            
            if price_data:
                if self.update_frontmatter(company["filepath"], {
                    "latest_price": price_data['close'],
                    "latest_price_date": price_data['date']
                }):
                    self.log(f"✓ Updated {ticker}: ₦{price_data['close']:,.2f}", "SUCCESS")
                    self.create_price_log(ticker, price_data)
                    self.stats["listed_updated"] += 1
                else:
                    self.log(f"✗ Failed to update file for {ticker}", "ERROR")
                    self.stats["listed_failed"] += 1
            else:
                self.log(f"✗ Failed to fetch price for {ticker}", "ERROR")
                self.stats["listed_failed"] += 1
            
            time.sleep(REQUEST_DELAY)
        
        self.log("=" * 70)
        self.log("UPDATE SUMMARY")
        self.log("=" * 70)
        self.log(f"Listed companies updated: {self.stats['listed_updated']}")
        self.log(f"Listed companies failed: {self.stats['listed_failed']}")
        self.log("=" * 70)

def main():
    updater = StockPriceUpdater(VAULT_PATH)
    updater.run()

if __name__ == "__main__":
    main()
