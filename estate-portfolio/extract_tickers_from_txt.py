import sys

def parse_text(file_path):
    tickers = set()
    with open(file_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            # Try to identify the ticker column (second column)
            if len(parts) >= 3 and parts[0].isdigit():
                ticker = parts[1].upper()
                if ticker.isalnum() and len(ticker) >= 2:
                    tickers.add(ticker)
    
    print("NGX_COMPANIES = [")
    for t in sorted(tickers):
        print(f'    ("{t}", "{t}", "Unknown", "listed"),')
    print("]")

if __name__ == "__main__":
    parse_text(sys.argv[1])
