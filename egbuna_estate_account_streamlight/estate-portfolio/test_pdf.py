import pdfplumber

pdf_path = "../GAINERS AND PRICE LIST FOR 04-05-2026/PRICES_LIST2.pdf"
try:
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            print(f"Page {i+1} - found {len(tables)} tables")
            for j, table in enumerate(tables):
                if not table: continue
                print(f"  Table {j+1} - Row 0: {table[0]}")
                print(f"  Table {j+1} - Row 1: {table[1] if len(table) > 1 else 'None'}")
                print(f"  Table {j+1} - Row 2: {table[2] if len(table) > 2 else 'None'}")
except Exception as e:
    print(f"Error: {e}")
