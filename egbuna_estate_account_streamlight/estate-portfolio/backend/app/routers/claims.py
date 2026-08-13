import csv
import io
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from sqlalchemy.orm import selectinload
from app.deps import get_session, get_current_user, require_admin
from app.models import ClaimRecord, Holding, Company, Registrar
from app.utils.company_matcher import find_company, MATCH_THRESHOLD, AMBIGUOUS_THRESHOLD
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date, datetime, timezone
from decimal import Decimal

router = APIRouter(prefix="/api/v1/claims", tags=["Claims"])

class ClaimRecordCreate(BaseModel):
    holding_id: int
    claim_reference: Optional[str] = None
    claim_authority: Optional[str] = None
    claim_type: str = "liquidation"
    date_filed: Optional[date] = None
    date_acknowledged: Optional[date] = None
    deadline_date: Optional[date] = None
    claim_status: str = "pending"
    expected_payout: Optional[Decimal] = None
    actual_payout: Optional[Decimal] = None
    payout_date: Optional[date] = None
    notes: Optional[str] = None
    documents_reference: Optional[str] = None

class ClaimRecordUpdate(BaseModel):
    claim_reference: Optional[str] = None
    claim_authority: Optional[str] = None
    claim_type: Optional[str] = None
    date_filed: Optional[date] = None
    date_acknowledged: Optional[date] = None
    deadline_date: Optional[date] = None
    claim_status: Optional[str] = None
    expected_payout: Optional[Decimal] = None
    actual_payout: Optional[Decimal] = None
    payout_date: Optional[date] = None
    notes: Optional[str] = None
    documents_reference: Optional[str] = None


class HoldingBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    num_shares: Optional[Decimal]
    company_ticker: Optional[str]
    company_name: Optional[str]
    registrar_name: Optional[str]


class ClaimResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    holding_id: Optional[int] = None
    claim_reference: Optional[str] = None
    claim_authority: Optional[str] = None
    claim_type: str
    claim_status: str
    lifecycle_status: str = "unresolved"
    expected_payout: Optional[Decimal] = None
    actual_payout: Optional[Decimal] = None
    payout_date: Optional[date] = None
    notes: Optional[str] = None
    documents_reference: Optional[str] = None
    raw_company_name: Optional[str] = None
    holding: Optional[HoldingBrief] = None


def _envelope(data: object) -> dict:
    return {"data": data, "meta": {}, "error": None}


@router.get("")
async def get_claims(
    holding_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    lifecycle_status: Optional[str] = Query(None),
    authority: Optional[str] = Query(None),
    registrar_id: Optional[int] = Query(None),
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user)
):
    stmt = (
        select(ClaimRecord)
        .options(
            selectinload(ClaimRecord.holding)
            .selectinload(Holding.company)
            .selectinload(Company.registrar)
        )
        .where(ClaimRecord.deleted_at.is_(None))
    )
    if holding_id:
        stmt = stmt.where(ClaimRecord.holding_id == holding_id)
    if status:
        status_list = [s.strip() for s in status.split(",")]
        stmt = stmt.where(ClaimRecord.claim_status.in_(status_list))
    if lifecycle_status:
        lc_list = [s.strip() for s in lifecycle_status.split(",")]
        stmt = stmt.where(ClaimRecord.lifecycle_status.in_(lc_list))
    if authority:
        stmt = stmt.where(ClaimRecord.claim_authority == authority)
    if registrar_id:
        stmt = stmt.where(
            ClaimRecord.holding.has(
                Holding.company.has(Company.registrar_id == registrar_id)
            )
        )

    result = await session.execute(stmt)
    records = result.scalars().all()

    response_data = []
    for c in records:
        holding = c.holding
        company = holding.company if holding else None
        response_data.append({
            "id": c.id,
            "holding_id": c.holding_id,
            "claim_reference": c.claim_reference,
            "claim_authority": c.claim_authority,
            "claim_type": c.claim_type,
            "claim_status": c.claim_status,
            "lifecycle_status": c.lifecycle_status,
            "raw_company_name": c.raw_company_name,
            "expected_payout": str(c.expected_payout) if c.expected_payout else None,
            "actual_payout": str(c.actual_payout) if c.actual_payout else None,
            "payout_date": c.payout_date,
            "notes": c.notes,
            "documents_reference": c.documents_reference,
            "holding": {
                "id": holding.id if holding else None,
                "num_shares": str(holding.num_shares) if holding and holding.num_shares else None,
                "company_ticker": company.ticker if company else None,
                "company_name": company.name if company else None,
                "registrar_name": company.registrar.name if company and company.registrar else None,
            } if holding else None,
        })

    return _envelope(response_data)

@router.post("")
async def create_claim(
    claim_in: ClaimRecordCreate,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(require_admin)
):
    new_claim = ClaimRecord(**claim_in.model_dump())
    session.add(new_claim)
    await session.commit()
    await session.refresh(new_claim)
    return new_claim

@router.put("/{claim_id}")
async def update_claim(
    claim_id: int,
    claim_in: ClaimRecordUpdate,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(require_admin)
):
    result = await session.execute(select(ClaimRecord).where(ClaimRecord.id == claim_id, ClaimRecord.deleted_at.is_(None)))
    claim = result.scalar_one_or_none()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    update_data = claim_in.model_dump(exclude_unset=True)
    
    # Business rule: when claim_status -> 'paid', actual_payout must be provided
    new_status = update_data.get("claim_status", claim.claim_status)
    if new_status == "paid":
        actual = update_data.get("actual_payout", claim.actual_payout)
        if actual is None:
            raise HTTPException(status_code=400, detail="actual_payout must be provided when claim_status is 'paid'")

    for key, value in update_data.items():
        setattr(claim, key, value)

    await session.commit()
    await session.refresh(claim)
    return claim

@router.delete("/{claim_id}")
async def delete_claim(
    claim_id: int,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(require_admin)
):
    result = await session.execute(select(ClaimRecord).where(ClaimRecord.id == claim_id, ClaimRecord.deleted_at.is_(None)))
    claim = result.scalar_one_or_none()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    claim.deleted_at = datetime.now(timezone.utc)
    await session.commit()
    return {"message": "Claim deleted successfully"}


# ── CSV Upload Endpoints ─────────────────────────────────────────────────────
# Governance: HO-036 — two-phase preview/commit pattern
# Dedup key: (company_id, account_number)
# Match thresholds: MATCH_THRESHOLD=90, AMBIGUOUS_THRESHOLD=70


@router.get("/upload/template")
async def download_template(
    current_user = Depends(require_admin),
):
    """Download a CSV template for claims upload."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Account#", "Shareholder", "Company", "Operator"])
    writer.writerow(["0000012345", "EGBUNA BENJAMIN EJIKE", "Access Bank Plc", "First Registrars Ltd"])
    writer.writerow(["0000056789", "EGBUNA BENJAMIN EJIKE", "Fidelity Bank Plc", "Zenith Registrars Ltd"])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=claims_upload_template.csv",
        },
    )


class CSVRowPreview(BaseModel):
    account_number: str
    shareholder: str
    company_name_raw: str
    company_id: Optional[int] = None
    company_name_matched: Optional[str] = None
    match_score: Optional[float] = None
    match_status: str = "unmatched"  # matched | unmatched | ambiguous
    operator_raw: str
    action: str = "create"  # create | skip | error
    error: Optional[str] = None


class PreviewResponse(BaseModel):
    rows: list[CSVRowPreview]
    summary: dict


class UploadCommitPayload(BaseModel):
    rows: list[CSVRowPreview]
    confirm_unmatched: bool = False


@router.post("/upload/preview")
async def preview_upload(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    current_user = Depends(require_admin),
):
    """Parse a CSV file, fuzzy-match companies, and return a preview."""
    content = await file.read()
    text = content.decode("utf-8-sig")  # handles BOM
    reader = csv.DictReader(io.StringIO(text))

    if not reader.fieldnames or set(reader.fieldnames) != {"Account#", "Shareholder", "Company", "Operator"}:
        raise HTTPException(
            status_code=400,
            detail="CSV must have columns: Account#, Shareholder, Company, Operator",
        )

    rows: list[CSVRowPreview] = []
    matched = unmatched = duplicates_skipped = 0

    for row_num, row in enumerate(reader, start=2):
        account_number = row.get("Account#", "").strip()
        shareholder = row.get("Shareholder", "").strip()
        company_raw = row.get("Company", "").strip()
        operator_raw = row.get("Operator", "").strip()

        if not account_number or not company_raw:
            rows.append(CSVRowPreview(
                account_number=account_number,
                shareholder=shareholder,
                company_name_raw=company_raw,
                match_status="unmatched",
                operator_raw=operator_raw,
                action="error",
                error=f"Row {row_num}: missing Account# or Company",
            ))
            unmatched += 1
            continue

        # Fuzzy match company name
        company_id, matched_name, candidates = await find_company(company_raw, session)

        if company_id and not candidates:
            # Auto-match (score >= 90)
            # Check for dedup: existing claim with same (company_id, account_number)?
            dedup = await session.execute(
                select(ClaimRecord.id).where(
                    ClaimRecord.deleted_at.is_(None),
                    ClaimRecord.holding.has(
                        Holding.company.has(Company.id == company_id)
                    ),
                    ClaimRecord.claim_reference == account_number,
                )
            )
            existing_id = dedup.scalar_one_or_none()

            status = "matched"
            action = "skip" if existing_id else "create"

            rows.append(CSVRowPreview(
                account_number=account_number,
                shareholder=shareholder,
                company_name_raw=company_raw,
                company_id=company_id,
                company_name_matched=matched_name,
                match_score=90,
                match_status=status,
                operator_raw=operator_raw,
                action=action,
            ))
            if action == "skip":
                duplicates_skipped += 1
            else:
                matched += 1

        elif candidates:
            # Ambiguous (score 70–89)
            rows.append(CSVRowPreview(
                account_number=account_number,
                shareholder=shareholder,
                company_name_raw=company_raw,
                company_id=None,
                company_name_matched=candidates[0]["company_name"],
                match_score=candidates[0]["score"],
                match_status="ambiguous",
                operator_raw=operator_raw,
                action="create",  # user must confirm
            ))
            unmatched += 1

        else:
            # Unmatched (score < 70)
            rows.append(CSVRowPreview(
                account_number=account_number,
                shareholder=shareholder,
                company_name_raw=company_raw,
                match_status="unmatched",
                operator_raw=operator_raw,
                action="create",  # user must confirm
            ))
            unmatched += 1

    return _envelope({
        "rows": [r.model_dump() for r in rows],
        "summary": {
            "total_rows": len(rows),
            "matched": matched,
            "unmatched": unmatched,
            "duplicates_skipped": duplicates_skipped,
            "match_threshold": MATCH_THRESHOLD,
            "ambiguous_threshold": AMBIGUOUS_THRESHOLD,
        },
    })


@router.post("/upload/commit")
async def commit_upload(
    payload: UploadCommitPayload,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(require_admin),
):
    """Commit the previewed rows — creates claim records and holdings as needed."""
    if not payload.confirm_unmatched:
        unmatched = [r for r in payload.rows if r.match_status in ("unmatched", "ambiguous")]
        if unmatched:
            raise HTTPException(
                status_code=400,
                detail=f"{len(unmatched)} row(s) are unmatched or ambiguous. Set confirm_unmatched=true to proceed.",
            )

    created = 0
    skipped = 0
    errors: list[str] = []

    for row in payload.rows:
        if row.action == "skip":
            skipped += 1
            continue

        if row.action == "error":
            errors.append(f"Row: {row.account_number}/{row.company_name_raw} — {row.error}")
            continue

        # Unmatched rows — create unresolved claim with raw company name
        if row.company_id is None:
            claim = ClaimRecord(
                holding_id=None,
                claim_reference=row.account_number,
                claim_authority=row.operator_raw,
                claim_type="dividend",
                lifecycle_status="unresolved",
                claim_status="pending",
                raw_company_name=row.company_name_raw,
                documents_reference=f"CSV Upload: {row.shareholder}",
            )
            session.add(claim)
            created += 1
            continue

        # Find or create holding for this company
        result = await session.execute(
            select(Holding).where(
                Holding.deleted_at.is_(None),
                Holding.company_id == row.company_id,
            ).limit(1)
        )
        holding = result.scalar_one_or_none()

        if not holding:
            # Create a placeholder holding for this claim
            holding = Holding(
                company_id=row.company_id,
                num_shares=0,
                average_cost_basis=0,
                total_cost=0,
                holding_type="claim",
            )
            session.add(holding)
            await session.flush()

        # Create claim record (idempotent check: same company + same account_number)
        dedup_check = await session.execute(
            select(ClaimRecord.id).where(
                ClaimRecord.deleted_at.is_(None),
                ClaimRecord.holding_id == holding.id,
                ClaimRecord.claim_reference == row.account_number,
            )
        )
        if dedup_check.scalar_one_or_none():
            skipped += 1
            continue

        claim = ClaimRecord(
            holding_id=holding.id,
            claim_reference=row.account_number,
            claim_authority=row.operator_raw,
            claim_type="dividend",
            lifecycle_status="unresolved",
            claim_status="pending",
            documents_reference=f"CSV Upload: {row.shareholder}",
        )
        session.add(claim)
        created += 1

    await session.commit()

    return _envelope({
        "created": created,
        "skipped": skipped,
        "errors": errors,
        "total": len(payload.rows),
    })


class ResolveClaimRequest(BaseModel):
    company_id: int


@router.put("/{claim_id}/resolve")
async def resolve_claim(
    claim_id: int,
    body: ResolveClaimRequest,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(require_admin),
):
    """Link an unresolved claim to a real company. Creates a placeholder
    holding if none exists, transitions lifecycle_status to 'unclaimed'."""
    # Fetch the claim
    result = await session.execute(
        select(ClaimRecord).where(
            ClaimRecord.id == claim_id,
            ClaimRecord.deleted_at.is_(None),
        )
    )
    claim = result.scalar_one_or_none()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    # Must be unresolved
    if claim.lifecycle_status != "unresolved":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot resolve claim with lifecycle_status='{claim.lifecycle_status}'. Only 'unresolved' claims can be resolved.",
        )

    # Verify company exists
    company_result = await session.execute(
        select(Company).where(Company.id == body.company_id, Company.deleted_at.is_(None))
    )
    company = company_result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Find or create placeholder holding
    holding_result = await session.execute(
        select(Holding).where(
            Holding.deleted_at.is_(None),
            Holding.company_id == body.company_id,
        ).limit(1)
    )
    holding = holding_result.scalar_one_or_none()

    if not holding:
        holding = Holding(
            company_id=body.company_id,
            num_shares=0,
            average_cost_basis=0,
            total_cost=0,
            holding_type="claim",
        )
        session.add(holding)
        await session.flush()

    # Update the claim
    claim.holding_id = holding.id
    claim.lifecycle_status = "unclaimed"
    claim.claim_status = "approved"
    claim.raw_company_name = None  # cleared once linked

    await session.commit()
    await session.refresh(claim)

    return _envelope({
        "id": claim.id,
        "holding_id": claim.holding_id,
        "lifecycle_status": claim.lifecycle_status,
        "claim_status": claim.claim_status,
        "company_ticker": company.ticker,
        "company_name": company.name,
    })
