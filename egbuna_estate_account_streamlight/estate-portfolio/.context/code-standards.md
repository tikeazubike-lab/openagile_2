# code-standards.md — EPM Code Standards

---

## Python (Backend)

### Types and Validation

- Type hints on ALL function signatures — no untyped arguments

- Pydantic BaseModel for ALL request bodies — never raw dict

- field_validator for domain rules (positive numbers, future dates, string format)

- Decimal for ALL monetary arithmetic — never float

- Optional[str] for nullable monetary fields in Pydantic models

### Database

- All DB operations async/await — no sync DB calls ever

- Always use get_session() — not get_db() (does not exist)

- Soft delete: deleted_at = datetime.now(timezone.utc)

- Never datetime.utcnow() — it returns naive datetime, causes timezone mismatch

- Filter deleted: .where(Model.deleted_at.is_(None))

### Errors

- HTTPException(status_code=N, detail="clear message") for all error responses

- 404 when resource not found

- 422 when payload validation fails (Pydantic handles automatically)

- 403 when role insufficient (not 401 — user is authenticated, just not authorised)

- 409 when unique constraint would be violated (duplicate company holding, etc.)

### API Response Shape

Every endpoint returns this envelope — no exceptions:

{

"data": <list or object>,

"meta": {"total": N}, # list endpoints only

"error": null

}

Monetary fields always strings:

"current_value": "45000.00" # CORRECT

"current_value": 45000.0 # WRONG — float causes JS precision loss

### Commits

feat(scope): description

fix(scope): description

chore(scope): description

test(scope): description

docs(scope): description

---

## TypeScript (Frontend)

### Types

- Strict mode — no any types

- Define interfaces for all API response shapes

- Optional chaining everywhere: item?.field ?? fallback

### Null Safety (Mandatory — crash prevention)

# Monetary display

fmtNaira(value ?? null) # correct

value.toLocaleString() # WRONG — crashes on null

# Percentages

value?.toFixed(2) ?? "—" # correct

value.toFixed(2) # WRONG — crashes on null

# Arrays from API

const items = data?.items ?? [] # correct

data.items.map(...) # WRONG — crashes when data not loaded

# Claim holdings

holding_type === 'claim' ? "—" : fmtPct(return_pct) # correct

### API Calls

fetch('/api/v1/endpoint', { credentials: 'include' }) # always include

fetch('/api/v1/endpoint') # WRONG — no cookie sent

### Colours

className="bg-[var(--accent-lavender)]" # correct

className="bg-[#BCBDFA]" # WRONG — hardcoded hex

### Recharts Exception (Only Place Floats Are Acceptable)

# Parse strings to numbers ONLY at the Recharts component boundary

const chartData = data.map(d => ({

name: d.name,

value: parseFloat(d.value), # number for chart sizing

display: fmtNaira(d.value), # string for tooltip display

}));

### Monetary Input Fields

# Always send strings to backend

avg_purchase_price: price.toFixed(2) # "400.00" — correct

avg_purchase_price: parseFloat(price) # 400.0 — WRONG

### TanStack Query Invalidation (After Every Mutation)

onSuccess: () => {

qc.invalidateQueries({ queryKey: ['dashboard'] });

qc.invalidateQueries({ queryKey: ['holdings'] });

// invalidate all related queries — never just one

}

### Inline Editing Pattern (Cursor-Jump Prevention)

# Edit state MUST live in a child component — never in the parent table

# Wrong: editForm state in HoldingsPage → re-renders table on every keystroke

# Correct: InlineEditRow child component owns its own state

---

## File Naming

Context files: .context/*.md

Feature specs: .context/feature-specs/F-XXX-feature-name.md

Gherkin specs: docs/testing/features/F-XXX-name.feature

Handovers: docs/handovers/HO-XXX-from-to-topic.md

Acceptance tests: docs/testing/acceptance/AT-XXX-feature-YYYY-MM-DD.md

Architecture decisions: docs/decisions/ADR-XXX-title.md

---

## Column Header Contract

The return percentage column header is EXACTLY the string "return[%]"

No variations: not "Return %", not "Return[%]", not "return %"

This is a hard contract because tests assert against this exact string.
