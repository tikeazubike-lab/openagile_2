import pdfplumber

pdf_path = "../GAINERS AND PRICE LIST FOR 04-05-2026/PRICES_LIST2.pdf"
try:
    with pdfplumber.open(pdf_path) as pdf:
        table_settings = {
            "vertical_strategy": "text",
            "horizontal_strategy": "text",
        }
        tables = pdf.pages[0].extract_tables(table_settings)
        for j, table in enumerate(tables):
            print(f"Table {j+1}: length {len(table)}")
            if len(table) > 1:
                print(table[0])
                print(table[1])
                print(table[-1])
            break
except Exception as e:
    print(f"Error: {e}")
