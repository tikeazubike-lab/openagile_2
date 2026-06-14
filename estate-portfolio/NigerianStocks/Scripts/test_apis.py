#!/usr/bin/env python3
"""Test various data sources for Nigerian stocks"""

import requests
import json

def test_investing_com():
    """Test Investing.com"""
    url = "https://api.investing.com/api/financialdata/historical/8406"  # Nestle Nigeria
    try:
        response = requests.get(url, timeout=5)
        print(f"✓ Investing.com: Status {response.status_code}")
        if response.status_code == 200:
            print(f"  Data available: Yes")
            return True
    except Exception as e:
        print(f"✗ Investing.com: {e}")
    return False

def test_ngx_direct():
    """Test NGX website"""
    urls = [
        "https://ngxgroup.com/api/market-data/equities",
        "https://ngxgroup.com/exchange/data/",
    ]
    for url in urls:
        try:
            response = requests.get(url, timeout=5, headers={
                "User-Agent": "Mozilla/5.0"
            })
            print(f"✓ NGX {url}: Status {response.status_code}")
            if response.status_code == 200 and len(response.content) > 100:
                print(f"  Might have data")
                return True
        except Exception as e:
            print(f"✗ NGX {url}: {e}")
    return False

def test_african_markets():
    """Test African Markets"""
    url = "https://www.african-markets.com/en/stock-markets/ngse/listed-companies"
    try:
        response = requests.get(url, timeout=5, headers={
            "User-Agent": "Mozilla/5.0"
        })
        print(f"✓ African Markets: Status {response.status_code}")
        if response.status_code == 200:
            print(f"  Page accessible: Yes")
            return True
    except Exception as e:
        print(f"✗ African Markets: {e}")
    return False

def test_alpha_vantage():
    """Test Alpha Vantage (requires free API key)"""
    # Free API key needed from: https://www.alphavantage.co/support/#api-key
    print("⚠ Alpha Vantage: Requires free API key from alphavantage.co")
    print("  Limited Nigerian stock coverage")
    return False

print("Testing Nigerian Stock Data Sources...\n")
print("=" * 60)

test_ngx_direct()
print()
test_investing_com()
print()
test_african_markets()
print()
test_alpha_vantage()

print("=" * 60)
print("\nRecommendation coming based on results...")
