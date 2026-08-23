"""
Company name fuzzy matching utility for claims CSV upload.

Uses rapidfuzz to match raw company names from CSV input against the
canonical company names in the database. Thresholds are named constants
so they can be tuned without touching business logic.

See HO-036 for governance ruling on thresholds.
"""

from rapidfuzz import fuzz, process
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Company

# ── Match thresholds (named constants — tunable) ──────────────────────────────
MATCH_THRESHOLD: int = 90       # Score >= 90 → auto-match
AMBIGUOUS_THRESHOLD: int = 70   # Score 70–89 → show candidates for user selection
                                # Score < 70 → unmatched


async def find_company(
    raw_name: str,
    db: AsyncSession,
) -> tuple[int | None, str | None, list[dict]]:
    """
    Fuzzy-match a raw company name against all companies in the database.

    Returns (company_id, company_name, candidates) where:
      - company_id: ID of the matched company (None if no match >= MATCH_THRESHOLD)
      - company_name: matched canonical name (None if no auto-match)
      - candidates: list of dicts {company_id, name, score} for scores >= AMBIGUOUS_THRESHOLD
                    (empty if score >= MATCH_THRESHOLD, since auto-match applies)

    Scoring is case-insensitive; abbreviations and extra whitespace are handled
    by rapidfuzz's partial token sort ratio.
    """
    result = await db.execute(select(Company.id, Company.name))
    companies = list(result.all())

    if not companies:
        return None, None, []

    names = [row[1] for row in companies]
    id_map = {row[1]: row[0] for row in companies}

    # Try exact match first (fast path)
    normalized = raw_name.strip().upper()
    for row_name in names:
        if row_name.strip().upper() == normalized:
            return int(id_map[row_name]), row_name, []

    # Fuzzy match using token_sort_ratio (handles word order differences)
    best_match, best_score, _ = process.extractOne(
        raw_name,
        names,
        scorer=fuzz.partial_token_sort_ratio,
    )

    if best_score >= MATCH_THRESHOLD:
        company_id = int(id_map[best_match])
        return company_id, best_match, []

    if best_score >= AMBIGUOUS_THRESHOLD:
        # Get all candidates above threshold
        all_scores = process.extract(
            raw_name,
            names,
            scorer=fuzz.partial_token_sort_ratio,
            limit=5,
        )
        candidates = [
            {
                "company_id": int(id_map[name]),
                "company_name": name,
                "score": score,
            }
            for name, score, _ in all_scores
            if score >= AMBIGUOUS_THRESHOLD
        ]
        return None, None, candidates

    return None, None, []


async def get_all_company_names(db: AsyncSession) -> list[str]:
    """Helper: get all canonical company names."""
    result = await db.execute(select(Company.name))
    return [row[0] for row in result.all()]
