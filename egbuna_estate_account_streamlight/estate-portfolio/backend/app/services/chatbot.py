"""
EPM — Chatbot RuleBasedRouter (F-022).

Intent matching, entity extraction, and handler dispatch.

INTENT ORDERING RULE (per HO-072 refinement 3):
  Intents are ordered most-specific to least-specific within each domain.
  More specific keyword patterns (e.g. "sector allocation") must appear
  before less specific ones that share substrings (e.g. "sector" alone).
  This prevents a short generic keyword from matching before the longer
  pattern that would produce a better answer.
"""
import logging
from datetime import date as date_type, datetime, timedelta
from decimal import Decimal
from typing import NamedTuple

from fastapi import HTTPException
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.models import (
    NavHistory, Holding, Company, ClaimRecord, PriceHistory, User, Registrar,
)
from app.routers.nav_history import _get_coverage_counts

logger = logging.getLogger(__name__)

# ─── Constants ───────────────────────────────────────────────────────────────

MAX_MESSAGE_LENGTH = 500

SECTOR_NAMES = {
    "banking", "consumer goods", "industrials", "oil & gas", "agriculture",
    "healthcare", "services", "real estate", "manufacturing", "insurance",
    "conglomerate", "hospitality", "technology", "utilities", "construction",
    "aviation", "telecommunications", "media", "entertainment", "ngx",
    "financial services", "investment", "energy", "mining", "transport",
    "education", "agric", "pharmaceutical", "brewery", "sugar", "tobacco",
}

try:
    from app.models import Company as _Comp
    _all_sectors = set()
    # Fetch known sectors at import time for matching
except Exception:
    pass


# ─── Types ───────────────────────────────────────────────────────────────────

class Intent(NamedTuple):
    name: str
    keywords: list[str]
    handler: callable
    required_entities: list[str]
    description: str


class ExtractionResult:
    ticker: str | None = None
    company_name: str | None = None
    sector: str | None = None
    ref_date: date_type | None = None
    relative_period_days: int | None = None  # e.g. 7 for "this week"

    def __init__(self):
        self.ticker = None
        self.company_name = None
        self.sector = None
        self.ref_date = None
        self.relative_period_days = None

    def has_any(self) -> bool:
        return any([self.ticker, self.company_name, self.sector, self.ref_date])


# ─── Entity Extraction ──────────────────────────────────────────────────────

def extract_entities(message: str) -> ExtractionResult:
    """Single shared entity extractor called once before intent matching.

    Extracts: ticker symbol, company name, sector, date/relative period.
    """
    result = ExtractionResult()
    lower = message.lower()
    words = lower.split()
    original_words = message.split()

    # Ticker: look for known ticker symbols (all-caps words in the original message)
    # Tickers are typically 2-7 uppercase letters.
    # We use original_words here because lowercasing loses the uppercase signal.
    for word in original_words:
        cleaned = word.strip(".,?!;:'\"()[]{}")
        if cleaned.isupper() and 3 <= len(cleaned) <= 7 and cleaned.isalpha():
            result.ticker = cleaned

    # Sector: check for known sector names
    for sector in SECTOR_NAMES:
        if sector in lower:
            result.sector = sector
            break

    # Relative periods
    if any(p in lower for p in ["this week", "7 day", "past week", "last week", "7d"]):
        result.relative_period_days = 7
    elif any(p in lower for p in ["this month", "30 day", "past month", "last month", "30d"]):
        result.relative_period_days = 30
    elif any(p in lower for p in ["this year", "ytd", "year to date", "365 day"]):
        result.relative_period_days = 365

    # Absolute date
    try:
        for word in words:
            cleaned = word.strip(".,?!;")
            parts = cleaned.split("-")
            if len(parts) == 3:
                d = date_type.fromisoformat(cleaned)
                result.ref_date = d
                break
    except (ValueError, TypeError):
        pass

    return result


# ─── Ticker Resolution (shared helper) ──────────────────────────────────────

async def _resolve_ticker(session, ticker: str) -> int | None:
    """Look up a company by ticker, return company_id or None."""
    r = await session.execute(
        select(Company.id).where(Company.ticker.ilike(ticker))
    )
    row = r.one_or_none()
    return row[0] if row else None


# ─── Handlers ────────────────────────────────────────────────────────────────

async def handle_nav_current(session, user, message, entities) -> dict:
    r = await session.execute(
        select(NavHistory).order_by(NavHistory.snapshot_date.desc()).limit(1)
    )
    row = r.scalar_one_or_none()
    coverage = await _get_coverage_counts(session)

    if row is None:
        return {
            "matched_intent": "nav_current",
            "response": "No NAV data available yet.",
            "raw_data": None,
        }

    pct = round(coverage["priced_holdings_count"] / coverage["total_active_holdings_count"] * 100)
    response = (
        f"Your current NAV is ₦{float(row.total_value):,.2f}, "
        f"based on {coverage['priced_holdings_count']} of "
        f"{coverage['total_active_holdings_count']} holdings "
        f"with price data ({pct}%)."
    )
    return {
        "matched_intent": "nav_current",
        "response": response,
        "raw_data": {"nav": str(row.total_value), "coverage": coverage},
    }


async def handle_nav_change(session, user, message, entities) -> dict:
    r = await session.execute(
        select(NavHistory).order_by(NavHistory.snapshot_date.desc()).limit(1)
    )
    row = r.scalar_one_or_none()
    if row is None:
        return {"matched_intent": "nav_change", "response": "No NAV data available yet.", "raw_data": None}

    coverage = await _get_coverage_counts(session)
    pct = round(coverage["priced_holdings_count"] / coverage["total_active_holdings_count"] * 100)

    # Get 7-day change from summary
    one_week_ago = date_type.today() - timedelta(days=7)
    r2 = await session.execute(
        select(NavHistory).where(NavHistory.snapshot_date <= one_week_ago)
        .order_by(NavHistory.snapshot_date.desc()).limit(1)
    )
    ref_row = r2.scalar_one_or_none()
    if ref_row and Decimal(str(ref_row.total_value)) > 0:
        current = Decimal(str(row.total_value))
        ref = Decimal(str(ref_row.total_value))
        change = ((current - ref) / ref) * Decimal("100")
        direction = "up" if change > 0 else "down"
        response = (
            f"NAV is ₦{float(row.total_value):,.2f}, "
            f"{direction} {abs(float(change)):.2f}% in the last 7 days "
            f"(based on {coverage['priced_holdings_count']} of "
            f"{coverage['total_active_holdings_count']} holdings with price data, {pct}%)."
        )
    else:
        response = (
            f"Your current NAV is ₦{float(row.total_value):,.2f}. "
            f"Not enough historical data to compute a 7-day change yet."
        )

    return {
        "matched_intent": "nav_change",
        "response": response,
        "raw_data": {"nav": str(row.total_value), "coverage": coverage},
    }


async def handle_hold_count(session, user, message, entities) -> dict:
    stmt = select(Holding).where(Holding.deleted_at.is_(None))
    if user.role != "admin":
        stmt = stmt.where(Holding.holding_type == "active")
    r = await session.execute(stmt)
    holdings = r.scalars().all()

    active = sum(1 for h in holdings if h.num_shares > 0 and h.holding_type == "active")
    claims = sum(1 for h in holdings if h.holding_type == "claim")

    response_parts = [f"You have {active} active holding{'s' if active != 1 else ''}"]
    if claims:
        response_parts.append(f"{claims} claim{'s' if claims != 1 else ''}")
    if user.role == "admin":
        drafts = sum(1 for h in holdings if h.holding_type == "draft")
        if drafts:
            response_parts.append(f"{drafts} draft{'s' if drafts != 1 else ''}")

    return {
        "matched_intent": "hold_count",
        "response": ", ".join(response_parts) + ".",
        "raw_data": {"active": active, "claims": claims},
    }


async def handle_hold_by_sector(session, user, message, entities) -> dict:
    sector = entities.sector
    if not sector:
        return {"matched_intent": "hold_by_sector", "response": "Which sector are you interested in?", "raw_data": None}

    stmt = (
        select(Holding)
        .join(Company, Holding.company_id == Company.id)
        .options(selectinload(Holding.company))
        .where(Holding.deleted_at.is_(None))
        .where(Holding.holding_type == "active")
        .where(Company.sector.ilike(f"%{sector}%"))
    )

    r = await session.execute(stmt)
    holdings = r.scalars().all()

    if not holdings:
        return {"matched_intent": "hold_by_sector", "response": f"No active holdings found in the {sector} sector.", "raw_data": []}

    total = sum(float(h.num_shares * (h.company.current_price or 0)) for h in holdings)
    names = ", ".join(h.company.name or h.company.ticker for h in holdings[:5])
    response = (
        f"You have {len(holdings)} holding{'s' if len(holdings) != 1 else ''} "
        f"in {sector}: {names}. "
        f"Total value: ₦{total:,.2f}."
    )
    return {"matched_intent": "hold_by_sector", "response": response, "raw_data": [{"ticker": h.company.ticker, "value": str(h.current_value)} for h in holdings]}


async def handle_hold_top(session, user, message, entities) -> dict:
    stmt = (
        select(Holding)
        .options(selectinload(Holding.company))
        .where(Holding.deleted_at.is_(None))
        .where(Holding.holding_type == "active")
        .where(Holding.num_shares > 0)
    )
    if user.role != "admin":
        stmt = stmt.where(Holding.holding_type == "active")

    r = await session.execute(stmt)
    holdings = r.scalars().all()

    sorted_h = sorted(
        holdings,
        key=lambda h: float(h.current_value or 0),
        reverse=True,
    )[:5]

    if not sorted_h:
        return {"matched_intent": "hold_top", "response": "No holdings found.", "raw_data": []}

    lines = []
    items = []
    for i, h in enumerate(sorted_h, 1):
        val = float(h.current_value or 0)
        ticker = h.company.ticker if h.company else "N/A"
        lines.append(f"{i}. {ticker} at ₦{val:,.2f}")
        items.append({"ticker": ticker, "value": str(val)})

    return {
        "matched_intent": "hold_top",
        "response": "Your top holdings are: " + "; ".join(lines) + ".",
        "raw_data": items,
    }


async def handle_hold_ticker(session, user, message, entities) -> dict:
    ticker = entities.ticker
    if not ticker:
        return {"matched_intent": "hold_ticker", "response": "Which ticker are you asking about?", "raw_data": None}

    company_id = await _resolve_ticker(session, ticker)
    if company_id is None:
        return {"matched_intent": "hold_ticker", "response": f"I couldn't find a company with ticker {ticker}.", "raw_data": None}

    stmt = (
        select(Holding)
        .options(selectinload(Holding.company), selectinload(Holding.claim_records))
        .where(Holding.deleted_at.is_(None))
        .where(Holding.company_id == company_id)
    )
    if user.role != "admin":
        stmt = stmt.where(Holding.holding_type == "active")

    r = await session.execute(stmt)
    holdings = r.scalars().all()

    if not holdings:
        return {"matched_intent": "hold_ticker", "response": f"You don't have any holdings in {ticker}.", "raw_data": None}

    h = holdings[0]
    val = float(h.current_value or 0)
    cost = float(h.total_cost or 0)
    shares = float(h.num_shares)
    ret_pct = ((val - cost) / cost * 100) if cost > 0 else 0

    response = (
        f"You hold {shares:,.4f} shares of {ticker} "
        f"valued at ₦{val:,.2f} "
        f"with a return of {ret_pct:+.2f}%."
    )
    return {"matched_intent": "hold_ticker", "response": response, "raw_data": {"ticker": ticker, "value": str(val), "return_pct": str(round(ret_pct, 2))}}


async def handle_sector_alloc(session, user, message, entities) -> dict:
    stmt = (
        select(Holding)
        .options(selectinload(Holding.company))
        .where(Holding.deleted_at.is_(None))
        .where(Holding.holding_type == "active")
        .where(Holding.num_shares > 0)
    )
    if user.role != "admin":
        stmt = stmt.where(Holding.holding_type == "active")

    r = await session.execute(stmt)
    holdings = r.scalars().all()

    sector_sums = {}
    for h in holdings:
        sec = h.company.sector if h.company and h.company.sector else "Unknown"
        sector_sums[sec] = sector_sums.get(sec, 0) + float(h.current_value or 0)

    total = sum(sector_sums.values()) or 1
    sorted_sectors = sorted(sector_sums.items(), key=lambda x: -x[1])

    lines = [f"{sec}: {val/total*100:.1f}%" for sec, val in sorted_sectors[:5]]
    return {
        "matched_intent": "sector_alloc",
        "response": "Sector allocation: " + "; ".join(lines) + ".",
        "raw_data": [{"sector": sec, "pct": str(round(val/total*100, 1))} for sec, val in sorted_sectors],
    }


async def handle_claim_status(session, user, message, entities) -> dict:
    stmt = (
        select(ClaimRecord)
        .options(selectinload(ClaimRecord.holding).selectinload(Holding.company))
    )

    r = await session.execute(stmt)
    claims = r.scalars().all()

    if not claims:
        return {"matched_intent": "claim_status", "response": "You don't have any claims recorded.", "raw_data": []}

    unresolved = [c for c in claims if c.lifecycle_status == "unresolved"]
    unclaimed = [c for c in claims if c.lifecycle_status == "unclaimed"]
    claimed = [c for c in claims if c.lifecycle_status == "claimed"]

    parts = []
    if unresolved:
        parts.append(f"{len(unresolved)} unresolved")
    if unclaimed:
        parts.append(f"{len(unclaimed)} unclaimed")
    if claimed:
        parts.append(f"{len(claimed)} claimed")

    response = f"You have {len(claims)} claim{'s' if len(claims) != 1 else ''}" + (": " + ", ".join(parts) + "." if parts else ".")

    return {"matched_intent": "claim_status", "response": response, "raw_data": {"total": len(claims), "unresolved": len(unresolved), "unclaimed": len(unclaimed), "claimed": len(claimed)}}


async def handle_comp_sector(session, user, message, entities) -> dict:
    ticker = entities.ticker
    if not ticker:
        return {"matched_intent": "comp_sector", "response": "Which company are you asking about?", "raw_data": None}

    r = await session.execute(
        select(Company).where(Company.ticker.ilike(ticker))
    )
    company = r.scalar_one_or_none()
    if not company:
        return {"matched_intent": "comp_sector", "response": f"I couldn't find a company with ticker {ticker}.", "raw_data": None}

    return {
        "matched_intent": "comp_sector",
        "response": f"{ticker} ({company.name}) is in the {company.sector or 'N/A'} sector.",
        "raw_data": {"ticker": ticker, "sector": company.sector},
    }


async def handle_price_latest(session, user, message, entities) -> dict:
    ticker = entities.ticker
    if not ticker:
        return {"matched_intent": "price_latest", "response": "Which ticker's price are you looking for?", "raw_data": None}

    company_id = await _resolve_ticker(session, ticker)
    if company_id is None:
        return {"matched_intent": "price_latest", "response": f"I couldn't find a company with ticker {ticker}.", "raw_data": None}

    r = await session.execute(
        select(PriceHistory)
        .where(PriceHistory.company_id == company_id)
        .order_by(PriceHistory.price_date.desc())
        .limit(1)
    )
    price = r.scalar_one_or_none()
    if not price:
        return {"matched_intent": "price_latest", "response": f"No price data available for {ticker}.", "raw_data": None}

    return {
        "matched_intent": "price_latest",
        "response": f"The latest price for {ticker} is ₦{float(price.close_price):,.2f} as of {price.price_date}.",
        "raw_data": {"ticker": ticker, "price": str(price.close_price), "date": str(price.price_date)},
    }


# ─── Intent Registry (ordered most-specific → least-specific) ────────────────
#
# INTENT ORDERING RULE (per HO-072 refinement 3):
# Within each domain, list more specific patterns first so they match before
# shorter/generic patterns that share substrings. For example, "sector allocation"
# must appear before a bare "sector" match, and "how many holdings in banking"
# must appear before a generic "how many" or "holdings" match.
#
# required_entities: if non-empty, the handler needs the entity to be present.
#   The router will check this and route to the entity-clarification branch
#   rather than calling the handler without the needed entity.

INTENTS: list[Intent] = [
    # ── NAV (most specific first) ─────────────────────────────────────────────
    Intent("nav_current", ["current nav", "net asset value", "portfolio worth",
                           "portfolio value", "total value", "what's my nav",
                           "what is my nav", "how much is my portfolio"],
           handle_nav_current, [], "Current NAV value"),
    Intent("nav_change", ["nav change", "nav performance", "nav this week",
                          "nav this month", "nav this year", "how did nav",
                          "nav trend", "nav movement"],
           handle_nav_change, [], "NAV change over period"),

    # ── Holdings (most specific first) ────────────────────────────────────────
    Intent("sector_alloc", ["sector allocation", "sector breakdown", "allocation by sector",
                            "how are my holdings spread", "sector split"],
           handle_sector_alloc, [], "Sector allocation breakdown"),
    Intent("hold_by_sector", ["holdings in", "holdings by", "companies in", "stocks in"],
           handle_hold_by_sector, ["sector"], "Holdings filtered by sector"),
    Intent("hold_top", ["biggest holding", "top holding", "largest position",
                        "most valuable", "top holdings"],
           handle_hold_top, [], "Top holdings by value"),
    Intent("hold_ticker", [],  # ticker entity handles this when present
           handle_hold_ticker, ["ticker"], "Holding details for a specific ticker"),
    Intent("hold_count", ["how many holdings", "total holdings", "holdings count",
                          "number of holdings"],
           handle_hold_count, [], "Total holding count"),

    # ── Claims ────────────────────────────────────────────────────────────────
    Intent("claim_status", ["claim status", "claims", "dividends due", "dividend status",
                            "my claims", "any claims", "unresolved claims",
                            "pending claims", "unclaimed"],
           handle_claim_status, [], "Claim/dividend status summary"),

    # ── Companies ─────────────────────────────────────────────────────────────
    Intent("comp_sector", ["what sector", "which sector", "sector of"],
           handle_comp_sector, ["ticker"], "Company sector lookup"),

    # ── Price History ─────────────────────────────────────────────────────────
    Intent("price_latest", ["latest price", "current price", "price of", "stock price"],
           handle_price_latest, ["ticker"], "Latest price for a ticker"),
]


# ─── Router / Dispatcher ────────────────────────────────────────────────────

async def route_intent(
    session, user, message: str, entities: ExtractionResult,
) -> tuple[dict, str]:
    """Match the message against the intent registry and dispatch.

    Returns (result_dict, execution_status).
    execution_status is one of: matched, unmatched, entity_not_found, error.
    """
    lower = message.lower()

    # Try each intent in order (most-specific first)
    for intent in INTENTS:
        if not any(kw in lower for kw in intent.keywords):
            continue

        # Check if required entities are present
        if intent.required_entities:
            missing = [e for e in intent.required_entities if not getattr(entities, e, None)]
            if missing:
                # Entity recognized but not enough info — route to clarification
                entity_hint = _build_entity_hint(entities)
                return {
                    "matched_intent": None,
                    "response": f"I see you're asking about {entity_hint}. "
                                f"What would you like to know — its current price, "
                                f"holding value, or claim status?",
                    "raw_data": None,
                }, "unmatched"

        try:
            result = await intent.handler(session, user, message, entities)
            return result, "matched"
        except HTTPException:
            logger.exception("HTTPException in chatbot handler for intent=%s", intent.name)
            return {
                "matched_intent": intent.name,
                "response": "Something went wrong retrieving that information. Please try again.",
                "raw_data": None,
            }, "error"
        except Exception:
            logger.exception("Unhandled exception in chatbot handler for intent=%s", intent.name)
            return {
                "matched_intent": intent.name,
                "response": "Something went wrong processing your request. Please try again.",
                "raw_data": None,
            }, "error"

    # No intent matched — check for entity-only matches (clarification branch)
    if entities.has_any():
        entity_hint = _build_entity_hint(entities)
        return {
            "matched_intent": None,
            "response": f"I see you mentioned {entity_hint}. "
                        f"What would you like to know — its current price, "
                        f"holding value, sector, or claim status?",
            "raw_data": None,
        }, "unmatched"

    # Truly unmatched
    return {
        "matched_intent": None,
        "response": "I can answer questions about your holdings, NAV, claims, companies, "
                    "and prices. Try asking about your biggest holding, current NAV, "
                    "or a specific ticker.",
        "raw_data": None,
    }, "unmatched"


def _build_entity_hint(entities: ExtractionResult) -> str:
    parts = []
    if entities.ticker:
        parts.append(entities.ticker)
    if entities.company_name:
        parts.append(entities.company_name)
    if entities.sector:
        parts.append(f"the {entities.sector} sector")
    if entities.ref_date:
        parts.append(f"data for {entities.ref_date}")
    return " and ".join(parts) if parts else "something"
