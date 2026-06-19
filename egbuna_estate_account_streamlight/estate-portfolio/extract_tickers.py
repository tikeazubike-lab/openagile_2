import pdfplumber
import sys

def extract(pdf_path):
    tickers = set()
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if not table or len(table) < 2:
                    continue
                header = [(str(cell) or "").strip().upper() for cell in table[0]]
                symbol_idx = next((i for i, h in enumerate(header) if h in ("COMPANY", "SYMBOL", "TICKER", "CODE")), None)
                if symbol_idx is None:
                    continue
                for row in table[1:]:
                    if not row or len(row) <= symbol_idx:
                        continue
                    ticker = (str(row[symbol_idx]) or "").strip().upper()
                    if ticker and ticker != "COMPANY" and len(ticker) > 1 and ticker != "S/N":
                        tickers.add(ticker)
    
    print("NGX_COMPANIES = [")
    for t in sorted(tickers):
        print(f'    ("{t}", "{t}", "Unknown", "listed"),')
    print("]")

if __name__ == "__main__":
    extract(sys.argv[1])
