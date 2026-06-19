import pdfplumber
import re

pdf_path = "../DAILY SUMMARY FOR 04-05-2026.pdf"

prices = {}

try:
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text: continue
            
            lines = text.split('\n')
            
            # State machine to find headers
            ticker_idx = -1
            close_idx = -1
            
            for line in lines:
                line = line.strip()
                if not line: continue
                
                parts = line.split()
                
                # Check for header row
                if "S/N" in parts and "COMPANY" in parts and "CLOSE" in parts:
                    try:
                        # Find indices based on parts
                        ticker_idx = parts.index("COMPANY")
                        # For equities, there are PCLOSE, OCLOSE, CLOSE
                        # We want the LAST "CLOSE" before "CHANGE" or just the index of "CLOSE"
                        # Wait, OCLOSE might be attached or separate.
                        # Let's just find the index of "CLOSE"
                        # But wait, the data rows might have different number of columns if some are "-" or empty!
                        # Actually, `parts` splitting by space works perfectly for data rows because NGX always puts "-" for empty!
                        pass
                    except ValueError:
                        pass
                
                # If we have a data row: starts with digit, has enough parts
                if parts[0].isdigit() and len(parts) >= 8:
                    ticker = parts[1]
                    # We know that for NGX Daily Official List:
                    # Equities: 15 columns. Close is at index 9.
                    # ETFs: 12 columns. Close is at index 7.
                    # Bonds: 11 columns. Close is at index 7.
                    
                    if len(parts) >= 14:
                        # Equity
                        close_price = parts[9]
                    elif len(parts) >= 10:
                        # ETF / Bond
                        close_price = parts[7]
                    else:
                        continue
                        
                    # Validate ticker is uppercase alphanumeric
                    if re.match(r'^[A-Z0-9]+$', ticker):
                        prices[ticker] = close_price
                        
    print(f"Extracted {len(prices)} prices.")
    for t, p in list(prices.items())[:5]:
        print(f"{t}: {p}")
except Exception as e:
    print(f"Error: {e}")
