"""
EPM — SQLAlchemy ORM Models.
Maps to the existing estate_portfolio Postgres schema (init_db.sql).
Phase 2A additions: users table (required for auth).
Phase 2B additions: status columns on holdings/transactions, new tables.
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ─── Users (Phase 2A — new table added via Alembic migration 001) ─────────────

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="readonly")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


# ─── Registrars (existing) ─────────────────────────────────────────────────────

class Registrar(Base):
    __tablename__ = "registrars"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    response_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    companies: Mapped[list["Company"]] = relationship("Company", back_populates="registrar")
    requirements: Mapped[list["RegistrarRequirement"]] = relationship("RegistrarRequirement", back_populates="registrar", cascade="all, delete-orphan")
    contact_fields: Mapped[list["RegistrarContactField"]] = relationship("RegistrarContactField", back_populates="registrar", cascade="all, delete-orphan", order_by="RegistrarContactField.sort_order")


class RegistrarContactField(Base):
    __tablename__ = "registrar_contact_fields"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    registrar_id: Mapped[int] = mapped_column(Integer, ForeignKey("registrars.id", ondelete="CASCADE"), nullable=False, index=True)
    field_type: Mapped[str] = mapped_column(String(20), nullable=False)
    field_value: Mapped[str] = mapped_column(Text, nullable=False)
    label: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    registrar: Mapped["Registrar"] = relationship("Registrar", back_populates="contact_fields")


# ─── Companies (existing) ──────────────────────────────────────────────────────

class Company(Base):
    __tablename__ = "companies"
    __table_args__ = (
        CheckConstraint("status IN ('listed','delisted','defunct','merged','uncertain','active','inactive')", name="companies_status_check"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    ticker: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    sector: Mapped[str | None] = mapped_column(String(100))
    isin: Mapped[str | None] = mapped_column(String(12))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="listed")
    market_cap: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    outstanding_shares: Mapped[int | None] = mapped_column(BigInteger)
    date_listed: Mapped[datetime | None] = mapped_column(Date)
    date_delisted: Mapped[datetime | None] = mapped_column(Date)
    registrar_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("registrars.id"))
    current_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    last_price_update: Mapped[datetime | None] = mapped_column(DateTime)
    notes: Mapped[str | None] = mapped_column(Text)
    
    # Phase 2B columns
    obsidian_slug: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    obsidian_imported: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    registrar: Mapped["Registrar | None"] = relationship("Registrar", back_populates="companies")
    holdings: Mapped[list["Holding"]] = relationship("Holding", back_populates="company")
    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="company")
    dividends: Mapped[list["Dividend"]] = relationship("Dividend", back_populates="company")
    registrar_documents: Mapped[list["RegistrarDocument"]] = relationship("RegistrarDocument", back_populates="company")


# ─── Holdings (existing + Phase 2B: status column added via migration 002) ────

class Holding(Base):
    __tablename__ = "holdings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    num_shares: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    average_cost_basis: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total_cost: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    current_value: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    unrealized_gain_loss: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    certificate_number: Mapped[str | None] = mapped_column(String(100))
    allocation_notes: Mapped[str | None] = mapped_column(Text)
    
    # Phase 2B columns
    holding_type: Mapped[str] = mapped_column(String(20), server_default="active", nullable=False)
    cost_basis_override: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    purchase_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    obsidian_imported: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    obsidian_last_synced: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    company: Mapped["Company"] = relationship("Company", back_populates="holdings")
    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="holding")
    claim_records: Mapped[list["ClaimRecord"]] = relationship("ClaimRecord", back_populates="holding", cascade="all, delete-orphan")


# ─── Claim Records (Phase 2B) ──────────────────────────────────────────────────

class ClaimRecord(Base):
    __tablename__ = "claim_records"
    __table_args__ = (
        CheckConstraint("claim_status IN ('pending','approved','rejected','partially_paid','paid','lapsed')", name="chk_claim_status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    holding_id: Mapped[int] = mapped_column(Integer, ForeignKey("holdings.id", ondelete="CASCADE"), nullable=False, index=True)

    claim_reference: Mapped[str | None] = mapped_column(String(100))
    claim_authority: Mapped[str | None] = mapped_column(String(100))
    claim_type: Mapped[str] = mapped_column(String(50), nullable=False, default="liquidation")

    date_filed: Mapped[datetime | None] = mapped_column(Date)
    date_acknowledged: Mapped[datetime | None] = mapped_column(Date)
    deadline_date: Mapped[datetime | None] = mapped_column(Date)

    claim_status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending", index=True)
    expected_payout: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    actual_payout: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    payout_date: Mapped[datetime | None] = mapped_column(Date)

    notes: Mapped[str | None] = mapped_column(Text)
    documents_reference: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    holding: Mapped["Holding"] = relationship("Holding", back_populates="claim_records")


# ─── Obsidian Sync Log (Phase 2B) ──────────────────────────────────────────────

class ObsidianSyncLog(Base):
    __tablename__ = "obsidian_sync_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    run_by: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"))
    vault_path: Mapped[str] = mapped_column(Text, nullable=False)
    
    companies_new: Mapped[int] = mapped_column(Integer, default=0)
    companies_skip: Mapped[int] = mapped_column(Integer, default=0)
    holdings_new: Mapped[int] = mapped_column(Integer, default=0)
    holdings_skip: Mapped[int] = mapped_column(Integer, default=0)
    dividends_new: Mapped[int] = mapped_column(Integer, default=0)
    dividends_skip: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[int] = mapped_column(Integer, default=0)
    
    error_details: Mapped[dict | list | None] = mapped_column(JSONB, server_default='[]')
    run_mode: Mapped[str] = mapped_column(String(20), default="manual")

    user: Mapped["User | None"] = relationship("User")


# ─── Transactions (existing + Phase 2B columns) ────────────────────────────────

class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint(
            "transaction_type IN ('buy','sell','dividend','stock_split','bonus_issue','rights_issue')",
            name="chk_transaction_type",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    holding_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("holdings.id"))
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    transaction_type: Mapped[str] = mapped_column(String(20), nullable=False)
    transaction_date: Mapped[datetime] = mapped_column(Date, nullable=False, index=True)
    settlement_date: Mapped[datetime | None] = mapped_column(Date)
    num_shares: Mapped[Decimal | None] = mapped_column(Numeric(15, 4))
    price_per_share: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    gross_amount: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    fees: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))
    net_amount: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    broker: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)


    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    company: Mapped["Company"] = relationship("Company", back_populates="transactions")
    holding: Mapped["Holding | None"] = relationship("Holding", back_populates="transactions")


# ─── Dividends (existing) ──────────────────────────────────────────────────────

class Dividend(Base):
    __tablename__ = "dividends"
    __table_args__ = (
        CheckConstraint(
            "status IN ('declared','pending','paid','cancelled')",
            name="chk_dividend_status",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    transaction_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("transactions.id"))
    declaration_date: Mapped[datetime | None] = mapped_column(Date)
    ex_dividend_date: Mapped[datetime | None] = mapped_column(Date)
    payment_date: Mapped[datetime | None] = mapped_column(Date, index=True)
    amount_per_share: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    shares_held: Mapped[Decimal | None] = mapped_column(Numeric(15, 4))
    gross_amount: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    tax_withheld: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    net_amount: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    payment_method: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), default="declared")
    notes: Mapped[str | None] = mapped_column(Text)
    
    # Needs to match import script (Dividend pass) if any Phase 2B changes apply here.
    # The script uses dividend_type, payment_status, source, obsidian_imported.
    # dividend_type, payment_status are different columns than status?
    # Let me check the script spec D.3:
    # dividend_type=..., payment_status=..., source="obsidian_import", obsidian_imported=True
    # I should add these columns to Dividend!

    dividend_type: Mapped[str] = mapped_column(String(50), default="final")
    payment_status: Mapped[str] = mapped_column(String(30), default="paid")
    source: Mapped[str] = mapped_column(String(50), default="manual")
    obsidian_imported: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    company: Mapped["Company"] = relationship("Company", back_populates="dividends")
    # Actually, the D.3 script does `holding_id=holding.id` on Dividend.
    holding_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("holdings.id"))


# ─── Price History (existing) ──────────────────────────────────────────────────

class PriceHistory(Base):
    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False)
    price_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    open_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    high_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    low_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    close_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    volume: Mapped[int | None] = mapped_column(BigInteger)
    source: Mapped[str] = mapped_column(String(50), default="manual")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    company: Mapped["Company"] = relationship("Company")


# ─── Price Audit (Phase 3A) ───────────────────────────────────────────────────

class PriceAudit(Base):
    __tablename__ = "price_audits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    old_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    new_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(Date, nullable=False, index=True)
    changed_by: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="manual")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    company: Mapped["Company"] = relationship("Company")
    user: Mapped["User | None"] = relationship("User")


# ─── Registrar Requirements (Phase 3B) ──────────────────────────────────────────

class RegistrarRequirement(Base):
    __tablename__ = "registrar_requirements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    registrar_id: Mapped[int] = mapped_column(Integer, ForeignKey("registrars.id", ondelete="CASCADE"), nullable=False, index=True)
    task_name: Mapped[str] = mapped_column(String(200), nullable=False)
    document_title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    registrar: Mapped["Registrar"] = relationship("Registrar", back_populates="requirements")
    documents: Mapped[list["RegistrarDocument"]] = relationship("RegistrarDocument", back_populates="requirement", cascade="all, delete-orphan")


# ─── Registrar Documents (Phase 3B) ───────────────────────────────────────────

class RegistrarDocument(Base):
    __tablename__ = "registrar_documents"
    __table_args__ = (
        CheckConstraint("status IN ('pending','submitted','completed','rejected')", name="chk_registrar_document_status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    registrar_requirement_id: Mapped[int] = mapped_column(Integer, ForeignKey("registrar_requirements.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("companies.id"), index=True)
    
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False, default='application/octet-stream')
    
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    notes: Mapped[str | None] = mapped_column(Text)
    
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    uploaded_by: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    requirement: Mapped["RegistrarRequirement"] = relationship("RegistrarRequirement", back_populates="documents")
    company: Mapped["Company | None"] = relationship("Company", back_populates="registrar_documents")
    uploader: Mapped["User | None"] = relationship("User")


# ─── Checklist Runs (Phase 3C — F-TD-001) ──────────────────────────────────────

class ChecklistRun(Base):
    __tablename__ = "checklist_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    admin_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    results_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    signoff_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    admin: Mapped["User"] = relationship("User")

