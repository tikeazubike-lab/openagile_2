---
type: HO
id: HO-042
title: Hermes → Claude: F-010 Reconciliation — Spec, Backend, Frontend Dump
date: 2026-07-07
from: Hermes (deepseek-flash)
to: Claude Web (The Brain / Architect)
protocol: OpenAgile Hybrid Framework v1.0
priority: URGENT — blocks F-010 audit and Phase 3C sequencing
---

# HO-042 — F-010 Reconciliation: All Files for Audit

## 1. Context

Claude requested the F-010 spec and implementation code to audit against
the new `lifecycle_status` column added by F-011 (HO-036 ruling). Below
is the complete dump of all relevant files with their paths, state derivation
logic, and the key tension that needs resolution.

---

## 2. File Inventory

| # | File | Lines | Purpose |
|---|------|-------|---------|
| 1 | `.context/feature-specs/F-010-claims.md` | 386 | Original F-010 feature specification |
| 2 | `backend/app/models.py` (lines 152–186) | 35 | ClaimRecord ORM model |
| 3 | `backend/app/routers/claims.py` (lines 76–141) | 66 | GET /api/v1/claims endpoint |
| 4 | `estate-portfolio-manager/src/routes/_app.claims.tsx` (lines 44–139) | 96 | Frontend claims page (state derivation) |
| 5 | `estate-portfolio-manager/src/types/index.ts` (lines 171–186) | 16 | Claim TypeScript interface |

---

## 3. File 1: F-010 Spec — State Model (Spec-Defined)

**Path:** `.context/feature-specs/F-010-claims.md`

The spec defines **3 display states** mapped from the 6-value `claim_status`
enum:

| DB claim_status | Display State | Filter Group |
|----------------|---------------|--------------|
| pending | Unresolved | Unresolved |
| partially_paid | Unresolved | Unresolved |
| approved | Unclaimed | Unclaimed |
| paid | Claimed | Claimed |
| rejected | Unresolved | Unresolved |
| lapsed | Unresolved | Unresolved |

This was written **before** `lifecycle_status` existed. It also uses
state names: **Unresolved / Unclaimed / Claimed**.

Full spec at `.context/feature-specs/F-010-claims.md` — 386 lines covering
KPIs, charts, registrar summary, detail drawers, document upload widget,
state transitions, acceptance criteria (AC-01 through AC-18).

---

## 4. File 2: ClaimRecord Model

**Path:** `backend/app/models.py` lines 152–186

```python
class ClaimRecord(Base):
    __tablename__ = "claim_records"
    __table_args__ = (
        CheckConstraint("claim_status IN ('pending','approved','rejected','partially_paid','paid','lapsed')",
                        name="chk_claim_status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    holding_id: Mapped[int] = mapped_column(Integer, ForeignKey("holdings.id", ondelete="CASCADE"),
                                            nullable=False, index=True)
    claim_reference: Mapped[str | None] = mapped_column(String(100))
    claim_authority: Mapped[str | None] = mapped_column(String(100))
    claim_type: Mapped[str] = mapped_column(String(50), nullable=False, default="liquidation")
    date_filed: Mapped[datetime | None] = mapped_column(Date)
    date_acknowledged: Mapped[datetime | None] = mapped_column(Date)
    deadline_date: Mapped[datetime | None] = mapped_column(Date)

    claim_status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending", index=True)
    lifecycle_status: Mapped[str] = mapped_column(String(12), nullable=False, default="unresolved", index=True)

    expected_payout: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    actual_payout: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    payout_date: Mapped[datetime | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)
    documents_reference: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    holding: Mapped["Holding"] = relationship("Holding", back_populates="claim_records")
```

Key facts:
- `holding_id` is `nullable=False` (current constraint — F-011 wanted to make it nullable for
  unresolved claims but this was **not yet implemented**)
- `lifecycle_status` has `CHECK` constraint from the additive migration: `IN ('unresolved','unclaimed','claimed')`
- Both `claim_status` and `lifecycle_status` coexist permanently (HO-036 ruling)
- No `raw_company_name` column exists yet (needed for unresolved claims without a matched company)

---

## 5. File 3: Backend API — GET /api/v1/claims

**Path:** `backend/app/routers/claims.py` lines 76–141

```python
@router.get("")
async def get_claims(
    holding_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),           # filters on claim_status
    lifecycle_status: Optional[str] = Query(None),  # filters on lifecycle_status
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
            "lifecycle_status": c.lifecycle_status,   # <-- exposed in response
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
```

Key facts:
- API returns BOTH `claim_status` AND `lifecycle_status` in every response
- Both can be used as filter parameters independently
- No `raw_company_name` in response (not yet added)
- If `holding` is null (unresolved claim), the `holding` key is `None` — frontend
  handles this gracefully? (Needs audit)

---

## 6. File 4: Frontend — State Derivation Logic

**Path:** `estate-portfolio-manager/src/routes/_app.claims.tsx`

### Status mapping (lines 44–53):

```typescript
// ─── Status mapping: 6 DB statuses → 3 UI statuses ──────────────────────────

const statusMap: Record<string, "Pending" | "Claimed" | "Unclaimed"> = {
  pending: "Pending",
  partially_paid: "Pending",
  approved: "Claimed",
  paid: "Claimed",
  rejected: "Unclaimed",
  lapsed: "Unclaimed",
};

type UiStatus = "Pending" | "Claimed" | "Unclaimed";
```

### Enriched records (lines 102–130):

```typescript
const enriched = useMemo(() => {
  if (!claims) return [];
  return claims.map((c) => {
    const uiStatus: UiStatus = statusMap[c.claim_status] ?? "Unclaimed";
    const mandate: MandateStatus = uiStatus === "Claimed" ? "Active" : "None";
    const ref = c.claim_reference || (...);
    const amount = c.actual_payout ?? c.expected_payout ?? 0;
    // ... derives company, registrar, shares, year, lastUpdated
    return { claim: c, ref, company, registrar, shares, uiStatus, mandate, amount, year, lastUpdated, notes };
  });
}, [claims]);
```

### Filter logic (lines 132–140):

```typescript
const filtered = useMemo(
  () =>
    enriched.filter(
      (r) =>
        (regFilter === "all" || r.registrar === regFilter) &&
        (statusFilter === "all" || r.uiStatus === statusFilter) &&
        (q === "" || r.ref.toLowerCase().includes(q.toLowerCase()) || ...)
    ),
  [enriched, regFilter, statusFilter, q]
);
```

Key facts:
- Frontend uses `c.claim_status` mapped through `statusMap` (lines 44–53, 105)
- Frontend does NOT use `c.lifecycle_status` at all — despite it being in the API response
- The 3 UI state names in the frontend are: **Pending / Claimed / Unclaimed**
- The F-010 spec defines them as: **Unresolved / Unclaimed / Claimed**
- The `lifecycle_status` column values are: **unresolved / unclaimed / claimed**

---

## 7. File 5: TypeScript Types

**Path:** `estate-portfolio-manager/src/types/index.ts` lines 171–186

```typescript
// ─── Claims (F-010) ────────────────────────────────────────────────────────────

export interface ClaimHolding {
  id: number;
  num_shares: string;
  company_ticker?: string;
  company_name?: string;
  registrar_name?: string;
}

export interface Claim {
  id: number;
  claim_reference: string;
  holding: ClaimHolding | null;
  claim_status: string;
  lifecycle_status: string;       // <-- already typed but unused in derivation
  actual_payout: number | null;
  expected_payout: number | null;
  // ...
}
```

Key facts:
- `lifecycle_status: string` is already in the Claim type
- `holding: ClaimHolding | null` — supports null holding (needed for unresolved claims)

---

## 8. The Tension — Three State Models Collide

There are three competing definitions of the 3-state model:

| Source | State A | State B | State C |
|--------|---------|---------|---------|
| **F-010 Spec** (§Status mapping) | Unresolved | Unclaimed | Claimed |
| **Frontend code** (`statusMap`, line 46) | Pending | Unclaimed | Claimed |
| **lifecycle_status column** (DB, model) | unresolved | unclaimed | claimed |

**Mismatches:**
1. Spec says `approved → Unclaimed`, frontend says `approved → Claimed`
2. Spec says `rejected → Unresolved`, frontend says `rejected → Unclaimed`
3. Spec says `lapsed → Unresolved`, frontend says `lapsed → Unclaimed`
4. Spec uses "Unresolved", frontend uses "Pending" for the same conceptual state
5. Frontend derives from `claim_status` (via `statusMap`) instead of reading `lifecycle_status` directly
6. `lifecycle_status` column is the authoritative 3-state value (from HO-036 ruling) but the frontend ignores it

---

## 9. Recommended Decision Path for Claude

The cleanest resolution is probably:
1. **Frontend reads `lifecycle_status` directly** instead of mapping `claim_status` through `statusMap`
2. **Rename the 3 UI states** to match the spec: "Unresolved" / "Unclaimed" / "Claimed"
3. **Remove the `statusMap`** — it's redundant now that `lifecycle_status` is the source of truth
4. **Align the `statusBadge` styling** to the new 3 names

But this is an architectural decision — Claude should rule.

---

## 10. Files Referenced (All in Repo)

```
.context/feature-specs/F-010-claims.md
backend/app/models.py                    (lines 152-186)
backend/app/routers/claims.py            (lines 1-141)
estate-portfolio-manager/src/routes/_app.claims.tsx  (lines 44-139)
estate-portfolio-manager/src/types/index.ts          (lines 171-186)
```

---

*Handover authored by Hermes Agent (deepseek-flash) on 2026-07-07 23:30 WAT*
