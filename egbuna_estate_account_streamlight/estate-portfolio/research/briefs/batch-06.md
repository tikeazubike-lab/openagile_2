NGX reconciliation research, batch-06 (HO-160; the Product Owner's brief is `docs/handovers/HO-160-po-reconciliation-brief.md`).

You are a careful financial-data researcher. For each Nigerian listed company below, establish from PRIMARY sources:
- its current NGX ticker;
- its current legal name;
- its current Nigerian share registrar;
- its listing status and its trading status.

Write ONE file, `research/out/batch-06.json`, and nothing else. Do not commit. Do not touch any other file.

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

Check that the file is valid JSON (`jq . research/out/batch-06.json`). Finish with a 3-line report: companies done, how many are UNVERIFIED, sites that blocked you.

COMPANIES (with what EPM and the registrar research file currently say):
```json
[
 {
  "ticker": "REGALINS",
  "epm_name": "REGALINS",
  "research_file": [
   {
    "registrar_slug": "meristem",
    "registrar_name": "Meristem Registrars & Probate Services Ltd",
    "company_in_file": "Regency Alliance Insurance Plc",
    "mapping_confidence": "High",
    "mapping_flag": "OK",
    "last_evidence_date": "2026-07-28",
    "registrar_as_recorded": "Meristem Registrars & Probate Services Ltd"
   }
  ],
  "proposed_rename": null,
  "lead": null,
  "workstreams": [
   "workstream 3 (List A: EPM name is just the ticker)"
  ]
 },
 {
  "ticker": "TANTALIZER",
  "epm_name": "TANTALIZER",
  "research_file": [
   {
    "registrar_slug": "meristem",
    "registrar_name": "Meristem Registrars & Probate Services Ltd",
    "company_in_file": "Tantalizers Plc",
    "mapping_confidence": "High",
    "mapping_flag": "OK",
    "last_evidence_date": "2026-06-25",
    "registrar_as_recorded": "Meristem Registrars & Probate Services Ltd"
   }
  ],
  "proposed_rename": null,
  "lead": null,
  "workstreams": [
   "workstream 3 (List A: EPM name is just the ticker)"
  ]
 },
 {
  "ticker": "BUACEMENT",
  "epm_name": "BUACEMENT",
  "research_file": [
   {
    "registrar_slug": "africa-prudential",
    "registrar_name": "AFRICA PRUDENTIAL PLC",
    "company_in_file": "BUA Cement Plc",
    "mapping_confidence": "High",
    "mapping_flag": "OK",
    "last_evidence_date": "2026-02-27",
    "registrar_as_recorded": "Africa Prudential Plc"
   }
  ],
  "proposed_rename": null,
  "lead": null,
  "workstreams": [
   "workstream 3 (List A: EPM name is just the ticker)"
  ]
 },
 {
  "ticker": "BUAFOODS",
  "epm_name": "BUAFOODS",
  "research_file": [
   {
    "registrar_slug": "africa-prudential",
    "registrar_name": "AFRICA PRUDENTIAL PLC",
    "company_in_file": "BUA Foods Plc",
    "mapping_confidence": "High",
    "mapping_flag": "OK",
    "last_evidence_date": "2026-03-30",
    "registrar_as_recorded": "Africa Prudential Plc"
   }
  ],
  "proposed_rename": null,
  "lead": null,
  "workstreams": [
   "workstream 3 (List A: EPM name is just the ticker)"
  ]
 },
 {
  "ticker": "CHAMPION",
  "epm_name": "CHAMPION",
  "research_file": [
   {
    "registrar_slug": "africa-prudential",
    "registrar_name": "AFRICA PRUDENTIAL PLC",
    "company_in_file": "Champion Breweries Plc",
    "mapping_confidence": "Medium",
    "mapping_flag": "SINGLE-SOURCE",
    "last_evidence_date": "2026-02-27",
    "registrar_as_recorded": "Africa Prudential Plc"
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
