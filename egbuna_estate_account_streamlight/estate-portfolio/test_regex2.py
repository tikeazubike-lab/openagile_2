import re

text = """
    PRICES FOR EQUITY SECURITIES TRADED ON 04/05/2026
     S/N COMPANY         PCLOSE OOPEN        OPEN      HIGH     LOW %SPREAD OCLOSE      CLOSE CHANGE      %CHANGE    TRADES      VOLUME              VALUE
      1    ABBEYBDS           6.30       -     6.30     6.00     5.85    2.50    5.90     5.90    -0.40      -6.35      288      3,358,318    19,971,321.40
      2    ABCTRANS           5.20       -     5.20        -        -       -       -     5.20        -          -      487      1,483,237      7,515,310.39
      4    ACCESSCORP       27.00    26.05    26.05    26.30    25.00    4.94   25.50    25.50    -1.50      -5.56     5,997   204,007,563 5,276,350,340.25
      7    AIRTELAFRI     3,021.30       - 3,021.30        -        -       -       - 3,021.30        -          -        3           222        737,794.80
"""

for line in text.split('\n'):
    line = line.strip()
    if not line: continue
    parts = line.split()
    if len(parts) >= 10 and parts[0].isdigit():
        ticker = parts[1]
        close_price = parts[9]
        print(f"Ticker: {ticker}, Close: {close_price}")

