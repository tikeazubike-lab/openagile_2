# FOUNDATION_VISION.md

## System Identity
- Name: Estate Portfolio Manager (EPM)
- Version: v2 (FastAPI + React — full rebuild from Streamlit v1)
- Owner: Single primary user (admin), with future multi-user expansion planned
- Hosting: Self-hosted, Netcup VPS, Ubuntu 24.04

## Problem Being Solved
- Nigerian retail investor has 85+ NGX stock holdings with no unified tool
- No single view of total net worth across active holdings + claims
- Unclaimed dividends scattered across multiple registrars
- Delisted/defunct stocks with AMCON/CAC claims not tracked
- Physical share certificates requiring digitisation with no document management
- Registrar requirements per action type (dematerialisation, KYC, dividend claim) not tracked
- Price data unavailable via free API — NGX requires manual PDF download
- No historical NAV tracking — portfolio performance unmeasurable
- All prior tooling: Obsidian markdown vault + Python scripts — no web UI, no edit capability

## What the System Becomes
- Complete personal Nigerian investment management system
- Single authoritative source of truth for: ownership, valuation, administration, documentation
- Replaces: Obsidian vault, Excel workarounds, manual registrar notes
- Grows from: single-user NGX equities → multi-user, multi-asset-class Nigerian investments

## Three Core Jobs (Morning Dashboard North Star)
1. Net worth: "What do I own and what is it worth today?"
2. Administration: "What paperwork is outstanding? What dividends uncollected?"
3. Performance: "Is my portfolio growing over time?"

## Asset Scope
- Current: NGX listed equities, delisted/defunct equities, merged equities
- Future: Eurobonds, real estate, treasury bills, fixed deposits, mutual funds
