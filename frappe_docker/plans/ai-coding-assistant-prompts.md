# AI Coding Assistant Prompts for Tutor Marketplace Implementation

This document contains comprehensive prompts that can be provided to AI coding assistants (Cursor, Windsurf, Claude Code, GitHub Copilot, etc.) to implement the Tutor Marketplace application.

---

## Overview

You are implementing a **Tutor Marketplace** application built on Frappe/ERPNext with a custom React frontend. The project uses an **API-first architecture** where the frontend and backend are completely separate.

### Project Context

- **Backend**: Frappe/ERPNext (Python) running in Docker
- **Frontend**: React 18 + Vite + Tailwind CSS + TypeScript
- **Site**: `tuts.erpnext.zubbystudio.shop`
- **App Name**: `tutor_marketplace`
- **Payment Gateways**: Stripe and PayPal
- **Key Features**: Tutor registration, Student management, Scheduling, Payments, Course Packages, Subscriptions, Group Sessions

### Architecture Approach

**API-First Design**: The frontend is a completely independent React SPA that communicates with Frappe's REST API. This provides:
- Complete control over UX/UI
- Modern, responsive design
- Fast SPA performance
- Independent development and testing

---

## Prompts for Different AI Assistants

Choose the appropriate prompt below based on which part of the system you're implementing.

---

## PROMPT 1: Frontend Implementation (React 18 + Tailwind)

### Copy This Prompt to Your AI Assistant

```
You are implementing the frontend for a Tutor Marketplace application using React 18, Vite, Tailwind CSS, and TypeScript.

## Project Context

This is an API-first application where the React frontend communicates with a Frappe/ERPNext backend via REST API. The backend is already implemented and provides whitelisted API endpoints.

## Your Working Directory

You are working in: `apps/tutor_marketplace/frontend/`

## Technology Stack

- **Framework**: React 18 with Hooks
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Language**: TypeScript
- **Router**: React Router v6
- **API Client**: Frappe REST API (via @frappe/client or fetch)
- **UI Components**: Custom components (inspired by shadcn/ui patterns)

## Design System

### Color Palette
- Primary: Brand blue (#3B82F6)
- Secondary: Brand yellow (#FBBF24)
- Success: Green (#10B981)
- Warning: Orange (#F59E0B)
- Error: Red (#EF4444)
- Neutral grays: #F3F4F6, #E5E7EB, #9CA3AF, #4B5563, #1F2937

### Typography
- Headings: Raleway (Variable font)
- Body: Merriweather (Regular, Bold)
- UI elements: System fonts

### Spacing
- Base spacing unit: 0.25rem (4px)
- Use Tailwind spacing scale consistently

## Component Patterns

Follow these patterns for consistency:

### Button Component
```tsx
import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-blue-600 text-white hover:bg-blue-700',
        secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300',
        outline: 'border border-gray-300 bg-transparent hover:bg-gray-100',
      },
      size: {
        default: 'h-10 py-2 px-4',
        sm: 'h-9 px-3',
        lg: 'h-11 px-8',
      },
    },
  }
)

interface ButtonProps extends VariantProps<typeof buttonVariants> {
  className?: string
  children?: React.ReactNode
}

export function Button({ className, children, ...props }: ButtonProps) {
  return (
    <button className={cn(buttonVariants({ variant, size }), className)}>
      {children}
    </button>
  )
}
```

### Input Component
```tsx
import * as React from 'react'
import { cn } from '@/lib/utils'

interface InputProps {
  value?: string
  onChange?: (value: string) => void
  type?: string
  placeholder?: string
  disabled?: boolean
  error?: string
}

export function Input({ value, onChange, type = 'text', placeholder, disabled, error }: InputProps) {
  return (
    <div className="space-y-1">
      <input
        type={type}
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        className={cn(
          'flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm',
          'placeholder:text-gray-500',
          'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
          'disabled:cursor-not-allowed disabled:opacity-50',
          error && 'border-red-500 focus:ring-red-500',
          !error && 'focus:ring-blue-500'
        )}
      />
      {error && <p className="text-sm text-red-500">{error}</p>}
    </div>
  )
}
```

## API Integration

### API Client Setup

```typescript
// lib/api.ts
import { createClient } from '@frappe/client'

const frappe = createClient({
  url: import.meta.env.VITE_FRAPPE_URL || 'https://tuts.erpnext.zubbystudio.shop',
  username: () => localStorage.getItem('username'),
  password: () => localStorage.getItem('password')
})

export default frappe
```

### Example API Call

```typescript
import frappe from '@/lib/api'
import { useQuery } from '@tanstack/react-query'

interface TutorProfile {
  id: string
  name: string
  bio: string
  subjects: Subject[]
  rating: number
  total_reviews: number
}

export function useTutorProfile(tutorId: string) {
  return useQuery({
    queryKey: ['tutor', tutorId],
    queryFn: async () => {
      const response = await frappe.call({
        method: 'tutor_marketplace.api.get_tutor_profile',
        args: { tutor_id: tutorId }
      })
      return response.message.tutor
    }
  })
}
```

### Error Handling Pattern

```typescript
import { useQuery } from '@tanstack/react-query'

export function useTutorProfile(tutorId: string) {
  return useQuery({
    queryKey: ['tutor', tutorId],
    queryFn: async () => {
      const response = await frappe.call({
        method: 'tutor_marketplace.api.get_tutor_profile',
        args: { tutor_id: tutorId }
      })
      return response.message.tutor
    },
    onError: (error) => {
      console.error('API Error:', error)
      // Show user-friendly error message
    }
  })
}
```

## Page Structure

Implement pages according to this structure:

```
src/pages/
├── Index.tsx                    # Landing page
├── tutor/
│   ├── Register.tsx            # Tutor registration
│   ├── Dashboard.tsx           # Tutor dashboard
│   ├── Profile.tsx             # Tutor profile (public view)
│   ├── Schedule.tsx            # Schedule management
│   ├── Students.tsx            # Student management
│   ├── Earnings.tsx           # Earnings & payouts
│   ├── CoursePackages.tsx      # Course packages management
│   ├── CreatePackage.tsx      # Create course package
│   ├── SubscriptionPlans.tsx   # Subscription plans management
│   ├── CreateSubscription.tsx # Create subscription plan
│   ├── GroupSessions.tsx      # Group sessions management
│   └── CreateGroupSession.tsx # Create group session
├── student/
│   ├── Register.tsx           # Student registration
│   ├── Dashboard.tsx          # Student dashboard
│   ├── FindTutor.tsx          # Tutor discovery
│   ├── Sessions.tsx           # My sessions
│   ├── Payments.tsx           # Payment history
│   ├── BrowsePackages.tsx     # Browse course packages
│   ├── PackagePurchase.tsx    # Package purchase
│   ├── MyPackages.tsx         # My purchased packages
│   ├── BrowseSubscriptions.tsx # Browse subscription plans
│   ├── MySubscriptions.tsx    # My subscriptions
│   ├── BrowseGroupSessions.tsx # Browse group sessions
│   └── MyGroupSessions.tsx    # My group sessions
├── auth/
│   ├── Login.tsx
│   └── Register.tsx
└── NotFound.tsx
```

## Component Structure

```
src/components/
├── layout/
│   ├── Header.tsx
│   ├── Footer.tsx
│   └── Sidebar.tsx
├── tutor/
│   ├── TutorCard.tsx
│   ├── TutorSearchFilters.tsx
│   ├── AvailabilityCalendar.tsx
│   ├── SessionForm.tsx
│   ├── StudentCard.tsx
│   ├── EarningsSummary.tsx
│   ├── PayoutHistory.tsx
│   ├── CoursePackageCard.tsx
│   ├── CoursePackageForm.tsx
│   ├── CoursePackageList.tsx
│   ├── PackagePurchaseForm.tsx
│   ├── PackageSessionsList.tsx
│   ├── SubscriptionPlanCard.tsx
│   ├── SubscriptionPlanForm.tsx
│   ├── SubscriptionList.tsx
│   ├── SubscribeForm.tsx
│   ├── SubscriptionDetails.tsx
│   ├── SubscriptionBillingHistory.tsx
│   ├── SubscriptionSessionsList.tsx
│   ├── GroupSessionCard.tsx
│   ├── GroupSessionForm.tsx
│   ├── GroupSessionList.tsx
│   ├── GroupSessionEnrollmentForm.tsx
│   ├── GroupSessionEnrollments.tsx
│   ├── WaitlistManager.tsx
│   └── GroupSessionDetails.tsx
├── student/
│   ├── SessionCard.tsx
│   ├── BookingModal.tsx
│   ├── PaymentForm.tsx
│   ├── ReviewForm.tsx
│   ├── CoursePackageBrowser.tsx
│   ├── PackagePurchaseCard.tsx
│   ├── SubscriptionPlanBrowser.tsx
│   ├── MySubscriptions.tsx
│   ├── GroupSessionBrowser.tsx
│   ├── GroupSessionEnrollmentCard.tsx
│   └── MyGroupSessions.tsx
├── common/
│   ├── RatingStars.tsx
│   ├── SubjectBadge.tsx
│   ├── StatusBadge.tsx
│   ├── LoadingSpinner.tsx
│   └── ErrorAlert.tsx
└── ui/
    ├── button/
    ├── input/
    ├── select/
    ├── modal/
    ├── card/
    └── sonner/
```

## Key Features to Implement

### 1. Tutor Registration (Multi-step Form)
- Step 1: Basic information (name, email, phone)
- Step 2: Subjects and qualifications
- Step 3: Availability settings
- Step 4: Payment method setup
- Progress indicator
- Form validation for each step

### 2. Tutor Dashboard
- Display key metrics (total students, sessions, earnings)
- Show upcoming sessions
- Display recent reviews
- Quick action buttons

### 3. Course Packages (Tutor)
- Create package management page
- Build package creation form
- Display package sales analytics
- Show package list

### 4. Course Packages (Student)
- Browse available packages
- Purchase package with payment
- View purchased packages
- Track package sessions

### 5. Subscriptions (Tutor)
- Create subscription plan management
- Build plan creation form
- Display subscriber analytics
- Show plan list

### 6. Subscriptions (Student)
- Browse subscription plans
- Subscribe to plan with payment
- View active subscriptions
- Track subscription sessions

### 7. Group Sessions (Tutor)
- Create group session management
- Build session creation form
- Display enrollment analytics
- Manage enrollments and waitlist

### 8. Group Sessions (Student)
- Browse group sessions
- Enroll in sessions
- View enrolled sessions
- See waitlist status

## Important Guidelines

### DO NOT:
- ❌ Do not modify Docker configurations
- ❌ Do not modify backend Python code
- ❌ Do not modify Frappe DocTypes
- ❌ Do not worry about backend infrastructure

### DO:
- ✅ Focus on React components and pages
- ✅ Implement responsive, accessible UI
- ✅ Handle loading states and errors
- ✅ Use Tailwind CSS for styling
- ✅ Integrate with Frappe REST API
- ✅ Create reusable components
- ✅ Follow the design system

### Mock Data Strategy

If the backend is not available:
1. Create mock data files in `src/mocks/`
2. Use environment variable to toggle mocks
3. Match exact API response structure
4. Continue development with mock data

## Testing

- Test all pages load without errors
- Test forms validate correctly
- Test API calls handle errors gracefully
- Test responsive design on mobile/tablet/desktop
- Test accessibility (keyboard navigation, screen readers)

## Reference Files

For design patterns and component structure, reference:
- `apps/edu_theme/frontend/` - Similar Vue 3 + Tailwind setup (adapt for React)
- `new_vue_website_for_reference2/` - Additional reference implementations

---

## PROMPT 2: Backend Implementation (Frappe/Python)

### Copy This Prompt to Your AI Assistant

```
You are implementing the backend for a Tutor Marketplace application using Frappe/ERPNext.

## Project Context

This is an API-first application where Frappe backend provides whitelisted REST API endpoints for a React frontend. The frontend is a completely independent SPA.

## Your Working Directory

You are working in: `apps/tutor_marketplace/` and `frappe_docker/`

## Technology Stack

- **Framework**: Frappe/ERPNext (Python)
- **Database**: MariaDB (via Frappe)
- **Deployment**: Docker Compose + Traefik
- **Payment Gateways**: Stripe and PayPal
- **Email**: Frappe's email system

## App Structure

```
apps/tutor_marketplace/
├── tutor_marketplace/
│   ├── __init__.py
│   ├── api.py                 # All whitelisted API methods
│   ├── hooks.py               # Frappe hooks
│   ├── modules.txt
│   ├── config/
│   │   └── __init__.py
│   ├── doctype/
│   │   ├── tutor_profile/
│   │   ├── student_profile/
│   │   ├── session_schedule/
│   │   ├── payment_transaction/
│   │   ├── tutor_availability/
│   │   ├── tutor_review/
│   │   ├── marketplace_settings/
│   │   ├── course_package/
│   │   ├── course_package_purchase/
│   │   ├── package_session/
│   │   ├── subscription_plan/
│   │   ├── subscription/
│   │   ├── subscription_billing/
│   │   ├── subscription_session/
│   │   ├── group_session_enrollment/
│   │   └── group_session_waitlist/
│   └── templates/
│       └── pages/
├── public/
│   └── frontend/
└── frontend/                  # React frontend app (separate)
```

## API Method Pattern

All API methods should follow this pattern:

```python
import frappe
from frappe import _

@frappe.whitelist()
def api_method_name(param1, param2, **kwargs):
    """
    API method description.
    
    Args:
        param1: Description
        param2: Description
        
    Returns:
        Dictionary with response data
    """
    
    try:
        # Validate inputs
        if not param1:
            frappe.throw("param1 is required")
        
        # Business logic
        result = do_something(param1, param2)
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        frappe.log_error(f"Error in api_method_name: {str(e)}")
        frappe.throw(str(e))
```

## DocType Pattern

When creating DocTypes, follow Frappe's conventions:

```python
from frappe.model.document import Document

class TutorProfile(Document):
    def validate(self):
        # Validation logic
        pass
    
    def before_save(self):
        # Before save logic
        pass
    
    def on_update(self):
        # After update logic
        pass
    
    def on_trash(self):
        # Before delete logic
        pass
```

## Key DocTypes to Implement

### 1. Tutor Profile
- Fields: user, instructor, bio, subjects, qualifications, hourly_rate, payment_method, payment_account, is_verified, rating, total_reviews, profile_image, video_intro, status
- Child tables: tutor_subject, tutor_qualification
- Permissions: Tutor can edit own profile

### 2. Student Profile
- Fields: user, student, tutor, guardian_email, guardian_phone, learning_goals, skill_level, status
- Relationships: Links to education.student

### 3. Session Schedule
- Fields: tutor, student, subject, scheduled_date, start_time, end_time, duration_minutes, session_type, max_students, current_students, min_students, price_per_student, is_public, enrollment_deadline, waitlist_enabled, waitlist_max, meeting_link, status, notes, recording_link, attendance_confirmed, package_purchase, subscription
- Conflict detection logic
- Indexes on: date, tutor, student

### 4. Payment Transaction
- Fields: session, tutor, student, amount, platform_fee, tutor_payout, payment_gateway, transaction_id, status, payout_status, payout_date, created_at, transaction_type, package_purchase, subscription_billing, group_enrollment, is_recurring, recurrence_id
- Status workflow
- Indexes on: tutor, student, status, created_at

### 5. Course Package
- Fields: tutor, package_name, description, subject, total_sessions, original_price, discounted_price, discount_percentage, validity_days, max_students, is_active, created_at, expires_at, terms, what_included, image, status

### 6. Course Package Purchase
- Fields: package, student, tutor, purchase_date, amount_paid, payment_gateway, transaction_id, sessions_remaining, valid_until, status, auto_renew

### 7. Subscription Plan
- Fields: tutor, plan_name, description, subject, billing_cycle, sessions_per_cycle, price_per_cycle, session_duration, preferred_days, preferred_time_start, preferred_time_end, max_subscribers, trial_sessions, cancellation_notice_days, is_active, created_at, terms, what_included, image, status

### 8. Subscription
- Fields: plan, student, tutor, start_date, next_billing_date, billing_cycle_count, total_paid, sessions_used, sessions_remaining, status, auto_renew, trial_used, trial_sessions_remaining, cancel_requested_at, cancel_effective_date, cancel_reason, notes

### 9. Subscription Billing
- Fields: subscription, billing_cycle, billing_date, amount, payment_gateway, transaction_id, status, paid_at, failure_reason, retry_count

### 10. Group Session Enrollment
- Fields: session, student, enrolled_at, enrollment_status, waitlist_position, payment_status, payment_transaction, amount_paid, joined_at, left_at, notes

### 11. Group Session Waitlist
- Fields: session, student, waitlisted_at, position, notified, notified_at, status

## Payment Gateway Integration

### Stripe Integration

```python
import stripe

# Configuration
stripe.api_key = frappe.conf.get("stripe_secret_key")

# Create Payment Intent
def create_payment_intent(amount, currency, customer_id):
    intent = stripe.PaymentIntent.create(
        amount=int(amount * 100),  # Convert to cents
        currency=currency,
        customer=customer_id,
        metadata={'order_id': 'ORDER_123'}
    )
    return intent

# Handle Webhook
@frappe.whitelist()
def stripe_webhook():
    payload = request.data
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = stripe.Webhook.construct_event(
        payload, sig_header, webhook_secret
    )
    
    if event.type == 'payment_intent.succeeded':
        handle_payment_success(event.data.object)
    elif event.type == 'payment_intent.failed':
        handle_payment_failure(event.data.object)
```

### PayPal Integration

```python
import paypalrestsdk

# Configuration
paypalrestsdk.core.ApiBase.set_environment(
    paypalrestsdk.core.SandboxEnvironment(
        client_id=frappe.conf.get("paypal_client_id"),
        client_secret=frappe.conf.get("paypal_client_secret")
    )
)

# Create Order
def create_order(amount, currency):
    order = paypalrestsdk.orders.OrdersCreateRequest().body({
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": currency,
                "value": str(amount)
            }
        }]
    })
    response = orders_create(order)
    return response.result

# Handle Webhook
@frappe.whitelist()
def paypal_webhook():
    payload = request.data
    event_type = request.headers.get('PAYPAL-TRANSACTION-ID')
    
    if event_type == 'PAYMENT.CAPTURE.COMPLETED':
        handle_payment_success(payload)
    elif event_type == 'PAYMENT.CAPTURE.DENIED':
        handle_payment_failure(payload)
```

## Email Notifications

### Email Template Pattern

```python
# In templates/emails/
from frappe.email import sendmail

def send_tutor_registration_confirmation(email, tutor_name):
    sendmail(
        recipients=[email],
        subject="Welcome to Tutor Marketplace!",
        template="tutor_registration_confirmation",
        args={
            "tutor_name": tutor_name,
            "dashboard_url": "https://tuts.erpnext.zubbystudio.shop/dashboard"
        }
    )
```

## Background Jobs

### Scheduled Job Pattern

```python
from frappe.utils.background_jobs import enqueue_job

# Enqueue job
enqueue_job(
    "method_name",
    queue="default",
    timeout=300,
    event="event_name",
    job_name="Job Name",
    kwargs={"param1": "value1"}
)

# Scheduled job
@frappe.whitelist()
def scheduled_job():
    # Job logic
    pass

# In hooks.py
scheduler_events = {
    "daily": "scheduled_job"
}
```

## Important Guidelines

### DO NOT:
- ❌ Do not write CSS, HTML, or React code
- ❌ Do not worry about frontend visual aesthetics
- ❌ Do not modify frontend code in `apps/tutor_marketplace/frontend/`
- ❌ Do not create design mockups or wireframes
- ❌ Do not implement frontend state management

### DO:
- ✅ Create and configure DocTypes
- ✅ Implement whitelisted API methods
- ✅ Integrate payment gateways
- ✅ Set up email notifications
- ✅ Configure Docker and Traefik
- ✅ Implement business logic
- ✅ Ensure data validation and security

## Docker Configuration

### Site Configuration

```yaml
# In docker-compose.yml or overrides/
services:
  frontend:
    environment:
      - SITES=tuts.erpnext.zubbystudio.shop
    volumes:
      - ./sites:/home/frappe/frappe-bench/sites
```

### Traefik Routing

```yaml
# Traefik labels for routing
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.tuts.rule=Host(`tuts.erpnext.zubbystudio.shop`)"
  - "traefik.http.routers.tuts.entrypoints=websecure"
  - "traefik.http.routers.tuts.tls=true"
  - "traefik.http.routers.tuts.tls.certresolver=letsencrypt"
```

## Security

### Role-Based Access Control

```python
# Create roles
tutor_role = frappe.get_doc("Role", "Tutor")
student_role = frappe.get_doc("Role", "Student")

# Permission checks
if not frappe.has_permission("Tutor Profile", "write"):
    frappe.throw("You don't have permission to edit this profile")
```

### Data Validation

```python
# Server-side validation
def validate_email(email):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        frappe.throw("Invalid email address")

# SQL injection prevention
# Use Frappe's ORM - never raw SQL
doc = frappe.get_doc("Tutor Profile", tutor_id)
```

## Testing

- Test all API endpoints
- Test payment flows (test mode)
- Test email sending
- Test background jobs
- Test security (authentication, authorization)
```

---

## PROMPT 3: Full Stack Implementation (Both Frontend & Backend)

### Copy This Prompt to Your AI Assistant

```
You are implementing a complete Tutor Marketplace application with both frontend and backend components.

## Project Overview

This is a full-stack application with:
- **Backend**: Frappe/ERPNext (Python) with REST API
- **Frontend**: React 18 SPA communicating with backend API
- **Site**: `tuts.erpnext.zubbystudio.shop`
- **App**: `tutor_marketplace`

## Implementation Strategy

### Phase 1: Backend Foundation (Week 1-2)

1. Create Frappe App
   ```bash
   bench new-app tutor_marketplace
   ```

2. Create Core DocTypes
   - Tutor Profile
   - Student Profile
   - Session Schedule
   - Payment Transaction
   - Tutor Availability
   - Tutor Review
   - Marketplace Settings

3. Implement Basic API Methods
   - `create_tutor_profile()`
   - `register_student()`
   - `create_session()`
   - `initiate_payment()`
   - `get_tutor_profile()`

4. Configure Docker
   - Add site to docker-compose.yml
   - Configure Traefik routing
   - Set up SSL certificates

### Phase 2: Frontend Foundation (Week 1-2)

1. Initialize React Project
   ```bash
   npm create vite@latest tutor-marketplace-frontend
   cd tutor-marketplace-frontend
   npm install react@latest
   npm install -D tailwindcss postcss autoprefixer
   npm install @tanstack/react-query @frappe/client
   ```

2. Set Up Project Structure
   - Create pages directory
   - Create components directory
   - Set up React Router
   - Configure Tailwind CSS

3. Create Base Components
   - Header.tsx
   - Footer.tsx
   - Layout components
   - UI components (Button, Input, Modal)

4. Implement Landing Page
   - Hero section
   - Featured tutors
   - Testimonials
   - Statistics

### Phase 3: Core Features (Week 3-8)

#### Backend:
- Implement all API methods for core features
- Integrate Stripe and PayPal
- Set up email notifications
- Create background jobs

#### Frontend:
- Build tutor registration flow
- Build student registration flow
- Implement scheduling system
- Create payment forms
- Build dashboards

### Phase 4: Advanced Features (Week 9-21)

#### Backend:
- Create Course Package DocTypes
- Create Subscription DocTypes
- Create Group Session DocTypes
- Implement all related APIs
- Set up recurring payments
- Implement waitlist logic

#### Frontend:
- Build course package UI
- Build subscription UI
- Build group session UI
- Implement all user flows

### Phase 5: Testing & Deployment (Week 22-23)

- End-to-end testing of all flows
- Security audit
- Performance optimization
- Production deployment

## Key Principles

### API-First Design
- Frontend and backend are completely separate
- Frontend communicates via REST API only
- No shared state or direct database access
- Clear API contracts between frontend and backend

### Separation of Concerns
- Backend: Business logic, data persistence, API endpoints
- Frontend: UI/UX, state management, user interactions
- Each can be developed and tested independently

### Progressive Enhancement
- Start with core features
- Add advanced features incrementally
- Each feature is self-contained
- Easy to test and iterate

## Communication Between Frontend and Backend

### API Documentation

Backend should document all API endpoints:

```python
"""
API: create_tutor_profile
Method: POST
Authentication: Required
Permission: Tutor

Description:
Creates a new tutor profile for the authenticated user.

Request Body:
{
    "bio": "string - Professional biography",
    "subjects": [...],
    "qualifications": [...],
    "hourly_rate": "float - Base hourly rate",
    "payment_method": "string - stripe|paypal|bank_transfer",
    "payment_account": "object - Payment account details"
}

Success Response (200):
{
    "tutor_id": "string - Tutor profile ID",
    "status": "string - pending|active"
}

Error Responses:
400 - Bad Request (invalid data)
401 - Unauthorized (not logged in)
403 - Forbidden (already has tutor profile)
500 - Internal Server Error
"""
```

### Frontend API Integration

Frontend should use documented endpoints:

```typescript
import { useMutation } from '@tanstack/react-query'
import frappe from '@/lib/api'

interface TutorProfileData {
  bio: string
  subjects: Subject[]
  qualifications: Qualification[]
  hourly_rate: number
  payment_method: string
  payment_account: object
}

export function useCreateTutorProfile() {
  const mutation = useMutation({
    mutationFn: async (data: TutorProfileData) => {
      const response = await frappe.call({
        method: 'tutor_marketplace.api.create_tutor_profile',
        args: data
      })
      return response.message
    }
  })

  return mutation
}
```

## Development Workflow

### Backend Development
1. Create/update DocType
2. Implement API method
3. Test API endpoint
4. Document API
5. Notify frontend of changes

### Frontend Development
1. Review API documentation
2. Implement UI component
3. Integrate API call
4. Handle loading/error states
5. Test user flow

### Mock Data Strategy
- Frontend can use mock data while backend is being built
- Backend can provide sample API responses
- Both teams can work in parallel

## Testing Strategy

### Backend Testing
- Unit tests for API methods
- Integration tests for payment gateways
- Test email sending
- Test background jobs

### Frontend Testing
- Component unit tests
- Integration tests with mock API
- E2E tests for user flows
- Cross-browser testing

### Integration Testing
- Test frontend with real backend
- Test all API endpoints
- Test payment flows end-to-end
- Test error handling

## Deployment

### Backend Deployment
- Build Frappe app
- Run migrations
- Restart Docker containers
- Verify API endpoints

### Frontend Deployment
- Build React app
- Deploy to CDN or static hosting
- Configure API URL
- Test production deployment

## Success Criteria

The application is complete when:
1. All DocTypes are created and validated
2. All API endpoints are implemented and tested
3. Frontend is fully functional with all features
4. Payment gateways are integrated and working
5. Email notifications are configured
6. Site is accessible at `tuts.erpnext.zubbystudio.shop`
7. All user flows work end-to-end
8. Security measures are in place
9. Performance is acceptable
10. Documentation is complete
```

---

## Quick Reference: API Endpoints Summary

### Public/Guest Endpoints
- `get_marketplace_data()` - Landing page data
- `search_tutors()` - Search and filter tutors
- `get_tutor_profile()` - Get public tutor profile
- `search_packages()` - Search course packages
- `get_package_details()` - Get package details
- `search_subscription_plans()` - Search subscription plans
- `search_group_sessions()` - Search group sessions

### Tutor Management
- `create_tutor_profile()` - Create tutor profile
- `update_tutor_profile()` - Update tutor profile
- `get_my_tutor_profile()` - Get current tutor profile
- `update_availability()` - Update availability
- `get_tutor_students()` - Get tutor's students
- `create_course_package()` - Create course package
- `update_course_package()` - Update course package
- `delete_course_package()` - Delete course package
- `get_tutor_packages()` - Get tutor's packages
- `create_subscription_plan()` - Create subscription plan
- `update_subscription_plan()` - Update subscription plan
- `delete_subscription_plan()` - Delete subscription plan
- `get_tutor_subscription_plans()` - Get tutor's plans
- `create_group_session()` - Create group session
- `update_group_session()` - Update group session
- `delete_group_session()` - Delete group session
- `get_tutor_group_sessions()` - Get tutor's group sessions

### Student Management
- `register_student()` - Register student
- `update_student_profile()` - Update student profile
- `get_my_student_profile()` - Get current student profile
- `get_my_tutors()` - Get student's tutors
- `purchase_package()` - Purchase course package
- `get_student_packages()` - Get student's packages
- `book_package_session()` - Book session from package
- `get_package_sessions()` - Get package sessions
- `subscribe_to_plan()` - Subscribe to plan
- `get_student_subscriptions()` - Get student's subscriptions
- `pause_subscription()` - Pause subscription
- `resume_subscription()` - Resume subscription
- `cancel_subscription()` - Cancel subscription
- `enroll_in_group_session()` - Enroll in group session
- `get_student_group_sessions()` - Get student's group sessions

### Scheduling
- `create_session()` - Create session
- `update_session()` - Update session
- `update_session_status()` - Update session status
- `cancel_session()` - Cancel session
- `get_tutor_schedule()` - Get tutor's schedule
- `get_student_sessions()` - Get student's sessions
- `get_session_details()` - Get session details
- `check_availability()` - Check availability
- `generate_meeting_link()` - Generate meeting link

### Payments
- `initiate_payment()` - Initiate payment
- `confirm_payment()` - Confirm payment
- `get_payment_status()` - Get payment status
- `get_tutor_earnings()` - Get tutor earnings
- `get_payment_history()` - Get payment history
- `request_payout()` - Request payout
- `get_payout_history()` - Get payout history
- `process_subscription_billing()` - Process subscription billing
- `get_subscription_billing_history()` - Get billing history

### Reviews
- `submit_review()` - Submit review
- `get_tutor_reviews()` - Get tutor reviews
- `get_my_reviews()` - Get my reviews
- `update_review()` - Update review
- `delete_review()` - Delete review

### Marketplace
- `get_marketplace_settings()` - Get settings
- `update_marketplace_settings()` - Update settings
- `get_statistics()` - Get statistics
- `verify_tutor()` - Verify tutor
- `suspend_tutor()` - Suspend tutor

---

## Tips for AI Coding Assistants

### For Cursor/Windsurf/Claude Code:
1. **Start with the appropriate prompt** based on what you're implementing
2. **Reference the architecture documents** in `plans/` directory
3. **Follow the component patterns** shown in the prompts
4. **Use the API integration examples** provided
5. **Test incrementally** - don't try to build everything at once
6. **Ask clarifying questions** if something is unclear

### For GitHub Copilot:
1. **Open the relevant files** in your editor
2. **Use the prompts as context** when asking for code suggestions
3. **Reference the architecture** when making decisions
4. **Follow the patterns** established in the prompts
5. **Test frequently** - run tests after each change

### General Tips:
- **Start small**: Implement one feature at a time
- **Test frequently**: Run tests after each change
- **Document as you go**: Add comments to complex logic
- **Use type hints**: TypeScript for frontend, type hints for Python
- **Follow conventions**: Stick to the patterns shown in the prompts
- **Ask for help**: If stuck, ask specific questions about the architecture

---

## Getting Started

1. **Choose your role**: Frontend, Backend, or Full Stack
2. **Copy the appropriate prompt** above
3. **Paste it into your AI coding assistant**
4. **Start implementing** following the guidelines
5. **Reference the architecture documents** in `plans/` for detailed specifications

Good luck with your implementation!
