---
type: HO
id: HO-107
title: Claude Web → ChatGPT (Reviewer): F-027 Tutor Marketplace Architecture Review
date: 2026-08-12
from: Claude Web (Architect)
to: ChatGPT (Architecture Reviewer)
protocol: OpenAgile Hybrid Framework v1.0
priority: HIGH
---

# Handover HO-107 — Architecture Review Request

## Context

Zubbyik wants to build a **tutor marketplace platform** that connects tutors, students, and the platform owner. The platform handles session booking, live video classes, automated attendance tracking, and three-way payment splitting.

The default ERPNext UX is too complex. We're building a streamlined React frontend while keeping Frappe/ERPNext as the backend.

## What I Need You to Review

### 1. Architecture Decision: Frappe as Backend

**Decision**: Use Frappe/ERPNext as the backend API layer. Custom `tutor_hub` Frappe app extends the `education` module.

**Tradeoffs considered**:
- Frappe provides: CRUD API, user auth, MariaDB, session management, DocType system
- Frappe adds: complexity, learning curve, Frappe-specific patterns
- Alternative: Custom FastAPI backend (like EPM) — simpler but reimplements auth, ORM, etc.

**My rationale**: Frappe already has the education module (Student, Instructor, Subject, Course, Program). Reusing it avoids reimplementing ~75 DocTypes. The React frontend consumes Frappe's REST API.

**Review request**: Is Frappe the right backend choice for a marketplace? What are the hidden costs?

### 2. Payment Flow: Stripe Connect

**Decision**: Use Stripe Connect for split payments (student → platform → tutor).

**Flow**:
```
Student pays → Stripe Connect → Platform account holds funds
Session completes → Platform calculates split
Platform payout → Tutor's Stripe account
```

**Review request**: 
- Is Stripe Connect the right tool for this 3-sided split?
- Should we hold funds or release immediately after session?
- What about refunds for cancellations?

### 3. Session Verification: Automated Tracking

**Decision**: Auto-track Jitsi join/leave times. If student attends ≥80% of scheduled duration → auto-complete → payment released.

**Review request**:
- Is 80% threshold appropriate?
- What if Jitsi tracking fails (network issues)?
- Should there be a manual override for disputes?

### 4. Live Streaming: Phased Jitsi

**Decision**:
- Phase 1: Free hosted Jitsi (meet.jit.si) — zero cost
- Phase 2: Daily.co API — branded, $0.004/min/participant
- Phase 3: Self-hosted Jitsi — full control, needs ~4GB RAM

**Review request**: Is this phased approach realistic? What are the security/privacy implications of using meet.jit.si for paid classes?

### 5. Multi-Tenancy: Single Site

**Decision**: Single ERPNext site, role-based access (Owner/Tutor/Student). Not multi-site.

**Review request**: For future scaling, should we design for multi-site from day one, or is single-site sufficient for a tutor marketplace?

### 6. Frontend: Reuse tutor-connect-hub

**Decision**: Reuse existing `tutor-connect-hub/` React codebase (React 18, TypeScript, Tailwind, shadcn-ui).

**Review request**: The existing codebase uses React Router DOM 7. Should we migrate to TanStack Router for URL-first routing (matching EPM patterns), or keep React Router for speed?

## Specific Review Questions

1. **Security**: Are there attack vectors in the session → payment flow that I'm missing?
2. **Scalability**: Will this architecture handle 100 concurrent tutors × 50 students each?
3. **Data integrity**: What happens if a session is marked complete but Stripe hasn't processed the payment?
4. **Cancellation policy**: How should we handle cancellations (student cancels, tutor cancels, no-show)?
5. **Edge cases**: What about timezone differences between tutor and student?
6. **Audit trail**: Should every payment state change be logged (like EPM's `admin_audit` table)?
7. **Mobile**: Should the React app be PWA-capable for mobile access?

## Files to Review

- `frappe_docker/plans/F-027-tutor-marketplace.md` — Full feature spec
- `frappe_docker/plans/tutor-marketplace-architecture.md` — Original architecture plan (1253 lines, detailed)
- `frappe_docker/apps/tutor_hub/` — Existing app scaffold
- `frappe_docker/tutor-connect-hub/` — Existing React frontend

## What I Need Back

1. **Approval or concerns** on each architecture decision above
2. **Risk assessment** — what's most likely to go wrong?
3. **Alternative suggestions** if you see a better approach
4. **Security review** of the payment and session flow
5. **Any missing considerations** I haven't thought of

## Constraints (from EPM Governance)

- This is a Zone 2 task — architecture decisions need consensus
- No implementation without specs (F-027 is this spec)
- Payment flow must be auditable (every state change logged)
- Frontend: modal-based CRUD only (no inline editing)
- Deploy via Docker Compose + Traefik on Netcup VPS

---

**Handover prepared by**: Claude Web (Architect)
**Date**: 2026-08-12
**Protocol**: OpenAgile Hybrid Framework v1.0
**Next step**: ChatGPT reviews architecture, returns concerns/approval, then Zone 1 builder implements
