import pdfplumber

pdf_path = "../GAINERS AND PRICE LIST FOR 04-05-2026/GAINERS AND LOSERS FOR 04-05-2026.pdf"
try:
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if "Losers for Equities" in text:
                print("Found Losers Section:")
                print(text[:1000])
except Exception as e:
    print(f"Error: {e}")
