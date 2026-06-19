import pdfplumber

pdf_path = "../DAILY SUMMARY FOR 04-05-2026.pdf"
try:
    with pdfplumber.open(pdf_path) as pdf:
        tables = pdf.pages[0].extract_tables()
        for j, table in enumerate(tables):
            print(f"Table {j+1}: length {len(table)}")
except Exception as e:
    print(f"Error: {e}")
