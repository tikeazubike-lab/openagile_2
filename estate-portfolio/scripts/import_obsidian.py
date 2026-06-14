#!/usr/bin/env python3
"""
Import data from Obsidian vault markdown files
Usage: python scripts/import_obsidian.py /path/to/vault
"""

import os
import re
import sys
from pathlib import Path
import psycopg2
from datetime import datetime
import frontmatter

def clean_value(value):
    """Clean value: remove wiki links and currency symbols"""
    if not value:
        return None
    
    # Handle nested lists (e.g. unquoted [[wiki links]] in YAML are parsed as lists of lists)
    while isinstance(value, list):
        value = value[0] if value else ""
        
    if isinstance(value, str):
        # Remove wiki links: [[Unity Registrars]] -> Unity Registrars
        value = re.sub(r'\[\[(.+?)\]\]', r'\1', value)
        # Remove currency symbols: ₦25.50 -> 25.50
        value = re.sub(r'[₦,]', '', value)
        return value.strip()
    return value

def extract_field_regex(content, field_name):
    """Extract field value from markdown using regex (fallback)"""
    pattern = rf'^-\s*{field_name}:\s*(.+)$'
    if match := re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
        return clean_value(match.group(1))
    return None

def extract_section(content, section_name):
    """Extract markdown section by heading"""
    pattern = rf'^#+ {section_name}\s*$(.*?)(?=^#|\Z)'
    if match := re.search(pattern, content, re.MULTILINE | re.DOTALL):
        return match.group(1).strip()
    return None

def import_obsidian_vault(vault_path, db_conn):
    """Parse Obsidian files and import to database"""
    cursor = db_conn.cursor()
    
    companies = []
    holdings = []
    dividends = []
    
    # Parse markdown files
    # Check explicitly in Companies/ directory as per structure
    search_path = Path(vault_path)
    companies_path = search_path / "Companies"
    
    print(f"Searching for files in: {companies_path.absolute()}")
    
    if companies_path.exists():
        md_files = list(companies_path.glob("*.md"))
    else:
        # Fallback to root if Companies folder doesn't exist
        print(f"Companies folder not found, searching root: {search_path.absolute()}")
        md_files = list(search_path.glob("*.md"))
    
    print(f"Found {len(md_files)} markdown files")
    
    for md_file in md_files:
        try:
            post = frontmatter.load(md_file)
            metadata = post.metadata
            content = post.content
            
            # Field mapping (Obsidian Frontmatter -> Database)
            ticker = metadata.get('ticker')
            if ticker is None:
                ticker = extract_field_regex(content, 'Ticker')
            
            if not ticker:
                continue
            
            ticker = str(ticker).upper()[:20]
            name = metadata.get('name') or md_file.stem
            
            sector = metadata.get('sector')
            if sector is None:
                sector = extract_field_regex(content, 'Sector')
                
            registrar = metadata.get('registrar')
            if registrar is None:
                registrar = extract_field_regex(content, 'Registrar')
            registrar = clean_value(registrar)
            
            isin = metadata.get('isin')
            if isin is None:
                isin = extract_field_regex(content, 'ISIN')
            
            company = {
                'name': name,
                'ticker': ticker,
                'sector': clean_value(sector),
                'registrar': registrar,
                'isin': clean_value(isin),
            }
            companies.append(company)
            
            # Holdings
            num_shares = metadata.get('shares_held')
            if num_shares is None:
                num_shares = extract_field_regex(content, 'Shares')
                
            purchase_price = metadata.get('avg_buy_price')
            if purchase_price is None:
                purchase_price = extract_field_regex(content, 'Purchase Price')
                
            purchase_date = metadata.get('purchase_date')
            if purchase_date is None:
                purchase_date = extract_field_regex(content, 'Purchase Date')
            
            if num_shares is not None and purchase_price is not None:
                try:
                    holdings.append({
                        'ticker': ticker,
                        'num_shares': float(num_shares),
                        'purchase_price': float(purchase_price),
                        'purchase_date': purchase_date or datetime.now().date()
                    })
                except (ValueError, TypeError):
                    pass
            
            # Dividends
            div_section = extract_section(content, 'Dividends')
            if div_section:
                for line in div_section.split('\n'):
                    if match := re.search(r'(\d{4}-\d{2}-\d{2}):\s*₦?([\d.]+)', line):
                        dividends.append({
                            'ticker': ticker,
                            'payment_date': match.group(1),
                            'amount_per_share': float(match.group(2))
                        })
        except Exception as e:
            print(f"Error parsing {md_file}: {e}")
    
    print(f"Parsed: {len(companies)} companies, {len(holdings)} holdings, {len(dividends)} dividends")
    
    # Import to database
    # 1. Registrars
    registrars = set(c['registrar'] for c in companies if c['registrar'])
    for reg in registrars:
        cursor.execute(
            "INSERT INTO registrars (name) VALUES (%s) ON CONFLICT DO NOTHING",
            (reg,)
        )
    
    # 2. Companies
    for company in companies:
        cursor.execute("SELECT id FROM registrars WHERE name = %s", (company['registrar'],))
        result = cursor.fetchone()
        registrar_id = result[0] if result and company['registrar'] else None
        
        cursor.execute("""
            INSERT INTO companies (name, ticker, sector, isin, registrar_id, status)
            VALUES (%s, %s, %s, %s, %s, 'listed')
            ON CONFLICT (ticker) DO UPDATE SET
                name = EXCLUDED.name,
                sector = EXCLUDED.sector
        """, (company['name'], company['ticker'], company['sector'], company.get('isin'), registrar_id))
    
    # 3. Holdings & Transactions
    for holding in holdings:
        cursor.execute("SELECT id FROM companies WHERE ticker = %s", (holding['ticker'],))
        result = cursor.fetchone()
        if not result:
            continue
        company_id = result[0]
        
        total_cost = holding['num_shares'] * holding['purchase_price']
        
        cursor.execute("""
            INSERT INTO holdings (
                company_id, num_shares, average_cost_basis, total_cost
            ) VALUES (%s, %s, %s, %s)
        """, (company_id, holding['num_shares'], holding['purchase_price'], total_cost))
        
        cursor.execute("""
            INSERT INTO transactions (
                company_id, transaction_type, transaction_date,
                num_shares, price_per_share, gross_amount, net_amount
            ) VALUES (%s, 'buy', %s, %s, %s, %s, %s)
        """, (company_id, holding['purchase_date'], holding['num_shares'],
              holding['purchase_price'], total_cost, total_cost))
    
    # 4. Dividends
    for div in dividends:
        cursor.execute("SELECT id FROM companies WHERE ticker = %s", (div['ticker'],))
        result = cursor.fetchone()
        if not result:
            continue
        company_id = result[0]
        
        cursor.execute("""
            INSERT INTO dividends (
                company_id, payment_date, amount_per_share, status
            ) VALUES (%s, %s, %s, 'paid')
        """, (company_id, div['payment_date'], div['amount_per_share']))
    
    db_conn.commit()
    print(f"✅ Import complete!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_obsidian.py /path/to/vault")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    
    # Explicitly use all DB environment variables from the container's environment
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        database=os.getenv("DB_NAME", "estate_portfolio"),
        user=os.getenv("DB_USER", "portfolio_user"),
        password=os.getenv("DB_PASSWORD")
    )
    
    import_obsidian_vault(vault_path, conn)
    conn.close()
