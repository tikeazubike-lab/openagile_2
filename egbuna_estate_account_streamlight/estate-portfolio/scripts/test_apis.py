import requests
import os
import yfinance as yf
import sys

def test_rapidapi():
    print("\n--- Testing RapidAPI ---")
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        print("❌ RAPIDAPI_KEY not found!")
        return

    # Using the host for 'sparior/yahoo-finance15' as per your confirmation
    # Host often matches the URL domain.
    host = "yahoo-finance15.p.rapidapi.com" 
    url = f"https://{host}/api/v1/markets/quote"
    
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": host
    }
    params = {"ticker": "MTNN.LG"}

    print(f"Requesting: {url}")
    print(f"Headers: X-RapidAPI-Key=***{api_key[-4:] if api_key else 'None'}, X-RapidAPI-Host={host}")

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body Preview: {response.text[:500]}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ JSON Decode Success")
                print(f"Keys: {data.keys()}")
            except:
                print("❌ JSON Decode Failed")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_rapidapi()
