# EPM Test Builder — Test Case Edit/Delete + Tags Implementation Plan

> **For Hermes:** Use subagent-driven-development to implement this plan task-by-task.
> **Goal:** Add cascade delete for test cases with runs, edit/delete functionality on execute page, and free-form tagging system for test cases with search capability.
> **Architecture:** Backend changes to TestCase model (add tags column), cascade delete for TestRun/BugReport, PUT/DELETE endpoints already exist. Frontend: edit/delete buttons on execute page, tags field on test case form, search filter on execute page.
> **Tech Stack:** FastAPI + Jinja2 + vanilla JS + SQLAlchemy (SQLite) + Docker

---

## Current Context / Assumptions

- **Repo root:** `/home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio/`
- **Test Builder location:** `test_builder/` directory with FastAPI app
- **Deployed at:** `https://testbuild.zubbystudio.shop` via Traefik + Docker
- **Database:** SQLite via SQLAlchemy async, WAL mode, file at `/data/test_builder.db` in container
- **Auth:** Session-based, shared password, 12h expiry
- **Current state:** 
  - PUT `/test-cases/{id}` and DELETE `/test-cases/{id}` endpoints exist but DELETE blocks if runs exist
  - No tags field on TestCase model
  - Execute page has edit/delete buttons wired to `editTestCase()`/`deleteTestCase()` JS functions
  - Test case form has domain, workflow, layer, test_type, title, requirement_ref — no tags field
  - No search/filter on execute page

---

## Proposed Approach

1. **Database migration:** Add `tags` column (TEXT, default empty string) to `test_cases` table
2. **Model update:** Add `tags` column to `TestCase` model with default empty string
3. **Cascade delete:** Modify DELETE endpoint to cascade delete TestRun (and BugReport via cascade) before deleting TestCase
3. **Frontend tags:** Add tags input field to test case form (comma-separated, auto-split on comma)
4. **Search/filter:** Add tags filter on execute page (text input, substring match on tags)
5. **Migration script:** Update existing test cases with empty tags

---

## Step-by-Step Plan

### Task 1: Add `tags` column to TestCase model and database

**Objective:** Add free-form tags column to TestCase model with JSON array storage (comma-separated internally)

**Files:**
- Modify: `test_builder/app/models.py:21-39` (TestCase class)
- Modify: `test_builder/app/database.py:26-47` (init_db migration)

**Step 1: Add tags column to TestCase model**
```python
class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(String(40), primary_key=True)
    domain_code = Column(String(4), ForeignKey("domain_codes.code"), nullable=False)
    workflow = Column(String(20), nullable=False)
    layer = Column(String(4), nullable=False)
    test_type = Column(String(4), nullable=False)
    sequence_no = Column(Integer, nullable=False)
    title = Column(Text, nullable=False)
    requirement_ref = Column(Text, nullable=True)
    tags = Column(Text, nullable=False, default="")  # NEW: comma-separated tags
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ...
```

**Step 2: Add migration in init_db()**
```python
async def init_db():
    _ensure_engine()
    from app import models  # noqa: F401
    async with engine.begin() as conn:
        await conn.execute(text("PRAGMA journal_mode=WAL"))
        await conn.run_sync(Base.metadata.create_all)

        # Migration: add tags column if missing
        try:
            await conn.execute(text("ALTER TABLE test_cases ADD COLUMN tags TEXT NOT NULL DEFAULT ''"))
        except Exception:
            pass  # Column already exists
```

**Verification:** Run container, check `/data/test_builder.db` has `tags` column in `test_cases` table

---

### Task 2: Implement cascade delete for test cases with runs

**Objective:** Modify DELETE endpoint to cascade delete TestRun (and BugReport via relationship cascade) before deleting TestCase

**Files:**
- Modify: `test_builder/app/routers/test_cases.py:169-184` (delete_test_case function)

**Step 1: Update delete endpoint to cascade**
```python
@router.delete("/{test_id}")
async def delete_test_case(test_id: str, session: AsyncSession = Depends(get_session)):
    """Delete a test case — cascades to delete runs and bug reports."""
    result = await session.execute(select(TestCase).where(TestCase.id == test_id))
    tc = result.scalar_one_or_none()
    if not tc:
        raise HTTPException(status_code=404, detail="Test case not found")

    # Cascade delete: runs will cascade to bug_reports via relationship
    await session.delete(tc)
    await session.commit()
    return JSONResponse(content={"message": "Test case and associated runs deleted"})
```

**Step 2: Add cascade to TestRun relationship in model**
```python
class TestCase(Base):
    ...
    runs = relationship("TestRun", back_populates="test_case", order_by="TestRun.run_number", cascade="all, delete-orphan")
```

**Verification:** 
- Create test case, add run, delete test case → verify test_case, test_run, and bug_report rows all deleted

---

### Task 3: Add tags field to test case form (frontend)

**Objective:** Add comma-separated tags input to test case form with live preview

**Files:**
- Modify: `test_builder/app/templates/test_cases.html:47-54` (form)
- Modify: `test_builder/app/static/app.js:48-92` (handleSaveDraft, renderDraftList, generateTestId)

**Step 1: Add tags input to form**
```html
<div class="form-group form-group-full">
    <label for="tags">Tags (comma-separated)</label>
    <input type="text" id="tags" name="tags" placeholder="e.g. regression, api, critical, payment">
    <span class="text-muted" style="font-size:0.75rem;">Press Enter or comma to separate tags</span>
</div>
```

**Step 2: Update handleSaveDraft to include tags**
```javascript
function handleSaveDraft() {
    const tags = document.getElementById('tags').value.trim()
        .split(',')
        .map(t => t.trim())
        .filter(t => t.length > 0);
    // ... include tags in draft object
    const draft = {
        // ... existing fields
        tags: tags,
    };
    // ...
}
```

**Step 3: Update renderDraftList to show tags**
```javascript
function renderDraftList() {
    // ...
    ${drafts.map((d, i) => `
        <tr>
            <td class="font-mono">${d.id}</td>
            <td>${escapeHtml(d.title)}</td>
            <td>${d.domain}</td>
            <td>${d.layer}</td>
            <td>${d.test_type}</td>
            <td><span class="tags-badge">${d.tags.join(', ')}</span></td>
            <td><button class="btn btn-ghost btn-sm" onclick="removeDraft(${i})">Remove</button></td>
        </tr>
    `).join('')}
```

**Verification:** Add test case with tags "regression, api, critical" → verify tags appear in draft list and submit correctly

---

### Task 4: Add tags to API submission and database storage

**Objective:** Include tags in API submission and store as comma-separated string

**Files:**
- Modify: `test_builder/app/routers/test_cases.py:41-102` (submit_test_cases endpoint)

**Step 1: Extract tags from request**
```python
# In submit_test_cases, for each case:
tags = case.get("tags", [])
if isinstance(tags, list):
    tags_str = ",".join(tags)
else:
    tags_str = str(tags)
```

**Step 2: Include in TestCase creation**
```python
tc = TestCase(
    id=test_id,
    domain_code=case["domain"].upper(),
    workflow=case["workflow"].upper(),
    layer=case["layer"].upper(),
    test_type=case["test_type"].upper(),
    sequence_no=seq,
    title=case.get("title", ""),
    requirement_ref=case.get("requirement_ref"),
    tags=tags_str,  # NEW
)
```

**Verification:** Submit test case with tags → query DB → verify tags column has comma-separated values

---

### Task 5: Add tags filter/search on execute page

**Objective:** Add tags search input on execute page that filters test cases by substring match on tags

**Files:**
- Modify: `test_builder/app/templates/execute.html:9-79` (add filter input, update template logic)
- Modify: `test_builder/app/routers/test_runs.py:51-99` (execute_page endpoint)

**Step 1: Add filter input to execute page template**
```html
<div class="page-header">
    <h1>Execute Tests</h1>
    <p class="text-secondary">Record execution results for submitted test cases.</p>
</div>

<div class="filter-bar">
    <div class="form-group">
        <label for="tags-filter">Filter by tags</label>
        <input type="text" id="tags-filter" placeholder="e.g. regression, api" oninput="filterByTags()">
    </div>
</div>
```

**Step 2: Add JavaScript filter function**
```javascript
function filterByTags() {
    const filter = document.getElementById('tags-filter').value.toLowerCase();
    const cards = document.querySelectorAll('.test-case-card');
    cards.forEach(card => {
        const tagsText = card.querySelector('.test-meta')?.textContent?.toLowerCase() || '';
        if (!filter || tagsText.includes(filter)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}
```

**Step 3: Add tags display to test case card (optional)**
```html
<div class="test-meta">
    <span>{{ item.test_case.domain_code }}</span>
    <span>{{ item.test_case.workflow }}</span>
    <span>{{ item.test_case.layer }}</span>
    <span>{{ item.test_case.test_type }}</span>
    <span class="tags-badge">{{ item.test_case.tags }}</span>
    <span>{{ item.total_runs }} run{{ 's' if item.total_runs != 1 else '' }}</span>
</div>
```

**Verification:** Tag test case "regression, api" → type "reg" in filter → only matching test cases visible

---

### Task 6: Add cascade to TestRun relationship in model

**Objective:** Ensure TestRun (and BugReport) cascade delete when TestCase is deleted

**Files:**
- Modify: `test_builder/app/models.py:39` (TestCase.runs relationship)

**Step 1: Update relationship with cascade**
```python
class TestCase(Base):
    ...
    runs = relationship("TestRun", back_populates="test_case", order_by="TestRun.run_number", cascade="all, delete-orphan")
```

**Step 2: Ensure BugReport cascade from TestRun**
```python
class TestRun(Base):
    ...
    bug_report = relationship("BugReport", back_populates="test_run", uselist=False, cascade="all, delete-orphan")
```

**Verification:** Delete test case with runs → verify test_runs and bug_reports tables have no orphaned rows

---

### Task 7: Rebuild and deploy

**Objective:** Rebuild Docker image and deploy to VPS

**Files:**
- No code changes, just deploy commands

**Step 1: Build and deploy**
```bash
cd /home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio
docker compose -f docker-compose.test-builder.yml up -d --build
```

**Step 2: Verify deployment**
```bash
# Check container status
docker ps --filter name=test-builder

# Test endpoint
curl -sL https://testbuild.zubbystudio.shop/test-cases/execute | grep -c "PRIC-UPDATE"

# Test cascade delete
# 1. Create test case with runs
# 2. Delete test case
# 3. Verify runs deleted
```

**Verification:** All features working on production URL

---

## Files Likely to Change

| File | Changes |
|------|---------|
| `test_builder/app/models.py` | Add `tags` column to TestCase, add cascade to runs relationship |
| `test_builder/app/database.py` | Add migration for `tags` column in `init_db()` |
| `test_builder/app/routers/test_cases.py` | Update submit endpoint for tags, update delete for cascade |
| `test_builder/app/templates/test_cases.html` | Add tags input to form, display tags in draft list |
| `test_builder/app/static/app.js` | Handle tags in form, display tags in draft list |
| `test_builder/app/templates/execute.html` | Add tags filter input, display tags on cards |
| `test_builder/app/static/app.js` | Add filterByTags() function |
| `test_builder/app/routers/test_runs.py` | Pass tags to template for display/filtering |

---

## Tests / Validation

| Test | Expected Result |
|------|----------------|
| Add test case with tags "regression, api" | Tags stored as "regression,api" in DB |
| Submit test case without tags | Tags column empty string |
| Edit test case title via PUT | Title updated, tags preserved |
| Delete test case with no runs | Test case deleted, 200 OK |
| Delete test case with runs | Test case + runs + bug reports all deleted |
| Filter by tag "reg" on execute page | Only test cases with "regression" tag shown |
| Filter by tag "api" | Only test cases with "api" tag shown |
| Clear filter | All test cases visible again |
| Tags display on execute page | Tags visible next to test case meta |
| Scaffold generation | Tags included in generated pytest stub (optional) |

---

## Risks, Tradeoffs, and Open Questions

| Risk | Mitigation |
|------|------------|
| SQLite ALTER TABLE may not support adding column with default in all versions | Use try/except in migration, manual migration as fallback |
| Cascade delete may be slow for test cases with many runs | Acceptable for QA tool scale; add index on test_case_id if needed |
| Tags search is client-side only | For large datasets, move to server-side search later |
| Tag format inconsistency (spaces, case) | Normalize to lowercase, trim spaces on save |
| No tag autocomplete/suggestions | Can add later if needed; free-form is flexible |

---

## Execution Handoff

Plan complete. Ready to execute using **subagent-driven-development** — dispatch fresh subagent per task with two-stage review (spec compliance then code quality).

**Shall I proceed with implementation?**