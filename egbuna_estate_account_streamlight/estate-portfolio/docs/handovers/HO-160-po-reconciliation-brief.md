# HO-160: Product Owner reconciliation brief (received 2026-11-28)

The Product Owner pasted this brief into the Claude Code session on 2026-11-28 as "the answer from CODEX".
The Product Owner owns it. It is filed here so the spec can cite it (F-026c §12).

## Summary of the brief as received
**Objective:** reconcile every EPM company against NGX across six attributes:
- ticker
- current legal name
- Nigerian registrar
- exchange
- listing status
- trading status

**Source hierarchy:**
1. NGX
2. the NGX Daily Official List
3. NGX X-Compliance
4. SEC Nigeria
5. audited annual reports
6. investor relations
7. registrar websites
8. secondary databases, for support only

**Settled decisions** (preserve unless authoritative evidence contradicts them):
- SEPLAT is on DataMax, with Computershare for London only. Co-registrar is not modelled.
- Keep OKOMUOIL, WEMABANK, LEARNAFRCA, LIVESTOCK, TRANSPOWER and DNMEYER ("Meyer Plc", Greenwich).
- ACCESSCORP is Access Holdings Plc (Coronation Registrars). ACCESS is the obsolete Access Bank ticker, and SDACCESS is Access Bank on NASD OTC. Access Bank history is preserved and reconciled separately.
- GTL is Greenwich.
- TRANSEXPR is the correct ticker (not TRANEX): Trans-Nationwide Express Plc, CardinalStone.
- WAPIC keeps its ticker. Legal name: Coronation Insurance Plc. Registrar: Coronation Registrars.
- These are not duplicates: TRANSCORP/TRANSPOWER, CAP/UCAP, UCBAL/UCBOND/UCEURO, TAJSUKS1/TAJSUKS2.

**Preliminary leads (to be verified):**

| Ticker | Lead |
|---|---|
| WAPIC | Trading suspended 2026-11-27 ahead of delisting under a Scheme of Arrangement |
| ALEX | Suspended 2026-07-22 (no 2025 accounts) |
| UNIVINSURE | Suspended 2026-08-20 (NAICOM, liquidator) |
| FTGINSURE | On the NGX delisting watchlist |
| FIRSTHOLDCO | Current ticker (not FIRSTHOLDC) |
| SDACCESS | NASD OTC |

**Workstreams:**
1. the 13 low-confidence mappings
2. List B (7)
3. List A (90)
4. the 6 renames
5. suspended and delisted companies

For each company, confirm the ticker, name, registrar, listing status and trading status, with primary evidence.

**Deliverables:**

| | File |
|---|---|
| A | `ngx_ticker_registrar_reconciliation_2026-11-28.csv` |
| B | `ngx_ticker_registrar_corrections_2026-11-28.md` |
| C | `f026c_production_change_log.md` (actions UPDATE/MERGE/RETAIN/FLAG/HOLD; no DELETE without approval) |
| D | `ngx_unresolved_items.md` |

**Constraints:**
- Production is READ-ONLY.
- No import, no schema change, no migration.
- Do not overwrite historical names silently, and do not invent registrar details.
- Never use secondary sites as the sole authority for a ticker.
- A suspended security is not a delisted one.
- Conflicting evidence is kept and escalated.

**Final gate:** STOP, and present the counts and the proposed change log. No production import until the Product Owner explicitly approves the final change log.

The full text is in the session transcript of 2026-11-28; sections 1–12 are summarised above.
