NGX reconciliation research, batch-10 (HO-160; the Product Owner's brief is `docs/handovers/HO-160-po-reconciliation-brief.md`).

You are a careful financial-data researcher. For each Nigerian listed company below, establish from PRIMARY sources:
- its current NGX ticker;
- its current legal name;
- its current Nigerian share registrar;
- its listing status and its trading status.

Write ONE file, `research/out/batch-10.json`, and nothing else. Do not commit. Do not touch any other file.

SOURCES, in this order:
1. NGX: ngxgroup.com (listed companies, company profile pages, the Daily Official List, X-Compliance reports), and doclib.ngxgroup.com (market bulletins, notices, disclosures).
2. SEC Nigeria: sec.gov.ng.
3. The company's latest audited annual report. Registrar details are usually on the "Corporate information" page.
4. The company's investor-relations page.
5. The registrar's own website.
6. Secondary sites (stock data or news sites) may SUPPORT a finding, but never decide a ticker on their own.

RULES:
- **Ticker:** take it from an NGX record only. Never derive it from the name or from third-party sites.
- **Registrar:** take it from the latest annual report or the company's own disclosure. If you can't establish the current one, set registrar_status "UNVERIFIED".
- **Listing vs trading:** they are different. A suspended security is still listed. A suspension announcement does not mean the company is delisted.
- **Conflicting evidence:** keep both sources and explain the conflict in review_notes. Do not pick one silently.
- **Never guess:** use null or "UNVERIFIED" whenever you are not sure. Every non-null finding needs at least one evidence item.
- **Your time:** about 6 minutes per company. If a site blocks you, try another primary source, then move on.
- **Preserve settled decisions** (field "lead" that starts with "Settled"), unless an authoritative source contradicts them. If one does, say so.
- **Your job is only to research.** No shell commands other than `ls`, `cat research/*`, `jq` and `date`.

OUTPUT: one JSON array, one object per company, in this exact shape:
```json
{
 "ticker": "AS GIVEN",
 "ngx_ticker": "current NGX ticker or null",
 "ticker_status": "CONFIRMED | DIFFERENT | UNVERIFIED",
 "company_name": "current legal name or null",
 "former_names": ["..."],
 "exchange": "NGX | NASD | null",
 "listing_status": "listed | delisted | nasd_otc | unverified",
 "trading_status": "trading | suspended | delisted | inactive | unverified",
 "status_effective_date": "YYYY-MM-DD or null",
 "status_reason": "string or null",
 "registrar_name": "current Nigerian registrar or null",
 "registrar_status": "CONFIRMED | DIFFERENT | UNVERIFIED",
 "evidence": [
  {"claim": "ticker|name|registrar|status", "url": "...", "source_type": "NGX|SEC|annual_report|investor_relations|registrar|secondary", "published": "YYYY-MM-DD or null", "quote": "short exact quote from the page"}
 ],
 "confidence": "high | medium | low",
 "review_notes": "conflicts, doubts, what was blocked"
}
```
- ticker_status DIFFERENT: NGX uses another ticker. Put it in ngx_ticker.
- registrar_status DIFFERENT: the current registrar differs from the research file.
- `last_verified_at` is added by the orchestrator, so leave it out.

Check that the file is valid JSON (`jq . research/out/batch-10.json`). Finish with a 3-line report: companies done, how many are UNVERIFIED, sites that blocked you.

COMPANIES (with what EPM and the registrar research file currently say):
```json
[
 {
  "ticker": "STANBIC",
  "epm_name": "STANBIC",
  "research_file": [
   {
    "registrar_slug": "first-registrars",
    "registrar_name": "First Registrars And Investor Services Limited",
    "company_in_file": "Stanbic IBTC Holdings Plc",
    "mapping_confidence": "High",
    "mapping_flag": "OK",
    "last_evidence_date": "2026-09-30",
    "registrar_as_recorded": "First Registrars And Investor Services Limited"
   }
  ],
  "proposed_rename": null,
  "lead": null,
  "workstreams": [
   "workstream 3 (List A: EPM name is just the ticker)"
  ]
 },
 {
  "ticker": "UPDCREIT",
  "epm_name": "UPDCREIT",
  "research_file": [
   {
    "registrar_slug": "first-registrars",
    "registrar_name": "First Registrars And Investor Services Limited",
    "company_in_file": "UPDC Real Estate Investment Trust",
    "mapping_confidence": "Medium",
    "mapping_flag": "STALE",
    "last_evidence_date": "2024-05-13",
    "registrar_as_recorded": "First Registrars And Investor Services Limited"
   }
  ],
  "proposed_rename": null,
  "lead": null,
  "workstreams": [
   "workstream 3 (List A: EPM name is just the ticker)"
  ]
 },
 {
  "ticker": "BETAGLAS",
  "epm_name": "BETAGLAS",
  "research_file": [
   {
    "registrar_slug": "greenwich",
    "registrar_name": "Greenwich Registrars & Data Solutions Limited",
    "company_in_file": "Beta Glass Plc",
    "mapping_confidence": "High",
    "mapping_flag": "OK",
    "last_evidence_date": "2026-04-01",
    "registrar_as_recorded": "Greenwich Registrars & Data Solutions Limited"
   }
  ],
  "proposed_rename": null,
  "lead": null,
  "workstreams": [
   "workstream 3 (List A: EPM name is just the ticker)"
  ]
 },
 {
  "ticker": "CHELLARAM",
  "epm_name": "CHELLARAM",
  "research_file": [
   {
    "registrar_slug": "greenwich",
    "registrar_name": "Greenwich Registrars & Data Solutions Limited",
    "company_in_file": "Chellarams Plc",
    "mapping_confidence": "High",
    "mapping_flag": "OK",
    "last_evidence_date": "2026-06-25",
    "registrar_as_recorded": "Greenwich Registrars & Data Solutions Limited"
   }
  ],
  "proposed_rename": null,
  "lead": null,
  "workstreams": [
   "workstream 3 (List A: EPM name is just the ticker)"
  ]
 },
 {
  "ticker": "ETI",
  "epm_name": "ETI",
  "research_file": [
   {
    "registrar_slug": "greenwich",
    "registrar_name": "Greenwich Registrars & Data Solutions Limited",
    "company_in_file": "Ecobank Transnational Incorporated",
    "mapping_confidence": "High",
    "mapping_flag": "OK",
    "last_evidence_date": "2026-04-15",
    "registrar_as_recorded": "Greenwich Registrars & Data Solutions Limited"
   }
  ],
  "proposed_rename": null,
  "lead": null,
  "workstreams": [
   "workstream 3 (List A: EPM name is just the ticker)"
  ]
 }
]
```
