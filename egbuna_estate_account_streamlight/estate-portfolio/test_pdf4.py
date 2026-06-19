import pdfplumber

pdf_path = "../DAILY SUMMARY FOR 04-05-2026.pdf"
try:
    with pdfplumber.open(pdf_path) as pdf:
        print(pdf.pages[0].extract_text()[:1000])
except Exception as e:
    print(f"Error: {e}")
