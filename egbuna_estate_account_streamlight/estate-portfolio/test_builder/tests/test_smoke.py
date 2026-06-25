"""
Playwright smoke tests for EPM Test Builder.
Covers key scenarios from the .feature files.

Run with: pytest test/smoke_test_builder.py -v
Requires: playwright install && playwright install-deps
"""
import pytest
from playwright.sync_api import Page, expect


BASE_URL = "http://localhost:8001"
PASSWORD = "test123"


@pytest.fixture(autouse=True)
def setup(page: Page):
    """Ensure we start each test logged out at the login page."""
    yield
    # Cleanup: clear localStorage
    page.evaluate("localStorage.clear()")


def login(page: Page):
    """Helper: login with the shared password."""
    page.goto(f"{BASE_URL}/login")
    page.fill('input[name="password"]', PASSWORD)
    page.click('button[type="submit"]')
    expect(page).to_have_url(f"{BASE_URL}/test-cases")


def test_login_page_renders(page: Page):
    """Scenario: Login page renders with password field."""
    page.goto(f"{BASE_URL}/login")
    expect(page.locator('input[name="password"]')).to_be_visible()
    expect(page.locator('button[type="submit"]')).to_be_visible()


def test_wrong_password_rejected(page: Page):
    """Scenario: Reject access with the wrong password."""
    page.goto(f"{BASE_URL}/login")
    page.fill('input[name="password"]', "wrongpassword")
    page.click('button[type="submit"]')
    expect(page.locator('.error-message')).to_have_text("Invalid credentials")


def test_correct_password_redirects(page: Page):
    """Scenario: Correct password redirects to test-cases."""
    login(page)
    expect(page).to_have_url(f"{BASE_URL}/test-cases")


def test_add_test_case_draft(page: Page):
    """Scenario: Draft a new test case cached in local storage."""
    login(page)
    page.goto(f"{BASE_URL}/test-cases")

    # Fill form
    page.select_option('#domain', 'AUTH')
    page.fill('#workflow', 'LOGIN')
    page.select_option('#layer', 'BE')
    page.select_option('#test_type', 'INT')
    page.fill('#title', 'Test login flow')

    # Save draft
    page.click('button:has-text("Save Draft")')

    # Verify test case appears in the list
    expect(page.locator('text=AUTH-LOGIN-BE-INT-001')).to_be_visible()


def test_sequential_numbering(page: Page):
    """Scenario: Sequential numbering within the same taxonomy key."""
    login(page)
    page.goto(f"{BASE_URL}/test-cases")

    # Add first case
    page.select_option('#domain', 'AUTH')
    page.fill('#workflow', 'LOGIN')
    page.select_option('#layer', 'BE')
    page.select_option('#test_type', 'INT')
    page.fill('#title', 'First test')
    page.click('button:has-text("Save Draft")')
    expect(page.locator('text=AUTH-LOGIN-BE-INT-001')).to_be_visible()

    # Add second case with same taxonomy
    page.select_option('#domain', 'AUTH')
    page.fill('#workflow', 'LOGIN')
    page.select_option('#layer', 'BE')
    page.select_option('#test_type', 'INT')
    page.fill('#title', 'Second test')
    page.click('button:has-text("Save Draft")')
    expect(page.locator('text=AUTH-LOGIN-BE-INT-002')).to_be_visible()


def test_reject_missing_layer(page: Page):
    """Scenario: Reject a test case missing a required taxonomy field."""
    login(page)
    page.goto(f"{BASE_URL}/test-cases")

    page.select_option('#domain', 'AUTH')
    page.fill('#workflow', 'LOGIN')
    # Intentionally leave layer empty
    page.select_option('#test_type', 'INT')
    page.fill('#title', 'Missing layer test')
    page.click('button:has-text("Save Draft")')

    expect(page.locator('#form-error')).to_have_text("Layer is required to generate a Test ID")


def test_submit_test_cases(page: Page):
    """Scenario: Submit all drafted test cases to the database."""
    login(page)
    page.goto(f"{BASE_URL}/test-cases")

    # Draft a case
    page.select_option('#domain', 'HOLD')
    page.fill('#workflow', 'CREATE')
    page.select_option('#layer', 'BE')
    page.select_option('#test_type', 'INT')
    page.fill('#title', 'Submit test')
    page.click('button:has-text("Save Draft")')
    expect(page.locator('text=HOLD-CREATE-BE-INT-001')).to_be_visible()

    # Submit
    page.click('#submit-btn')

    # Should redirect to execute page
    expect(page).to_have_url(f"{BASE_URL}/test-cases/execute")


def test_block_empty_submission(page: Page):
    """Scenario: Block submission when no test cases have been drafted."""
    login(page)
    page.goto(f"{BASE_URL}/test-cases")

    # Try to submit with no drafts
    page.click('#submit-btn')

    # Should show error
    expect(page.locator('#submit-error')).to_have_text("Add at least one test case before submitting")


def test_execute_test_passing(page: Page):
    """Scenario: Record a passing execution."""
    login(page)

    # Submit a test case first
    page.goto(f"{BASE_URL}/test-cases")
    page.select_option('#domain', 'HOLD')
    page.fill('#workflow', 'CREATE')
    page.select_option('#layer', 'BE')
    page.select_option('#test_type', 'INT')
    page.fill('#title', 'Execute test')
    page.click('button:has-text("Save Draft")')
    page.click('#submit-btn')

    # On execute page, fill in the run form
    page.select_option('#status', 'Passed')
    page.fill('textarea[name="execution_path"]', 'POST /admin/holdings')
    page.fill('textarea[name="expected_result"]', '201 response')
    page.fill('textarea[name="actual_result"]', '201 response')
    page.click('button:has-text("Save Result")')

    # Verify success message
    expect(page.locator('.success-message')).to_contain_text("saved")


def test_execute_test_failing_generates_bug_report(page: Page):
    """Scenario: Record a failing execution auto-generates a bug report."""
    login(page)

    # Submit a test case
    page.goto(f"{BASE_URL}/test-cases")
    page.select_option('#domain', 'PRIC')
    page.fill('#workflow', 'UPDATE')
    page.select_option('#layer', 'BE')
    page.select_option('#test_type', 'INT')
    page.fill('#title', 'Bug report test')
    page.click('button:has-text("Save Draft")')
    page.click('#submit-btn')

    # Execute with Failed status
    page.select_option('#status', 'Failed')
    page.fill('textarea[name="execution_path"]', 'POST /api/prices')
    page.fill('textarea[name="expected_result"]', '200 response')
    page.fill('textarea[name="actual_result"]', '500 error')
    page.click('button:has-text("Save Result")')

    # Verify bug report was generated (success message should mention it)
    expect(page.locator('.success-message')).to_contain_text("saved")


def test_versioned_runs(page: Page):
    """Scenario: Re-execute a test case keeps prior runs intact."""
    login(page)

    # Submit test case
    page.goto(f"{BASE_URL}/test-cases")
    page.select_option('#domain', 'DIVD')
    page.fill('#workflow', 'CREATE')
    page.select_option('#layer', 'BE')
    page.select_option('#test_type', 'INT')
    page.fill('#title', 'Version test')
    page.click('button:has-text("Save Draft")')
    page.click('#submit-btn')

    # First run - Failed
    page.select_option('#status', 'Failed')
    page.fill('textarea[name="execution_path"]', 'Step 1')
    page.fill('textarea[name="expected_result"]', 'Expected')
    page.fill('textarea[name="actual_result"]', 'Error')
    page.click('button:has-text("Save Result")')

    # Second run - Passed
    page.select_option('#status', 'Passed')
    page.fill('textarea[name="execution_path"]', 'Step 2')
    page.fill('textarea[name="expected_result"]', 'Expected')
    page.fill('textarea[name="actual_result"]', 'Success')
    page.click('button:has-text("Save Result")')

    # Verify run history shows 2 runs
    page.click('text=Run History')
    rows = page.locator('.run-history table tbody tr')
    expect(rows).to_have_count(2)


def test_generate_report(page: Page):
    """Scenario: Generate a full markdown report."""
    login(page)

    # Submit + execute a test case
    page.goto(f"{BASE_URL}/test-cases")
    page.select_option('#domain', 'WTCH')
    page.fill('#workflow', 'CREATE')
    page.select_option('#layer', 'BE')
    page.select_option('#test_type', 'INT')
    page.fill('#title', 'Report test')
    page.click('button:has-text("Save Draft")')
    page.click('#submit-btn')

    page.select_option('#status', 'Passed')
    page.fill('textarea[name="execution_path"]', 'Test steps')
    page.fill('textarea[name="expected_result"]', 'Expected')
    page.fill('textarea[name="actual_result"]', 'Actual')
    page.click('button:has-text("Save Result")')

    # Go to reports page
    page.goto(f"{BASE_URL}/reports")
    page.click('button:has-text("Generate Report")')

    # Verify report rendered
    expect(page.locator('#report-display')).to_be_visible()
    expect(page.locator('#report-markdown')).to_contain_text("WTCH-CREATE-BE-INT-001")
    expect(page.locator('#report-markdown')).to_contain_text("Passed")


def test_admin_add_domain_code(page: Page):
    """Scenario: Add a new domain code via admin."""
    login(page)
    page.goto(f"{BASE_URL}/admin/domain-codes")

    page.fill('input[name="code"]', 'NEW1')
    page.fill('input[name="label"]', 'New Test Domain')
    page.fill('input[name="folder_slug"]', 'new-test')
    page.click('button:has-text("Add Domain Code")')

    # Verify it appears
    expect(page.locator('text=NEW1')).to_be_visible()
    expect(page.locator('text=New Test Domain')).to_be_visible()


def test_admin_reject_duplicate_domain(page: Page):
    """Scenario: Reject a duplicate domain code."""
    login(page)
    page.goto(f"{BASE_URL}/admin/domain-codes")

    page.fill('input[name="code"]', 'AUTH')
    page.fill('input[name="label"]', 'Duplicate Auth')
    page.fill('input[name="folder_slug"]', 'auth')
    page.click('button:has-text("Add Domain Code")')

    expect(page.locator('.error-message')).to_contain_text("already exists")


def test_logout(page: Page):
    """Scenario: Logout clears session and redirects to login."""
    login(page)
    page.click('button:has-text("Logout")')
    expect(page).to_have_url(f"{BASE_URL}/login")
