# HO-159 artefacts index (PR #10: F-026 dashboard + F-026b reminders)

Main document: `HO-159-pr10-completion-brief.md` (rulings, Parts A–G, review responses).
Rule (Product Owner, 2026-11-24): every handover artefact passed to another agent is saved in
`docs/handovers/`, prefixed with the HO number it belongs to. No new HO numbers are used for attachments.

## Briefs sent to agents (verbatim)
| File | Agent / model | Purpose |
|---|---|---|
| HO-159-brief-dispatch-smoke-test.md, -2.md | builder | dispatch.sh smoke tests (permissions) |
| HO-159-brief-partA-backend-tests.md | builder (deepseek-v4.1-flash) | Part A: F-026b backend tests |
| HO-159-brief-partB-frontend-port.md | frontend (mimo-v2.6-pro) | Part B: port /settings/registrars, route tree |
| HO-159-brief-partC-dashboard.md | frontend (mimo-v2.6-pro) | Part C: RegistrarsDashboard |
| HO-159-brief-partD-vitest-config.md | builder (mimo-v2.6-flash) | Part D: vitest picks up src/**/__tests__ |
| HO-159-brief-review-deepseek.md | reviewer (deepseek-v4-pro) | advisory review, Parts A–D |
| HO-159-brief-partE1-E3-backend-fixes.md | builder (mimo-v2.6-flash) | Part E1–E3, first run (timed out) |
| HO-159-brief-partE1-E3-retry.md | builder (mimo-v2.6-flash) | Part E1–E3 retry with explicit interpreter |
| HO-159-brief-partE4-frontend-cleanups.md | frontend (mimo-v2.6-pro) | Part E4 |
| HO-159-brief-partF-fix-round2.md | builder (mimo-v2.6-flash) | Part F: fix round 2 (AC-6 leak etc.) |
| HO-159-brief-investigate-registrars-playwright.md | frontend (prepared, not dispatched) | Playwright investigation of /registrars |
| HO-159-brief-partG-tabs.md | frontend (mimo-v2.6-pro) | Part G: tabs on /registrars |
| HO-159-brief-review-deepseek-partG.md | reviewer (deepseek-v4-pro) | advisory review, Part G |

## Agent reports (raw final output, as returned)
HO-159-report-partA.md, -partB.md, -partC.md, -partD.md, -partE123.md (timed-out run),
-partE123b.md, -partE4.md, -partF.md, -reviews-parts-A-D.md (auditor + DeepSeek, Parts A–D).
Part G reports are summarised in the main document ("Part G review responses").

## PR texts
HO-159-pr10-description.md (PR #10 body), HO-159-pr10-comment-partG.md (Part G update comment).
