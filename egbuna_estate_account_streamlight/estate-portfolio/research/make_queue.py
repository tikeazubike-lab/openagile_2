"""Build the NGX reconciliation work queue and the per-batch research briefs (HO-160, PO brief workstreams 1-5).

Inputs (all in git): the research file, the read-only names report, the PO brief.
Output: research/queue.json, research/briefs/batch-NN.md. Stdlib only.
"""
import json
import re
import sys
from pathlib import Path

EPM = Path(__file__).resolve().parents[1]
RESEARCH = EPM / "docs/registrars/registrars_contact_details_final.md"
NAMES = EPM / "docs/handovers/HO-160-names-report-2026-11-28.md"
BATCH = 5

WEAK = ["MULTITREX", "SOVRENINS", "CAP", "SCOA", "DAARCOMM", "PRESTIGE", "ALEX", "WAPIC", "RONCHESS",
        "AFROMEDIA", "CUTIX", "NNFM", "VERITASKAP"]
RENAMES = {"WEMABANK": "Wema Bank Plc", "LEARNAFRCA": "Learn Africa Plc", "LIVESTOCK": "Livestock Feeds Plc",
           "TRANSPOWER": "Transcorp Power Plc", "DNMEYER": "Meyer Plc", "ACCESSCORP": "Access Holdings Plc"}
LEADS = {
    "WAPIC": "PO lead: trading suspension announced 2026-11-27 ahead of delisting under a Scheme of Arrangement. Verify whether the suspension is in effect, whether the scheme is complete, whether it is formally delisted, effective dates, and outstanding shareholder entitlements.",
    "ALEX": "PO lead: suspended 2026-07-22 for failing to file 2025 audited accounts. Verify.",
    "UNIVINSURE": "PO lead: suspended 2026-08-20 after NAICOM action and appointment of a liquidator. Verify.",
    "FTGINSURE": "PO lead: on the NGX delisting watchlist. Verify.",
    "FIRSTHOLDCO": "PO lead: FIRSTHOLDCO is the current ticker (not FIRSTHOLDC). Verify.",
    "ACCESSCORP": "Settled: ACCESSCORP = Access Holdings Plc (NGX). The former Access Bank Plc shares are NASD OTC SDACCESS; ACCESS is the obsolete NGX ticker. Never name ACCESSCORP 'Access Bank'. Verify the registrar (research file: Coronation).",
    "TRANSEXPR": "Settled: TRANSEXPR is the official ticker (not TRANEX), Trans-Nationwide Express Plc, CardinalStone. Confirm only.",
    "DNMEYER": "Settled: DNMEYER = Meyer Plc (formerly DN Meyer Plc), Greenwich. The research file lists it under 'MEYER'. Confirm only.",
}


def research_entries():
    text = RESEARCH.read_text()
    m = re.search(r"```json\s*\n(.*?)\n```", text, re.S)
    data = json.loads(m.group(1))
    out = {}
    for reg in data["registrars"]:
        for c in reg.get("clients") or []:
            t = (c.get("ticker") or "").upper()
            if t:
                out.setdefault(t, []).append({
                    "registrar_slug": reg["slug"],
                    "registrar_name": reg.get("legal_name") or reg.get("name") or reg.get("trading_name"),
                    "company_in_file": c.get("company"),
                    "mapping_confidence": c.get("mapping_confidence"),
                    "mapping_flag": c.get("mapping_flag"),
                    "last_evidence_date": c.get("last_evidence_date"),
                    "registrar_as_recorded": c.get("registrar_as_recorded"),
                })
    return out


def epm_names():
    names = {}
    for line in NAMES.read_text().splitlines():
        m = re.match(r'\s+[\d.]+ (\S+): file "(.*)" vs db "(.*)" \(registrar in file', line)
        if m:
            names[m[1]] = m[3]
    return names


def main():
    res, db = research_entries(), epm_names()
    order = WEAK + [t for t in db if t not in WEAK] + [t for t in RENAMES if t not in db and t not in WEAK]
    for t in LEADS:
        if t not in order:
            order.append(t)
    queue = []
    for t in order:
        work = []
        if t in WEAK:
            work.append("workstream 1 (low-confidence mapping held back from the import)")
        if t in db and db[t].upper().replace(" ", "") != t:
            work.append("workstream 2 (List B: EPM has a different full name)")
        elif t in db:
            work.append("workstream 3 (List A: EPM name is just the ticker)")
        if t in RENAMES:
            work.append(f"workstream 4 (proposed rename to '{RENAMES[t]}', approved in principle)")
        queue.append({"ticker": t, "epm_name": db.get(t) or "(not listed in the names report: EPM name already matches the research file)", "research_file": res.get(t, []),
                      "proposed_rename": RENAMES.get(t), "lead": LEADS.get(t), "workstreams": work})
    out = Path(__file__).parent
    (out / "queue.json").write_text(json.dumps(queue, indent=1, ensure_ascii=False))
    (out / "briefs").mkdir(exist_ok=True)
    template = (out / "brief_template.md").read_text()
    batches = [queue[i:i + BATCH] for i in range(0, len(queue), BATCH)]
    for n, b in enumerate(batches, 1):
        name = f"batch-{n:02d}"
        (out / "briefs" / f"{name}.md").write_text(
            template.replace("{{BATCH}}", name).replace("{{COMPANIES}}", json.dumps(b, indent=1, ensure_ascii=False)))
    sys.stdout.write(f"{len(queue)} companies, {len(batches)} batches\n")


if __name__ == "__main__":
    main()
