#!/usr/bin/env python3
"""
Yahoo Finance Price Scraper for NGX Stocks
"""

import yfinance as yf
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
        cur.execute("SELECT id, ticker, name FROM companies WHERE deleted_at IS NULL AND status = 'listed'")
        return cur.fetchall()

def update_price(conn, company_id, price, price_date):
    """Update company current price and insert history"""
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
            VALUES (%s, %s, %s, 'yfinance')
            ON CONFLICT (company_id, price_date) 
            DO UPDATE SET close_price = EXCLUDED.close_price
        """, (company_id, price_date, price))
    conn.commit()

def main():
    logger.info("Starting Yahoo Finance scraper...")
    conn = get_db_connection()
    companies = get_companies(conn)
    logger.info(f"Found {len(companies)} companies to update")
    
    # Create a custom session to bypass Yahoo's bot detection
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })
    
    success_count = 0
    error_count = 0
    
    for company in companies:
        ticker = company['ticker']
        # Yahoo Finance expects NGX stocks to have .LG suffix
        yf_ticker = f"{ticker}.LG" if not ticker.endswith('.LG') else ticker
        
        try:
            logger.info(f"Fetching {yf_ticker}...")
            # Pass the custom session
            stock = yf.Ticker(yf_ticker, session=session)
            
            # Get today's data
            hist = stock.history(period="1d")
            
            if not hist.empty:
                current_price = float(hist['Close'].iloc[-1])
                price_date = hist.index[-1].date()
                
                update_price(conn, company['id'], current_price, price_date)
                logger.info(f"✅ {ticker}: ₦{current_price:,.2f}")
                success_count += 1
            else:
                logger.warning(f"⚠️ No data found for {yf_ticker}")
                error_count += 1
                
            # Be nice to the API
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"❌ Error fetching {ticker}: {e}")
            error_count += 1
            
    conn.close()
    logger.info(f"Summary: {success_count} updated, {error_count} failed")

if __name__ == "__main__":
    main()
