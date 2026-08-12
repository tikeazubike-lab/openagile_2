---
type: FR
id: F-027
title: Tutor Marketplace Platform (EduHub)
status: DRAFT
version: 1.0
updated: 2026-08-12
author: Claude Web (Architect)
---

# F-027 — Tutor Marketplace Platform

## 1. Purpose

Build a multi-sided tutor marketplace on ERPNext/Frappe that connects tutors (staff), students, and the platform owner. The platform handles session booking, live video classes, automated attendance tracking, and three-way payment splitting (student pays → platform takes % → tutor receives payout).

The default ERPNext UX is too complex for this use case. This feature replaces it with a streamlined React frontend while keeping Frappe as the backend.

## 2. Scope

### In Scope
- Tutor profile management (extends `education.Instructor`)
- Student profile management (extends `education.Student`)
- Session scheduling and booking
- Live video integration (Jitsi — phased)
- Automated session tracking (join/leave → auto-complete)
- Pay-per-session and course package purchases
- Stripe Connect for split payments
- Platform fee calculation and tutor payouts
- Three role-based dashboards (Owner, Tutor, Student)
- Tutor discovery and search

### Out of Scope
- Multi-site deployment (single site only — `tutor.zubbystudio.site`)
- Custom video streaming infrastructure (use Jitsi hosted/free tier first)
- Mobile native apps (web-first, responsive)
- ERPNext HR module integration (salaries handled separately)
- Scholarship or financial aid workflows

## 3. Data Model

### Core DocTypes

| DocType | Extends | Purpose |
|---------|---------|---------|
| `Tutor Profile` | `education.Instructor` | Tutor identity, rates, availability, payment info |
| `Student Profile` | `education.Student` | Student identity, guardian info, learning goals |
| `Session Schedule` | New | Core entity — links tutor + student + time + meeting |
| `Payment Transaction` | New | Every payment: student → platform → tutor split |
| `Course Package` | New | Bundled sessions with discount pricing |
| `Package Purchase` | New | Student's package purchase record |
| `Session Attendance` | New | Automated join/leave tracking |
| `Marketplace Settings` | New (Single) | Platform config: fee %, payout rules |

### Tutor Profile Fields

| Field | Type | Description |
|-------|------|-------------|
| `user` | Link → User | Frappe user account |
| `instructor` | Link → Instructor | Reference to education app |
| `bio` | Text | Professional biography |
| `subjects` | Table → Tutor Subject | Subjects taught |
| `hourly_rate` | Currency | Base hourly rate |
| `availability` | Table → Tutor Availability | Weekly schedule |
| `payment_method` | Select | Stripe, Bank Transfer |
| `stripe_account_id` | Data | Stripe Connect account |
| `is_verified` | Check | Admin verification |
| `rating` | Float | Average rating (0-5) |
| `total_reviews` | Int | Review count |
| `status` | Select | Active, Suspended, Pending |

### Session Schedule Fields

| Field | Type | Description |
|-------|------|-------------|
| `tutor` | Link → Tutor Profile | Who teaches |
| `student` | Link → Student Profile | Who attends |
| `subject` | Link → Subject | What's taught |
| `scheduled_date` | Date | When |
| `start_time` | Time | Start |
| `end_time` | Time | End |
| `duration_minutes` | Int | Calculated duration |
| `session_type` | Select | 1-on-1, Group, Online |
| `price` | Currency | Session fee |
| `meeting_link` | Data | Jitsi room URL |
| `status` | Select | Scheduled, In Progress, Completed, Cancelled, No Show |
| `attendance_confirmed` | Check | Auto-set by tracking |
| `package_purchase` | Link | If paid via package |

### Payment Transaction Fields

| Field | Type | Description |
|-------|------|-------------|
| `session` | Link → Session Schedule | Related session |
| `tutor` | Link → Tutor Profile | Tutor receiving |
| `student` | Link → Student Profile | Student paying |
| `amount` | Currency | Total amount |
| `platform_fee` | Currency | Platform commission |
| `tutor_payout` | Currency | Amount to tutor |
| `payment_gateway` | Select | Stripe |
| `transaction_id` | Data | Gateway transaction ID |
| `status` | Select | Pending, Completed, Failed, Refunded |
| `payout_status` | Select | Pending, Paid |
| `payout_date` | Date | When tutor was paid |
| `created_at` | Datetime | Transaction timestamp |

### Marketplace Settings (Single DocType)

| Field | Type | Description |
|-------|------|-------------|
| `platform_fee_percentage` | Percent | Default: 15% |
| `minimum_payout_amount` | Currency | Minimum for tutor payout |
| `payout_frequency` | Select | Weekly, Bi-weekly, Monthly |
| `require_tutor_verification` | Check | Admin must verify tutors |
| `auto_complete_threshold` | Int | % of duration to auto-complete (default: 80) |

## 4. API Contract

### Frappe REST API (Standard CRUD)
```
GET    /api/resource/Tutor Profile
POST   /api/resource/Tutor Profile
PUT    /api/resource/Tutor Profile/{name}
DELETE /api/resource/Tutor Profile/{name}
```

### Custom Whitelisted Endpoints

| Method | Path | Request | Response | Purpose |
|--------|------|---------|----------|---------|
| POST | `tutor_marketplace.api.book_session` | `{tutor, student, subject, date, time, type}` | `{session: {name, meeting_link, status}}` | Book + create meeting |
| POST | `tutor_marketplace.api.complete_session` | `{session_name}` | `{payment: {amount, tutor_payout, platform_fee}}` | Mark complete + trigger payout |
| GET | `tutor_marketplace.api.get_tutor_schedule` | `{tutor_name, start_date, end_date}` | `[{date, slots: [{time, available}]}]` | Tutor availability |
| GET | `tutor_marketplace.api.get_student_sessions` | `{student_name, status?}` | `[{session, tutor, subject, date, status}]` | Student's sessions |
| POST | `tutor_marketplace.api.calculate_payouts` | `{period_start, period_end}` | `[{tutor, total, fee, payout}]` | Batch payout calc |
| POST | `tutor_marketplace.api.create_meeting_link` | `{session_name}` | `{meeting_link, room_name}` | Generate Jitsi URL |
| POST | `tutor_marketplace.api.purchase_package` | `{tutor, student, package_id}` | `{purchase, sessions_remaining}` | Buy package |
| GET | `tutor_marketplace.api.get_owner_dashboard` | `{}` | `{revenue, sessions, tutors, students}` | Owner metrics |

## 5. Frontend Requirements

### Tech Stack (reuse tutor-connect-hub)
- React 18 + TypeScript
- Tailwind CSS 4 + shadcn/ui
- TanStack Query 5 (server state)
- React Router DOM 7 (routing)
- Recharts (dashboards)
- frappe-js-sdk (API client)
- Framer Motion (animations)

### Role-Based Dashboards

**Owner Dashboard** (`/owner/*`)
- Revenue overview (platform fees, total transactions)
- Active tutors and students count
- Session completion rate
- Payout management
- Marketplace settings

**Tutor Dashboard** (`/tutor/*`)
- My sessions (upcoming, completed, cancelled)
- Earnings summary
- Availability management
- Student reviews
- Profile management

**Student Dashboard** (`/student/*`)
- My classes (upcoming, past)
- Book a session (search tutors → pick time → pay)
- My packages (remaining sessions)
- Payment history
- Profile management

### Key UX Simplifications vs ERPNext

| ERPNext Default | EduHub React |
|----------------|--------------|
| 30+ field forms | 3-5 field focused forms |
| Module-based navigation | Role-based dashboards |
| Inline editing everywhere | Modal-based CRUD only (HO-023 pattern) |
| Complex sidebar | Clean top nav + dashboard cards |
| No video integration | Embedded Jitsi per session |
| Manual attendance | Auto-tracking via join/leave |

### Route Structure

```
/                          → Landing page (tutor discovery)
/login                     → Auth (Frappe session)
/register/student          → Student registration
/register/tutor            → Tutor registration

/owner/dashboard           → Owner overview
/owner/tutors              → Manage tutors
/owner/payments            → Payout management
/owner/settings            → Platform config

/tutor/dashboard           → Tutor overview
/tutor/schedule            → Availability
/tutor/sessions            → Session list
/tutor/earnings            → Payment history

/student/dashboard         → Student overview
/student/browse            → Find tutors
/student/book              → Book session
/student/sessions          → My sessions
/student/packages          → My packages
/student/payments          → Payment history
```

## 6. Acceptance Criteria

| AC ID | Scenario | Given | When | Then |
|-------|----------|-------|------|------|
| AC-001 | Tutor creates profile | Tutor is logged in | Fills profile form | Profile created, visible to students |
| AC-002 | Student books session | Student logged in, tutor available | Selects tutor, date, time | Session created, meeting link generated |
| AC-003 | Session auto-completes | Session in progress | Duration reaches 80% of scheduled | Status → Completed, payment released |
| AC-004 | Platform fee calculated | Session completes | Payment processing | Platform gets %, tutor gets remainder |
| AC-005 | Package purchase | Student logged in | Buys 10-session package | Package active, sessions_remaining = 10 |
| AC-006 | Package session deducted | Student uses package session | Session completes from package | sessions_remaining decremented |
| AC-007 | Owner sees revenue | Owner logged in | Views dashboard | Total revenue, fees, payouts displayed |
| AC-008 | Tutor availability | Tutor logged in | Sets weekly availability | Students can book during available slots |
| AC-009 | Automated attendance | Session starts | Student joins Jitsi | Attendance recorded with join time |
| AC-010 | Tutor payout | Payout period due | System calculates | Tutor receives payment minus platform fee |

## 7. Dependencies

| Dependency | Type | Notes |
|------------|------|-------|
| `education` app | Frappe app | Already installed — provides Student, Instructor, Subject |
| `tutor_hub` app | Custom app | Existing scaffold at `frappe_docker/apps/tutor_hub/` |
| `tutor-connect-hub` | Frontend | Existing React codebase to reuse |
| Stripe Connect | External API | Payment splitting |
| Jitsi Meet | External/Hosted | Video calls (free tier first) |
| MariaDB | Database | Shared via Frappe |

## 8. Open Questions

| ID | Question | Default | Owner |
|----|----------|---------|-------|
| OQ-F027-1 | Stripe Connect or Stripe standard for split payments? | Stripe Connect (better for marketplace) | Zubbyik |
| OQ-F027-2 | Should students be able to rate tutors after session? | Yes — 1-5 stars + comment | Zubbyik |
| OQ-F027-3 | What happens if student doesn't show up? | Status → No Show, partial refund | Zubbyik |
| OQ-F027-4 | Should tutor set their own rates or use platform default? | Both — tutor rate overrides platform default | Zubbyik |
| OQ-F027-5 | Group sessions — how many students max? | Configurable per session (default 10) | Zubbyik |
