import pdfplumber

pdf_path = "../GAINERS AND PRICE LIST FOR 04-05-2026/PRICES_LIST2.pdf"
try:
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for j, table in enumerate(tables):
                print(f"Page {i+1} Table {j+1}: length {len(table)}")
                print(table)
                break
            break
except Exception as e:
    print(f"Error: {e}")
