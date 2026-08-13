# HO-108 — F-027 Tutor Marketplace Architecture Review → OpenCode Implementation Handover

**From:** ChatGPT — Architecture Reviewer
**To:** OpenCode [Mimo 2.5] — Zone 1 Builder
**Related Feature:** F-027 — Tutor Marketplace Platform (EduHub)
**Related Handover:** HO-107
**Protocol:** OpenAgile Hybrid Framework v1.0
**Priority:** HIGH
**Status:** Architecture conditionally approved — implementation may proceed only after the specification updates below are incorporated.

---

# 1. Executive Decision

The overall architecture is **conditionally approved**.

The selected stack is sound:

* Frappe/ERPNext backend
* Custom `tutor_hub` Frappe application
* React 18 + TypeScript frontend
* React Router 7
* TanStack Query
* Stripe Connect
* Jitsi
* Docker Compose + Traefik
* Single Frappe site

Do **not** replace Frappe with FastAPI.

Do **not** migrate React Router 7 to TanStack Router.

Do **not** introduce multi-site architecture.

However, implementation must not treat the following as simple CRUD relationships:

```text
Session completion
Payment completion
Tutor payout
Attendance
Refunds
Cancellations
```

These require explicit domain state machines and server-side business commands.

The largest architectural risk is **not Frappe scalability**. It is **financial-state correctness combined with unreliable real-world session/attendance events**.

---

# 2. Critical Architectural Correction

The original conceptual flow was:

```text
Student pays
    ↓
Platform holds funds
    ↓
Session completes
    ↓
Platform calculates split
    ↓
Tutor payout
```

This is acceptable as a business requirement, but the implementation must NOT make:

```text
Session.status = Completed
```

automatically equivalent to:

```text
Payment.status = Completed
Payout.status = Paid
```

These must be independent state machines.

Recommended flow:

```text
                     SESSION
                        │
                        ▼
                   ATTENDANCE
                        │
                        ▼
              COMPLETION ELIGIBILITY
                        │
                        ▼
                    COMPLETED
                        │
                        ▼
                PAYOUT ELIGIBLE
                        │
                        ▼
                     PAYMENT
                        │
                        ▼
                  STRIPE TRANSFER
                        │
                        ▼
                     PAID OUT
```

Payment failure, refund, dispute, or payout failure must not corrupt the session state.

---

# 3. Frappe Backend — APPROVED

## Decision

Keep Frappe/ERPNext as the backend.

The existing Education module already provides important domain concepts:

* Student
* Instructor
* Subject
* Course
* Program
* User/authentication
* permissions
* DocTypes
* ORM
* background jobs
* administrative tooling

Reimplementing these in FastAPI would increase development and maintenance cost without providing enough value for F-027.

## Architectural Rule

Do NOT expose sensitive marketplace business state through unrestricted generic DocType CRUD.

For example, this must NOT be allowed:

```http
PUT /api/resource/Session Schedule/SESSION-0001
```

with:

```json
{
  "status": "Completed",
  "attendance_confirmed": 1
}
```

The client must not directly manipulate authoritative financial/session fields.

Use domain commands such as:

```text
book_session()
cancel_session()
start_session()
record_attendance()
evaluate_session_completion()
mark_session_disputed()
approve_refund()
release_payout()
```

Generic REST CRUD should primarily be used for safe reads and controlled profile/settings operations.

---

# 4. Stripe Connect — APPROVED WITH REQUIRED DESIGN CHANGE

Stripe Connect is the correct general architecture for a marketplace.

However, because the business requires delaying tutor payment until after the session outcome is known, the preferred Connect model is:

> **Separate charges and transfers**

Conceptually:

```text
Student
   │
   ▼
Stripe charge
   │
   ▼
Platform Stripe balance
   │
   ├── platform commission
   │
   └── tutor amount
           │
           │ session becomes payout eligible
           ▼
      Stripe transfer
           │
           ▼
         Tutor
```

Do not assume destination charges are appropriate if funds must remain under platform control until session completion.

---

# 5. Stripe Webhooks Are Authoritative

The browser must NEVER be the authoritative source for payment success.

Incorrect:

```text
React
  ↓
"Payment successful"
  ↓
Frappe marks Payment = Completed
```

Correct:

```text
Student
  ↓
Stripe
  ↓
Stripe webhook
  ↓
Verify webhook signature
  ↓
Check idempotency
  ↓
Persist event
  ↓
Update Payment Transaction
```

The payment subsystem must handle asynchronous Stripe events.

Every processed Stripe event must have a unique persisted identifier.

Example:

```text
stripe_event_id
event_type
received_at
processed_at
processing_status
```

---

# 6. Payment Idempotency

Payment operations must be idempotent.

The system must tolerate:

* duplicate webhook delivery
* worker retries
* HTTP retries
* browser refreshes
* network failures
* Stripe event replay
* payout worker restart

Example:

```text
Stripe Event
     │
     ▼
Already processed?
   /       \
 YES        NO
 │           │
Ignore      Process
             │
             ▼
        Persist event
```

Never create a second payout because a worker was restarted.

---

# 7. Payment Transaction Model

The existing model:

```text
amount
platform_fee
tutor_payout
transaction_id
status
payout_status
```

is insufficient for production financial reconciliation.

The implementation should support, at minimum:

```text
internal_transaction_id
session
student
tutor
currency

gross_amount
stripe_fee
platform_fee
tutor_amount

payment_status
payment_intent_id
charge_id

payout_status
transfer_id
payout_id

refund_status
refunded_amount

dispute_status

created_at
updated_at
```

Do not remove the simpler F-027 fields without a migration/compatibility plan. Extend the model as required.

---

# 8. Immutable Financial Audit Trail

Every financial state transition must be recorded.

Create an immutable financial event/audit mechanism capable of recording:

```text
PAYMENT_CREATED
PAYMENT_SUCCEEDED
PAYMENT_FAILED

SESSION_COMPLETED
PAYOUT_ELIGIBLE

TRANSFER_CREATED
TRANSFER_SUCCEEDED
TRANSFER_FAILED

REFUND_REQUESTED
REFUND_SUCCEEDED
REFUND_FAILED

DISPUTE_OPENED
DISPUTE_RESOLVED

TRANSFER_REVERSED
```

Each event should record:

```text
event_id
payment_transaction
event_type
previous_state
new_state
amount
currency
stripe_event_id
actor_type
actor_id
reason
metadata
created_at
```

The audit record must be append-only from the application's perspective.

---

# 9. Session Completion — 80% Rule

The 80% threshold is acceptable as an initial marketplace policy.

However:

> **80% attendance is an automatic completion criterion, NOT an unconditional payout trigger.**

Do not implement:

```text
student_attendance >= 80%
    ↓
Completed
    ↓
Pay tutor
```

Instead:

```text
Student attendance >= threshold
        AND
Tutor attendance >= minimum threshold
        AND
Session was not cancelled
        AND
Payment is confirmed
        AND
No active dispute
        ↓
AUTO_COMPLETION_ELIGIBLE
        ↓
COMPLETED
        ↓
PAYOUT_ELIGIBLE
```

The 80% threshold must remain configurable through Marketplace Settings.

---

# 10. Tutor Attendance Is Required

Consider this scenario:

```text
Student remains in Jitsi for 48 minutes.
Tutor never joins.
```

Student attendance is 80%.

The tutor must obviously not receive an automatic payout.

Therefore automatic completion must consider both participants.

At minimum:

```text
student_attendance_duration
tutor_attendance_duration
scheduled_duration
```

Do not calculate attendance simply as:

```text
last_seen - first_seen
```

Participants may disconnect and reconnect.

Instead, aggregate attendance intervals:

```text
10:00 → 10:20
10:22 → 10:48

= 20 + 26
= 46 minutes
```

---

# 11. Attendance Must Not Be Client-Authoritative

Do not allow React to submit:

```json
{
  "attendance_percentage": 80
}
```

and treat that as authoritative.

The backend must derive attendance from the meeting integration.

The attendance subsystem must record events such as:

```text
participant_joined
participant_left
participant_rejoined
meeting_started
meeting_ended
```

and associate them with:

```text
session_id
meeting_id
user_id
role
timestamp
```

---

# 12. Manual Dispute Override — REQUIRED

Manual intervention is mandatory.

The Owner/Admin must be able to resolve exceptional sessions.

Possible decisions:

```text
Complete
Partial payout
Full refund
Partial refund
No payout
Reschedule
Cancel
```

Any manual override must record:

```text
actor
timestamp
previous state
new state
reason
```

Do not allow silent administrative state manipulation.

---

# 13. Session State Machine

Add an explicit state machine.

Minimum states:

```text
SCHEDULED
    │
    ▼
IN_PROGRESS
    │
    ├──────────────► CANCELLED
    │
    ▼
ATTENDANCE_REVIEW
    │
    ├──────────────► DISPUTED
    │
    ▼
COMPLETED
    │
    ▼
PAYOUT_ELIGIBLE
```

Additional exceptional states may be introduced where justified.

Do not collapse all business states into one `status` field without documented transition rules.

---

# 14. Payment State Machine

Implement independently from session state.

Minimum conceptual states:

```text
CREATED
   │
   ▼
PAYMENT_PENDING
   │
   ├────────────► PAYMENT_FAILED
   │
   ▼
PAID
   │
   ▼
PAYOUT_ELIGIBLE
   │
   ▼
TRANSFER_PENDING
   │
   ├────────────► PAYOUT_FAILED
   │
   ▼
TRANSFERRED
   │
   ▼
PAID_OUT
```

Exceptional paths:

```text
PAID
  ↓
REFUND_PENDING
  ↓
REFUNDED
```

and:

```text
PAID
  ↓
DISPUTED
```

---

# 15. Refund Architecture

Refunds must be explicitly designed.

Required scenarios:

```text
Student cancels
Tutor cancels
Student no-show
Tutor no-show
Technical failure
Mutual cancellation
Admin cancellation
```

Each scenario needs an explicit policy for:

```text
student refund
tutor compensation
platform fee
payout status
rescheduling
```

Do not allow the implementation agent to invent these business rules.

If the existing F-027 specification does not define the percentages/timing, leave them as configurable policy fields or mark them as unresolved requirements rather than silently choosing values.

---

# 16. Jitsi — APPROVED FOR MVP/PILOT

Using `meet.jit.si` is acceptable for prototype/pilot development.

However, classify it as:

> Development / early pilot video infrastructure

rather than assuming it is the permanent production video architecture.

The eventual direction should probably be:

```text
meet.jit.si
     ↓
self-hosted Jitsi
```

rather than automatically:

```text
meet.jit.si
     ↓
Daily.co
     ↓
self-hosted Jitsi
```

Daily.co should only be introduced if a concrete requirement justifies its operational cost.

Examples:

* managed scaling
* superior SDK requirements
* recording
* analytics
* reduced operational burden

Do not introduce Daily simply because it provides branding.

---

# 17. Jitsi Meeting Security

Do not generate a publicly guessable meeting URL and consider that authentication.

Avoid simplistic patterns such as:

```text
https://meet.jit.si/session-123
```

being the sole access mechanism.

Eventually use authenticated/token-based meeting access.

Meeting authorization should conceptually bind:

```text
session_id
user_id
role
expiry
```

The eventual self-hosted Jitsi deployment should use token authentication or an equivalent authorization mechanism.

---

# 18. Booking Concurrency — REQUIRED

F-027 must protect against double booking.

Example:

```text
Student A ─────┐
               ├── Tutor 14:00 slot
Student B ─────┘
```

Both users may see:

```text
14:00 AVAILABLE
```

Both can click Book.

The booking operation must be atomic.

Conceptually:

```text
BEGIN TRANSACTION

    verify tutor availability

    lock/recheck relevant booking state

    verify no conflicting session

    create Session Schedule

    reserve slot

COMMIT
```

The implementation must not rely only on a frontend availability check.

---

# 19. Timezone — REQUIRED

The current:

```text
scheduled_date
start_time
end_time
```

model is insufficient for an international marketplace.

Tutor and student may have different timezones.

Example:

```text
Tutor:
Africa/Lagos

Student:
Europe/London
```

Store canonical session timestamps and retain timezone information required for display.

Recommended conceptual model:

```text
scheduled_start_at_utc
scheduled_end_at_utc

tutor_timezone
student_timezone
```

The frontend should render the session according to the current user's timezone.

Never use server/local timezone implicitly as marketplace truth.

---

# 20. Single-Site Architecture — APPROVED

Keep:

```text
tutor.zubbystudio.site
```

as a single Frappe site.

Do not implement multi-site tenancy now.

However:

* use stable IDs
* use proper relationships
* avoid hard-coded site assumptions
* do not make business logic dependent on the current hostname

This leaves room for future architectural evolution without paying the cost of multi-tenancy today.

---

# 21. React Router 7 — KEEP

Do not migrate to TanStack Router.

The existing frontend already uses:

* React 18
* TypeScript
* React Router 7
* TanStack Query 5
* Tailwind CSS 4
* shadcn/ui

The proposed route structure is straightforward:

```text
/
├── owner/*
├── tutor/*
└── student/*
```

React Router 7 is sufficient.

Do not introduce a migration solely for consistency with EPM.

Project-level consistency is less important than avoiding unnecessary migration risk.

---

# 22. Security Rules

The following values must never be trusted from the browser:

```text
session status
attendance percentage
payment status
platform fee
tutor payout
refund amount
Stripe transaction state
payout status
```

The server calculates/authorizes them.

Specifically:

### Price

Do not trust:

```json
{
  "price": 5000
}
```

from React.

Determine price from server-side tutor/package/rate configuration.

### Platform fee

Calculate server-side.

### Tutor payout

Calculate server-side.

### Completion

Calculate server-side.

### Attendance

Derive from meeting events.

### Payment

Derive from verified Stripe events.

---

# 23. Scalability

The architecture should comfortably support the initial marketplace scale.

The relevant concern is not simply:

```text
100 tutors
×
50 students
```

but:

```text
concurrent sessions
×
participants
×
video bandwidth
×
attendance events
×
background jobs
```

Frappe is not the primary scaling concern.

The likely pressure points are:

1. Jitsi/video infrastructure
2. database query patterns
3. background workers
4. attendance event processing
5. dashboard aggregation

Do not prematurely introduce distributed infrastructure.

Use Frappe background jobs for:

* payout processing
* attendance evaluation
* payment reconciliation
* notifications
* scheduled state transitions

---

# 24. Dashboard Performance

Do not initially over-engineer analytics.

However, avoid making every dashboard request perform large transactional aggregations.

At small scale:

```text
COUNT
SUM
GROUP BY
```

is acceptable.

As transaction volume grows, consider:

```text
daily aggregates
cached metrics
materialized reporting tables
```

Do not implement this unless required by measured performance.

---

# 25. PWA — DEFER

Do not make PWA a blocker for F-027.

Implement:

```text
responsive React web application
```

first.

The application must work well on mobile browsers.

PWA can be introduced after the core booking/payment/session workflow has been validated.

---

# 26. Required Specification Addendum

Before declaring F-027 implementation complete, the specification must explicitly define:

```text
F027-FIN-001
Payment state machine

F027-FIN-002
Stripe webhook authority

F027-FIN-003
Payment/webhook/payout idempotency

F027-FIN-004
Stripe Connect separate charges/transfers

F027-FIN-005
Immutable financial audit trail

F027-SES-001
80% attendance completion policy

F027-SES-002
Tutor attendance requirement

F027-SES-003
Manual dispute override

F027-BOOK-001
Atomic booking / double-booking prevention

F027-TIME-001
Timezone handling

F027-JIT-001
Authenticated meeting identity

F027-REF-001
Cancellation/refund policy
```

---

# 27. Implementation Boundaries for Zone 1

Do not implement business rules that are not explicitly specified.

If a requirement is ambiguous, stop at the boundary and report:

```text
AMBIGUOUS REQUIREMENT

Question:
<specific question>

Current alternatives:
A. ...
B. ...

Recommended:
...

Reason:
...
```

Do not silently select a business policy.

Technical implementation choices may be made where the business behavior is already unambiguous.

---

# 28. Testing Requirements

For every new state transition, implement tests before implementation code.

Minimum critical test coverage should include:

### Booking

```text
available slot → booking succeeds
occupied slot → booking rejected
concurrent bookings → only one succeeds
```

### Attendance

```text
student < threshold → not auto-completed
student >= threshold + tutor attendance valid → eligible
student >= threshold + tutor absent → not eligible
disconnect/reconnect → duration correctly aggregated
```

### Payments

```text
payment pending → no payout
payment succeeded → paid
duplicate webhook → no duplicate transaction
duplicate webhook → no duplicate payout
payment failure → no payout
```

### Session/payout

```text
session completed + payment pending → no payout
session completed + payment confirmed → payout eligible
payout retry → no duplicate transfer
```

### Refunds

```text
refund requested → refund state created
duplicate refund event → no duplicate refund accounting
```

### Authorization

```text
student cannot complete another student's session
student cannot alter payout
tutor cannot alter platform fee
tutor cannot mark session completed manually
owner can perform authorized override
```

---

# 29. Recommended Request Flow

For booking:

```text
React
  │
  ▼
book_session()
  │
  ├── authenticate user
  ├── authorize student
  ├── validate tutor
  ├── validate subject
  ├── validate timezone/date
  ├── validate availability
  ├── atomically reserve slot
  ├── create Session Schedule
  └── create meeting identity
          │
          ▼
        Response
```

For completion:

```text
Attendance events
       │
       ▼
Attendance records
       │
       ▼
Completion evaluator
       │
       ├── student attendance
       ├── tutor attendance
       ├── scheduled duration
       ├── cancellation
       ├── payment state
       └── dispute state
              │
              ▼
       Session Completed
              │
              ▼
       Payout Eligible
```

For payout:

```text
Payout worker
     │
     ▼
Find PAYOUT_ELIGIBLE
     │
     ├── verify payment
     ├── verify no dispute
     ├── verify no existing transfer
     ├── create Stripe transfer
     ├── persist transfer ID
     └── update payout state
```

---

# 30. Architecture Approval

## Approved

```text
Frappe/ERPNext backend              YES
Custom tutor_hub app                YES
Education module reuse              YES
React frontend                      YES
React Router 7                      YES
TanStack Query                      YES
Single Frappe site                  YES
Stripe Connect                      YES
Separate charges/transfers          YES
Jitsi for pilot                     YES
Self-hosted Jitsi later             YES
Responsive web-first                YES
Manual dispute handling             YES
Immutable payment audit             YES
```

## Approved with conditions

```text
80% attendance                      YES, as eligibility rule
meet.jit.si                         YES, for pilot
Stripe Connect                      YES, after country/currency validation
Automated payout                    YES, after state-machine implementation
```

## Not approved

```text
Browser-authoritative payment
Browser-authoritative attendance
Direct client manipulation of session status
Direct client manipulation of payout
Immediate payout solely because 80% was reached
Generic unrestricted CRUD for financial state
Blind migration from React Router to TanStack Router
Premature multi-site architecture
```

---

# 31. Final Direction to Zone 1

Proceed with implementation **only after incorporating the state-machine and financial-flow requirements into F-027**.

The architecture itself does not need to be replaced.

The recommended final stack is:

```text
React 18
TypeScript
React Router 7
TanStack Query
Tailwind CSS
shadcn/ui
        │
        ▼
Frappe
        │
        ├── education
        └── tutor_hub
              │
              ├── marketplace domain
              ├── booking
              ├── attendance
              ├── payment state
              ├── payout state
              └── audit trail
        │
        ├───────────────┐
        ▼               ▼
     MariaDB          Redis/RQ
        │               │
        │               ├── attendance jobs
        │               ├── payment reconciliation
        │               └── payout jobs
        │
        ├───────────────┐
        ▼               ▼
      Stripe           Jitsi
     Connect
```

**Architecture verdict: CONDITIONAL GO.**

The technology choices are sound. Resolve the financial/session state model, concurrency, timezone, attendance authority, Stripe webhook/idempotency behavior, and cancellation/refund policy before treating F-027 as implementation-ready.

**Do not redesign the entire stack. Harden the domain model.**

