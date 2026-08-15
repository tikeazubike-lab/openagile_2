---
type: HO
id: HO-109
title: OpenCode → New Session: Frontend Redesign Based on Target Image
date: 2026-08-16
from: OpenCode (MiMo v2.5 Pro)
to: New Session (any agent that can view images)
protocol: OpenAgile Hybrid Framework v1.0
priority: HIGH
---

# Handover HO-109 — Frontend Redesign

## Why This Handover

The previous agent could NOT view images. The user has a target design screenshot that needs to be implemented. A new session with image-viewing capability is required.

---

## What Was Built (All Complete)

### Backend — Frappe v16 (DONE)

- **Site**: `https://tutor.zubbystudio.site/` — fresh Frappe v16 site
- **Database**: `tutor_db` on shared MariaDB
- **Apps installed**: frappe 16.30.0, erpnext 16.31.1, education 15.0.0, tutor_hub 0.0.1
- **11 DocTypes**: Tutor Profile, Session Schedule, Payment Transaction, Payment Audit Event, Course Package, Package Purchase, Session Attendance, Marketplace Settings, Tutor Subject, Tutor Availability, Tutor Qualification
- **Stripe webhook**: `payments.py` + `stripe_client.py` — handles payment_intent, transfer, refund, dispute events with idempotency + immutable audit trail
- **Booking**: `book_session()` with `SELECT ... FOR UPDATE` for atomic slot reservation
- **Login**: `Administrator` / `admin`

### Frontend — React 18 (NEEDS REDESIGN)

- **Location**: `/home/zubbyik/openagile_2/frappe_docker/tutor-connect-hub/`
- **Tech**: React 18, TypeScript, Vite 7, Tailwind CSS 4, shadcn/ui, TanStack Query 5, React Router 7, Recharts, Lucide React
- **50 source files**, indigo color scheme (#4F46E5)
- **Deployed** at `https://tutor.zubbystudio.site/` via custom nginx config

### Infrastructure (DONE)

- Traefik routing with Cloudflare SSL
- Custom nginx config serves React SPA at `/`, Frappe API at `/api`, desk at `/desk`
- Desk modules restricted to Education + Tutor Hub only (all ERPNext clutter hidden)
- All pushed to GitHub `test` branch

---

## What Needs To Be Done

### Step 1: View the target design

Read the image at `/home/zubbyik/openagile_2/website_redesign_2.png` and describe what you see in detail (layout, colors, typography, sections, components).

### Step 2: Create a redesign spec

Write a feature spec (F-028) documenting the target design with:
- Layout structure (header, hero, sections in order)
- Color palette (hex codes)
- Typography (fonts, sizes)
- Key UI components
- Responsive behavior

### Step 3: Implement the redesign

Update these files in `/home/zubbyik/openagile_2/frappe_docker/tutor-connect-hub/`:

| File | What to change |
|------|---------------|
| `src/components/home/HeroSection.tsx` | Hero area — layout, text, imagery |
| `src/components/home/SubjectsSection.tsx` | Subject/category cards |
| `src/components/home/HowItWorksSection.tsx` | Process steps |
| `src/components/home/TestimonialsSection.tsx` | Social proof section |
| `src/components/home/CTASection.tsx` | Call to action |
| `src/components/layout/Header.tsx` | Top navigation |
| `src/components/layout/Footer.tsx` | Footer |
| `src/index.css` | Global styles, colors, fonts |
| `src/types/index.ts` | TypeScript interfaces (if new data shapes) |
| `index.html` | Title, meta, fonts |

### Step 4: Build and deploy

```bash
cd /home/zubbyik/openagile_2/frappe_docker/tutor-connect-hub
npm run build
cp -r dist/* /home/zubbyik/openagile/frappe_docker/tutor-connect-hub/dist/
cd /home/zubbyik/openagile/frappe_docker
docker compose -f compose.yaml -f overrides/compose.databases.yaml -f overrides/compose.external-traefik.yaml -f overrides/compose.persist-apps.yaml -f overrides/compose.frontend-custom-apps.yaml -f overrides/compose.tutor-frontend.yaml up -d --force-recreate frontend
```

### Step 5: Commit and push

```bash
cd /home/zubbyik/openagile_2
git add frappe_docker/tutor-connect-hub/
git commit -m "feat: redesign landing page to match target design (F-028)"
git push origin test
```

---

## Architecture Decisions (from HO-108 ChatGPT review — DO NOT REVISIT)

| Decision | Value |
|----------|-------|
| Backend | Frappe/ERPNext v16 (not FastAPI) |
| Frontend router | React Router 7 (not TanStack Router) |
| Multi-tenancy | Single site, role-based (Owner/Tutor/Student) |
| Payments | Stripe Connect, separate charges/transfers |
| Video | Jitsi (meet.jit.si for pilot) |
| Session states | SCHEDULED → IN_PROGRESS → ATTENDANCE_REVIEW → COMPLETED → PAYOUT_ELIGIBLE |
| Payment states | Independent from session state |
| Browser authority | NEVER trusted for payment/attendance/status |
| Auth | Frappe session cookies (not JWT) |
| CRUD pattern | Modal-based only (no inline row editing) |

---

## Key File Locations

| Purpose | Path |
|---------|------|
| Target design image | `/home/zubbyik/openagile_2/website_redesign_2.png` |
| Feature spec | `/home/zubbyik/openagile_2/frappe_docker/plans/F-027-tutor-marketplace.md` |
| ChatGPT review | `/home/zubbyik/openagile_2/frappe_docker/plans/HO-108—F-027-Tutor-Marketplace-Architecture-Review.md` |
| Frontend source | `/home/zubbyik/openagile_2/frappe_docker/tutor-connect-hub/src/` |
| Backend app | `/home/zubbyik/openagile_2/frappe_docker/apps/tutor_hub/` |
| nginx config | `/home/zubbyik/openagile_2/frappe_docker/configs/nginx/frappe-tutor.conf` |
| Compose override | `/home/zubbyik/openagile_2/frappe_docker/overrides/compose.tutor-frontend.yaml` |
| VPS deployment path | `/home/zubbyik/openagile/frappe_docker/` |

---

## Current Color Scheme (to be replaced)

```css
--primary: #4F46E5 (indigo)
--background: #ffffff
--foreground: #0f172a
```

---

## Constraints (from AGENTS.md)

- Branch: `test` (never commit to `main`)
- Gate 2: PR required with Zubbyik's explicit approval to merge
- Monetary API values always returned as JSON strings
- Migrations: additive only, never destructive
- No new Postgres instances — reuse shared PostgreSQL 15
- All HTTP/HTTPS through Traefik

---

## Login

| Field | Value |
|-------|-------|
| URL | `https://tutor.zubbystudio.site/desk` |
| Username | `Administrator` |
| Password | `admin` |

---

## How to Start the New Session

```
Read /home/zubbyik/openagile_2/frappe_docker/plans/HO-109-opencode-to-new-session-frontend-redesign.md for full context. Then read the target design image at /home/zubbyik/openagile_2/website_redesign_2.png and implement the frontend redesign following the steps in the handover.
```

---

**Handover prepared by**: OpenCode (MiMo v2.5 Pro)
**Date**: 2026-08-16
**Protocol**: OpenAgile Hybrid Framework v1.0
**Next step**: New session views image, creates F-028 spec, implements redesign, builds, deploys, commits
