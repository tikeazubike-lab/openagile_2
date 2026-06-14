#!/usr/bin/env python3
"""
RapidAPI (Yahoo Finance) Scraper for NGX Stocks
Uses 'sparior/yahoo-finance15' provider
"""

import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import logging
import os
import sys
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Connect to PostgreSQL using env vars"""
    try:
        return psycopg2.connect(
            host=os.getenv("DB_HOST", "postgres"),
            database=os.getenv("DB_NAME", "estate_portfolio"),
            user=os.getenv("DB_USER", "portfolio_user"),
            password=os.getenv("DB_PASSWORD"),
            cursor_factory=RealDictCursor
        )
    except Exception as e:
        logger.error(f"DB Connection failed: {e}")
        sys.exit(1)

def get_companies(conn):
    """Fetch all active companies from DB"""
    with conn.cursor() as cur:
        # Only fetch 'listed' companies to save API quota
        cur.execute("SELECT id, ticker, name FROM companies WHERE deleted_at IS NULL AND status = 'listed'")
        return cur.fetchall()

def update_price(conn, company_id, price):
    """Update company current price and insert history"""
    today = datetime.now().date()
    
    with conn.cursor() as cur:
        # Update current price
        cur.execute("""
            UPDATE companies 
            SET current_price = %s, last_price_update = NOW() 
            WHERE id = %s
        """, (price, company_id))
        
        # Insert history
        cur.execute("""
            INSERT INTO price_history (company_id, price_date, close_price, source)
            VALUES (%s, %s, %s, 'rapidapi')
            ON CONFLICT (company_id, price_date) 
            DO UPDATE SET close_price = EXCLUDED.close_price
        """, (company_id, today, price))
    conn.commit()

def fetch_price_rapidapi(ticker, api_key):
    """Fetch price from RapidAPI (sparior/SteadyAPI)"""
    # Ensure .LG suffix for NGX
    symbol = f"{ticker}.LG" if not ticker.endswith('.LG') else ticker
    
    # Endpoint for SteadyAPI / Yahoo Finance 15
    url = f"https://yahoo-finance15.p.rapidapi.com/api/yahoo/qu/quote/{symbol}"
    
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "yahoo-finance15.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 429:
            logger.error("🛑 RapidAPI Rate Limit Exceeded!")
            return "RATE_LIMIT"
            
        if response.status_code != 200:
            logger.error(f"❌ API Error {response.status_code} for {symbol}")
            return None

        try:
            data = response.json()
        except ValueError:
            logger.error(f"Invalid JSON response for {symbol}: {response.text[:200]}...")
            return None
        
        # Parsing logic for SteadyAPI
        price = None
        
        if isinstance(data, list) and len(data) > 0:
            item = data[0]
            price = item.get('regularMarketPrice') or item.get('price')
            
        elif isinstance(data, dict):
            # Check for the 'body' wrapper common in some versions of this API
            body = data.get('body', {})
            if isinstance(body, list) and len(body) > 0:
                price = body[0].get('regularMarketPrice') or body[0].get('price')
            elif isinstance(body, dict):
                price = body.get('regularMarketPrice') or body.get('price')
            else:
                price = data.get('regularMarketPrice') or data.get('price')

        if price is not None:
            try:
                if isinstance(price, str):
                    return float(price.replace(',', ''))
                return float(price)
            except (ValueError, TypeError):
                logger.error(f"Could not convert price '{price}' to float for {symbol}")
                return None
        
        logger.warning(f"❓ Price not found in JSON for {symbol}. Response: {str(data)[:200]}...")
        return None
        
    except Exception as e:
        logger.error(f"API Error for {symbol}: {e}")
        return None

def main():
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        logger.error("❌ RAPIDAPI_KEY not found in environment variables")
        sys.exit(1)
        
    logger.info("Starting RapidAPI scraper...")
    conn = get_db_connection()
    companies = get_companies(conn)
    logger.info(f"Found {len(companies)} active companies to update")
    
    success_count = 0
    error_count = 0
    
    for company in companies:
        ticker = company['ticker']
        result = fetch_price_rapidapi(ticker, api_key)
        
        if result == "RATE_LIMIT":
            logger.error("Stopping script due to rate limit.")
            break
            
        if result:
            update_price(conn, company['id'], result)
            logger.info(f"✅ {ticker}: ₦{result:,.2f}")
            success_count += 1
        else:
            logger.warning(f"⚠️ No data/price for {ticker}")
            error_count += 1
            
        # Rate limit protection (conservative 2 seconds)
        time.sleep(2)
            
    conn.close()
    logger.info(f"Summary: {success_count} updated, {error_count} failed")

if __name__ == "__main__":
    main()