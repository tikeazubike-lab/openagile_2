# EPM Bug Report
# Copy this template, fill it in, paste to any agent (Hermes, OpenCode, ChatGPT)
# The agent will know exactly what to do without any additional context

---

## BUG REPORT — EPM

**Reported by**: Malachy E. (Product Owner)
**Date**: [YYYY-MM-DD]
**Environment**: testdrive.epm.zubbystudio.shop
**Severity**: P0 (blocking) | P1 (usability) | P2 (polish)

---

## What I Did
[Exact steps you took — be specific]

Example:
1. Logged in as admin
2. Navigated to /holdings
3. Clicked [+ Add Holding] button
4. Selected DANGCEM from dropdown
5. Entered 100 shares, ₦400.00 avg cost
6. Clicked [Save as Draft]

---

## What I Expected
[What should have happened]

Example:
A new DANGCEM row should appear in the Holdings table with a DRAFT badge.

---

## What Actually Happened
[Exact error or wrong behaviour — paste error messages verbatim]

Example:
The drawer closed but no new row appeared.
Browser console shows: "TypeError: Cannot read properties of undefined (reading 'map')"
Network tab shows: POST /api/v1/admin/holdings returned 500

---

## Layer
[Tick the layer where the problem appears]

- [ ] [DB] — data wrong or missing in database
- [ ] [API] — endpoint returns wrong status, shape, or data
- [ ] [UI] — page renders wrong, crashes, or shows stale data
- [ ] Unknown — needs diagnosis

---

## Evidence
[Paste any of these you have]

Console error:
```
[paste here]
```

Network request payload (DevTools → Network → Request tab):
```json
[paste here]
```

Network response body (DevTools → Network → Response tab):
```json
[paste here]
```

Server logs (if accessible):
```
[paste here]
```

---

## Feature Affected
F-XXX — [Feature Name]

---

## Agent Instructions
[The agent reads this section and knows exactly what to do]

1. This is a bug report for the EPM project at:
   /home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio/

2. Read .context/AGENTS.md and .context/current-issues.md before doing anything.

3. Follow the debug protocol from .context/ai-workflow-rules.md:
   - Identify the exact layer [DB/API/UI]
   - Capture exact error from server logs or network tab
   - Trace to exact file and line
   - Write root cause analysis
   - Propose ONE fix — do not implement yet

4. Output format required:
   - Root cause: [file] line [N] — [what is wrong and why]
   - Proposed fix: [exact change — file, line, what to change]
   - Test to verify: [specific AT checklist item or curl command]

5. Do NOT implement the fix until the product owner confirms.
   Write "AWAITING APPROVAL" at the end of your analysis.

6. After approval and fix: update .context/current-issues.md
   and write HO-XXX.md in docs/handovers/

---

## Related
- Feature spec: .context/feature-specs/F-XXX.md
- Previous AT: docs/testing/acceptance/AT-XXX.md
- Related HO: docs/handovers/HO-XXX.md
