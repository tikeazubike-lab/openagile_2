---
type: ADR
id: ADR-XXX
title: [Decision Title]
status: PROPOSED | ACCEPTED | SUPERSEDED | DEPRECATED
created: YYYY-MM-DD
updated: YYYY-MM-DD
deciders: [Claude, Grok, Owner]
supersedes: null | ADR-YYY
---

# ADR-XXX — [Decision Title]
> **Type**: Architecture Decision · **Status**: ACCEPTED

---

## Context

[What situation, constraint, or problem forced this decision?
Be specific. Reference the feature or phase where this arose.
Example: "In Phase 2A, we needed to choose how to store JWT tokens.
The system has a browser-based React frontend and a FastAPI backend.
XSS attacks are a concern because the app handles financial data."]

---

## Decision

[State the decision in ONE sentence — active voice, no hedging.]

Example:
> JWT tokens are stored in httpOnly cookies with a 30-day max_age,
> never in localStorage.

---

## Rationale

[Why this option over the alternatives? Be direct.
Connect it to the specific constraints from Context above.]

Example:
> httpOnly cookies prevent JavaScript access entirely, eliminating
> XSS risk. localStorage tokens can be stolen by any injected script.
> For a financial app handling portfolio data, this risk is unacceptable.
> The 30-day lifetime avoids daily re-login friction for a personal
> daily-use tool.

---

## Alternatives Considered

| Option | Rejected Because |
|--------|-----------------|
| localStorage JWT | Vulnerable to XSS — any script injection can steal token |
| Session-only cookie (no max_age) | User must re-login every browser close — unacceptable for daily use |
| Server-side sessions | Adds Redis/DB session storage dependency — unnecessary complexity |

---

## Consequences

**Positive**:
- [What gets better as a result of this decision]
- [What becomes simpler]

**Negative / Trade-offs**:
- [What gets harder]
- [What this prevents you from doing later]

**Risks**:
- [What could go wrong with this choice]
- [What would force a reversal]

---

## Implementation Notes

[Any specific implementation details agents must follow as a result
of this decision. These become invariants in .context/architecture.md]

Example:
```python
# auth.py — always set these exact cookie attributes
response.set_cookie(
    key="epm_token",
    value=token,
    httponly=True,       # Never False
    secure=True,         # Never False in production
    samesite="strict",   # Never 'lax' or 'none'
    max_age=60*60*24*30, # Always 30 days — never session-only
)
```

---

## Invariant (add to .context/architecture.md)

```
JWT in httpOnly cookie — never localStorage
Cookie: max_age=2592000, httponly=True, secure=True, samesite="strict"
```

---

## Status History

| Date | Status | Note |
|------|--------|------|
| YYYY-MM-DD | PROPOSED | Initial draft |
| YYYY-MM-DD | ACCEPTED | Approved by [deciders] |
