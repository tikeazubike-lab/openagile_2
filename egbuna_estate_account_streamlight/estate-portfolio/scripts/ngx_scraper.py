#!/usr/bin/env python3
"""
NGX Price Scraper - Runs weekly via cron
"""

import requests
from bs4 import BeautifulSoup
import psycopg2
from datetime import datetime
import logging
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/cron.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Connect to PostgreSQL"""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "estate_portfolio"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres")
    )

def scrape_ngx_prices():
    """
    Scrape current prices from NGX website
    NOTE: Update URL and selectors based on actual NGX website structure
    """
    url = "https://ngxgroup.com/exchange/data/equities-price-list/"
    
    try:
        logger.info("Starting NGX price scrape...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        prices = []
        # TODO: Adjust selectors based on actual NGX website
        # This is a placeholder - inspect NGX website and update
        table = soup.find('table', {'class': 'market-data'})
        if table:
            for row in table.find_all('tr')[1:]:  # Skip header
                cols = row.find_all('td')
                if len(cols) >= 3:
                    ticker = cols[0].text.strip()
                    try:
                        close_price = float(cols[2].text.strip().replace(',', ''))
                        prices.append({'ticker': ticker, 'price': close_price})
                    except (ValueError, IndexError) as e:
                        logger.warning(f"Could not parse price for {ticker}: {e}")
                        continue
        
        logger.info(f"Scraped {len(prices)} prices")
        return prices
    
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        return []

def update_database(prices):
    """Update companies and price_history tables"""
    if not prices:
        logger.warning("No prices to update")
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    today = datetime.now().date()
    
    updated_count = 0
    failed_count = 0
    
    for item in prices:
        try:
            # Update current_price in companies table
            cursor.execute("""
                UPDATE companies
                SET current_price = %s, last_price_update = NOW()
                WHERE ticker = %s AND deleted_at IS NULL
                RETURNING id
            """, (item['price'], item['ticker']))
            
            result = cursor.fetchone()
            if result:
                company_id = result[0]
                
                # Insert into price_history
                cursor.execute("""
                    INSERT INTO price_history (
                        company_id, price_date, close_price, source
                    ) VALUES (%s, %s, %s, 'ngx_scraper')
                    ON CONFLICT (company_id, price_date) DO UPDATE
                    SET close_price = EXCLUDED.close_price
                """, (company_id, today, item['price']))
                
                updated_count += 1
                logger.info(f"✅ Updated {item['ticker']}: ₦{item['price']}")
            else:
                logger.warning(f"Company {item['ticker']} not found in database")
                failed_count += 1
        
        except Exception as e:
            logger.error(f"Error updating {item['ticker']}: {e}")
            failed_count += 1
            continue
    
    conn.commit()
    cursor.close()
    conn.close()
    
    logger.info(f"Scraper completed: {updated_count} updated, {failed_count} failed")

if __name__ == "__main__":
    prices = scrape_ngx_prices()
    update_database(prices)
