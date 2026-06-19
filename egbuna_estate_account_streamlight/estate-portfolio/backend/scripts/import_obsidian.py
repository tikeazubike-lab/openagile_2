import sys
import os
import glob
import re
from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal
import argparse

import frontmatter

# Import from app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models import Company, Holding, Dividend, User, ObsidianSyncLog
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

sync_url = settings.DATABASE_URL.replace("+asyncpg", "")
engine = create_engine(sync_url)
SessionLocal = sessionmaker(bind=engine)

HOLDING_TYPE_MAP = {
    "listed":    ("active", False),
    "merged":    ("active", False),
    "delisted":  ("claim",  True),
    "defunct":   ("claim",  True),
    "uncertain": ("claim",  True),
}

def extract_ticker_from_link(link_str: str) -> str | None:
    if not link_str:
        return None
    link_str = str(link_str)
    match = re.search(r'\[\[(.*?)\]\]', link_str)
    if match:
        return match.group(1).strip()
    return link_str.strip()

class SyncLog:
    def __init__(self):
        self.companies_new = 0
        self.companies_skip = 0
        self.holdings_new = 0
        self.holdings_skip = 0
        self.dividends_new = 0
        self.dividends_skip = 0
        self.errors = []

    def error(self, path: str, msg: str):
        self.errors.append({"file": Path(path).name, "message": msg})


def run_import(vault_path: str, dry_run: bool = False) -> ObsidianSyncLog | None:
    log = SyncLog()
    db = SessionLocal()

    try:
        # ── PASS 1: Companies ──────────────────────────────────────────────
        companies_path = os.path.join(vault_path, "Companies", "*.md")
        for md_file in glob.glob(companies_path):
            try:
                fm = frontmatter.load(md_file)
            except Exception as e:
                log.error(md_file, f"Parse error: {e}")
                continue

            ticker = fm.get("ticker")
            if not ticker:
                log.error(md_file, "Missing ticker field")
                continue
            ticker = str(ticker).strip()

            slug = Path(md_file).stem
            obsidian_status = str(fm.get("status", "uncertain")).lower()

            existing = db.query(Company).filter_by(ticker=ticker).first()
            if existing:
                log.companies_skip += 1
                continue

            company = Company(
                ticker=ticker,
                name=str(fm.get("name", ticker)),
                sector=str(fm.get("sector")) if fm.get("sector") else None,
                status=obsidian_status,
                obsidian_slug=slug,
                obsidian_imported=True,
            )
            if not dry_run:
                db.add(company)
            log.companies_new += 1

        if not dry_run:
            db.flush()

        # ── PASS 2: Holdings ───────────────────────────────────────────────
        admin_user = db.query(User).filter_by(role="admin").first()

        for md_file in glob.glob(companies_path):
            try:
                fm = frontmatter.load(md_file)
            except Exception:
                continue
            
            ticker = str(fm.get("ticker", "")).strip()
            if not ticker:
                continue

            company = db.query(Company).filter_by(ticker=ticker).first()
            if not company:
                continue

            obsidian_status = str(fm.get("status", "uncertain")).lower()
            holding_type, is_claim = HOLDING_TYPE_MAP.get(obsidian_status, ("claim", True))
            shares = Decimal(str(fm.get("shares_held", 0)))
            avg_price = Decimal(str(fm.get("avg_buy_price", 0)))

            existing_holding = db.query(Holding).filter_by(company_id=company.id).first()
            if existing_holding:
                log.holdings_skip += 1
                continue

            total_cost = shares * avg_price

            holding = Holding(
                company_id=company.id,
                # Admin user assumes user_id = admin_user.id. Since Holding doesn't explicitly store user_id
                # wait, let me check models.py: Holding doesn't have user_id, it is a global portfolio!
                # Wait, Phase 2A added Users but Holding doesn't have user_id. Let me confirm.
                # models.py says: id, company_id, num_shares, average_cost_basis, total_cost, ...
                num_shares=shares,
                average_cost_basis=Decimal("0.00") if is_claim else avg_price,
                total_cost=total_cost,
                holding_type=holding_type,
                cost_basis_override=Decimal("0.00") if is_claim else None,
                obsidian_imported=True,
                obsidian_last_synced=datetime.now(timezone.utc),
            )
            if not dry_run:
                db.add(holding)
            log.holdings_new += 1

        if not dry_run:
            db.flush()

        # ── PASS 3: Dividends ──────────────────────────────────────────────
        dividends_path = os.path.join(vault_path, "Dividends", "*.md")
        for md_file in glob.glob(dividends_path):
            try:
                fm = frontmatter.load(md_file)
            except Exception as e:
                log.error(md_file, f"Parse error: {e}")
                continue

            company_ref = fm.get("company")
            ticker = extract_ticker_from_link(company_ref)
            if not ticker:
                log.error(md_file, "Missing company link")
                continue

            company = db.query(Company).filter_by(ticker=ticker).first()
            if not company:
                log.error(md_file, f"Company not found: {ticker}")
                continue

            holding = db.query(Holding).filter_by(company_id=company.id).first()
            if not holding:
                log.dividends_skip += 1
                continue

            payment_date_val = fm.get("payment_date")
            try:
                if isinstance(payment_date_val, str):
                    payment_date = datetime.strptime(payment_date_val, "%Y-%m-%d").date()
                else:
                    payment_date = payment_date_val
            except Exception:
                log.error(md_file, f"Invalid date format: {payment_date_val}")
                continue

            existing_div = db.query(Dividend).filter_by(
                company_id=company.id,
                payment_date=payment_date,
            ).first()
            if existing_div:
                log.dividends_skip += 1
                continue

            gross = Decimal(str(fm.get("gross_amount", "0.00")))
            net = Decimal(str(fm.get("net_amount", "0.00")))
            tax = Decimal(str(fm.get("withholding_tax", "0.00")))
            
            # Use shares from holding by default or provide 1 to avoid ZeroDivision
            amount_per_share = net / holding.num_shares if holding.num_shares > 0 else Decimal("0.00")

            dividend = Dividend(
                company_id=company.id,
                payment_date=payment_date,
                amount_per_share=amount_per_share,
                dividend_type=str(fm.get("dividend_type", "final")),
                gross_amount=gross,
                net_amount=net,
                tax_withheld=tax,
                payment_status=str(fm.get("payment_status", "paid")),
                source="obsidian_import",
                obsidian_imported=True,
            )
            if not dry_run:
                db.add(dividend)
            log.dividends_new += 1

        # ── COMMIT & LOG ───────────────────────────────────────────────────
        sync_log_record = None
        if not dry_run:
            db.commit()
            sync_log_record = ObsidianSyncLog(
                vault_path=vault_path,
                companies_new=log.companies_new,
                companies_skip=log.companies_skip,
                holdings_new=log.holdings_new,
                holdings_skip=log.holdings_skip,
                dividends_new=log.dividends_new,
                dividends_skip=log.dividends_skip,
                errors=len(log.errors),
                error_details=log.errors,
            )
            db.add(sync_log_record)
            db.commit()

        print_summary(log, dry_run, vault_path)
        return sync_log_record

    finally:
        db.close()


def print_summary(log: SyncLog, dry_run: bool, vault_path: str):
    header = "DRY RUN (no changes written)" if dry_run else "LIVE RUN"
    print(f"\nEPM Obsidian Import — {header}")
    print("====================================================")
    print(f"Vault path:   {vault_path}")
    print(f"Companies:    {log.companies_new} new  |  {log.companies_skip} skip")
    print(f"Holdings:     {log.holdings_new} new  |  {log.holdings_skip} skip")
    print(f"Dividends:    {log.dividends_new} new  |  {log.dividends_skip} skip")
    print(f"Errors:       {len(log.errors)}")
    for err in log.errors:
        print(f"  → {err['file']}: {err['message']}")
    
    if dry_run:
        print("\nRun without --dry-run to apply these changes.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import Obsidian vault records.")
    parser.add_argument("--vault-path", required=True, help="Path to Obsidian vault directory")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without committing")
    args = parser.parse_args()

    run_import(args.vault_path, args.dry_run)
