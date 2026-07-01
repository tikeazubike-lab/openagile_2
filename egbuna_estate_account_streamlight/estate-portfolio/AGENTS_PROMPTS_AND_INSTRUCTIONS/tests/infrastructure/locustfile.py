# backend/tests/performance/locustfile.py
"""
Stage 5A — Performance Tests (Locust)
Runs against staging: demo.estate.zubbystudio.shop

Usage (from GitHub Actions or manually on server):
  locust -f backend/tests/performance/locustfile.py \
         --headless \
         --host=https://demo.estate.zubbystudio.shop \
         --users=50 \
         --spawn-rate=5 \
         --run-time=60s \
         --html=perf_report.html

Acceptance thresholds (enforced in CI via --exit-code-on-error):
  P95 response time < 500ms (GET endpoints)
  P95 response time < 1000ms (POST endpoints)
  Error rate < 1%
"""
import os
import json
from locust import HttpUser, task, between, events
from locust.env import Environment


# ---------------------------------------------------------------------------
# Credentials (injected via GitHub Actions secrets)
# ---------------------------------------------------------------------------
ADMIN_USERNAME = os.environ.get("E2E_ADMIN_USER", "zubbyik")
ADMIN_PASSWORD = os.environ.get("E2E_ADMIN_PASS", "changeme")


# ---------------------------------------------------------------------------
# Base authenticated user class
# ---------------------------------------------------------------------------

class AuthenticatedUser(HttpUser):
    """
    Logs in once via POST /api/v1/auth/login and reuses the httpOnly
    epm_token cookie for all subsequent requests (cookie jar is shared
    per Locust user session).
    """
    abstract = True
    wait_time = between(1, 3)

    def on_start(self):
        """Authenticate on session start."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
            name="[auth] login",
        )
        if response.status_code != 200:
            raise Exception(
                f"Login failed during Locust setup: {response.status_code} {response.text}"
            )

    def on_stop(self):
        self.client.post("/api/v1/auth/logout", name="[auth] logout")


# ---------------------------------------------------------------------------
# Dashboard load scenario
# ---------------------------------------------------------------------------

class DashboardUser(AuthenticatedUser):
    """
    Simulates a user who loads the dashboard and auto-refresh pattern.
    50 concurrent users, 60s run.
    """
    weight = 3  # 60% of users in mixed scenario

    @task(5)
    def load_dashboard(self):
        self.client.get("/api/v1/dashboard", name="GET /api/v1/dashboard")

    @task(2)
    def load_holdings(self):
        self.client.get("/api/v1/holdings", name="GET /api/v1/holdings")

    @task(1)
    def load_nav_history(self):
        self.client.get("/api/v1/nav-history", name="GET /api/v1/nav-history")


# ---------------------------------------------------------------------------
# Price entry scenario (write path)
# ---------------------------------------------------------------------------

class PriceEntryUser(AuthenticatedUser):
    """
    Simulates an admin entering stock prices.
    20 concurrent users.
    P95 < 1000ms for POST.
    """
    weight = 1  # 20% of users in mixed scenario

    def on_start(self):
        super().on_start()
        # Get a real company ID to use in price entries
        response = self.client.get("/api/v1/companies?limit=1", name="[setup] get company")
        if response.status_code == 200:
            companies = response.json().get("data", [])
            self.company_id = companies[0]["id"] if companies else 1
        else:
            self.company_id = 1

    @task(3)
    def quick_price_entry(self):
        from datetime import date
        self.client.post(
            "/api/v1/prices/quick",
            json={
                "company_id": self.company_id,
                "price": "100.00",
                "entry_date": str(date.today()),
            },
            name="POST /api/v1/prices/quick",
        )

    @task(1)
    def view_price_audit(self):
        self.client.get("/api/v1/prices/audit", name="GET /api/v1/prices/audit")


# ---------------------------------------------------------------------------
# Auth cycle scenario
# ---------------------------------------------------------------------------

class AuthCycleUser(HttpUser):
    """
    Simulates login → browse → logout.
    20 concurrent users. Tests auth endpoint throughput.
    """
    weight = 1
    wait_time = between(2, 5)

    @task
    def login_view_logout(self):
        login_resp = self.client.post(
            "/api/v1/auth/login",
            json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
            name="POST /api/v1/auth/login",
        )
        if login_resp.status_code == 200:
            self.client.get("/api/v1/auth/me", name="GET /api/v1/auth/me")
            self.client.post("/api/v1/auth/logout", name="POST /api/v1/auth/logout")


# ---------------------------------------------------------------------------
# Custom failure thresholds (checked at end of run by CI)
# ---------------------------------------------------------------------------

@events.quitting.add_listener
def assert_thresholds(environment: Environment, **kwargs):
    """
    Fail the Locust run (non-zero exit code) if performance thresholds are breached.
    GitHub Actions treats non-zero exit as a test failure.
    """
    stats = environment.runner.stats if environment.runner else None
    if not stats:
        return

    errors = 0
    total = 0

    for entry in stats.entries.values():
        total += entry.num_requests
        errors += entry.num_failures

        # P95 thresholds
        p95 = entry.get_response_time_percentile(0.95)
        if entry.method == "GET" and p95 > 500:
            print(
                f"PERF FAIL: {entry.method} {entry.name} "
                f"P95={p95}ms > 500ms threshold"
            )
            environment.process_exit_code = 1

        if entry.method == "POST" and p95 > 1000:
            print(
                f"PERF FAIL: {entry.method} {entry.name} "
                f"P95={p95}ms > 1000ms threshold"
            )
            environment.process_exit_code = 1

    # Error rate threshold
    if total > 0:
        error_rate = errors / total
        if error_rate > 0.01:  # > 1%
            print(f"PERF FAIL: Error rate {error_rate:.2%} > 1% threshold")
            environment.process_exit_code = 1
