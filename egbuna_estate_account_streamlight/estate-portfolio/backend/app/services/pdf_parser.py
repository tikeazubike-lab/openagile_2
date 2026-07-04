import re
import tempfile
import os

import pdfplumber


def parse_ngx_companies_pdf(file_content: bytes) -> list[dict]:
    """
    Parse NGX Daily Official List PDF and extract company records.

    Returns list of dicts with keys: ticker, name, sector.
    The PDF format groups equities under sector headers (all-caps lines).
    Data rows start with a serial number and contain company name + ticker.
    """
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(file_content)
        tmp_path = tmp.name

    companies = []
    current_sector = None

    try:
        with pdfplumber.open(tmp_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue

                for line in text.split('\n'):
                    line = line.strip()
                    if not line:
                        continue

                    parts = line.split()

                    # Sector header: all-caps, not starting with digit, short
                    if (
                        parts
                        and not parts[0].isdigit()
                        and line.isupper()
                        and len(parts) <= 4
                    ):
                        current_sector = line.title()
                        continue

                    # Data row: starts with serial number (digit)
                    if len(parts) >= 4 and parts[0].isdigit():
                        symbol_index = -1
                        for i in range(len(parts) - 1, 0, -1):
                            if re.search(r'[A-Za-z]', parts[i]):
                                symbol_index = i
                                break

                        if symbol_index == -1 or symbol_index == len(parts) - 1:
                            continue

                        text_parts = parts[1:symbol_index + 1]
                        potential_ticker = text_parts[-1].upper()
                        company_name = ' '.join(text_parts[:-1])
                        company_name = re.sub(r'\s+', ' ', company_name).strip()

                        if company_name and potential_ticker:
                            companies.append({
                                "ticker": potential_ticker,
                                "name": company_name,
                                "sector": current_sector,
                            })
    finally:
        os.unlink(tmp_path)

    return companies
