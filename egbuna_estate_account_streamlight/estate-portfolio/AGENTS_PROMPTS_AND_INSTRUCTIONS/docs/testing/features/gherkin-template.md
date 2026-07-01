# Gherkin Feature File Template
# Save as: docs/testing/features/F-XXX-[name].feature
# Test IDs follow taxonomy: DOMAIN-WORKFLOW-LAYER-TYPE-NNN

Feature: [Feature name — matches F-XXX title]
  As a [admin | portfolio owner | read-only user]
  I want [the action or capability]
  So that [the business outcome]

  # ── Background (shared setup for all scenarios) ──────────────────────────

  Background:
    Given I am authenticated as an admin user
    And the following test data exists:
      | field | value |
      | ...   | ...   |

  # ── Happy Path ───────────────────────────────────────────────────────────
  # Test ID: DOMAIN-WORKFLOW-BE-INT-001
  # REQ: REQ-DOMAIN-001

  Scenario: SC-XXX [descriptive name — happy path]
    Given [initial state — what exists before the action]
    When  [the action taken — user action or API call]
    Then  [observable outcome — what changed]
    And   [additional observable outcome]

  # ── Validation Error ─────────────────────────────────────────────────────
  # Test ID: DOMAIN-WORKFLOW-BE-INT-002

  Scenario: SC-XXX [descriptive name — validation rejected]
    Given [initial state]
    When  I [action] with [invalid input]
    Then  the response status is 422
    And   the error message contains "[specific text]"
    And   no record is created in the database

  # ── Auth — Unauthenticated ───────────────────────────────────────────────
  # Test ID: SEC-ROLE-BE-SEC-001

  Scenario: SC-XXX Unauthenticated request is rejected
    Given I am not authenticated
    When  I request [METHOD] /api/v1/[endpoint]
    Then  the response status is 401

  # ── Auth — Wrong Role ────────────────────────────────────────────────────
  # Test ID: SEC-ROLE-BE-SEC-002

  Scenario: SC-XXX Read-only user cannot perform write operation
    Given I am authenticated as a read-only user
    When  I [POST | PATCH | DELETE] /api/v1/[endpoint]
    Then  the response status is 403

  # ── Empty State ──────────────────────────────────────────────────────────
  # Test ID: DOMAIN-WORKFLOW-BE-INT-003

  Scenario: SC-XXX Empty state returns valid empty response
    Given no [entities] exist in the database
    When  I request GET /api/v1/[endpoint]
    Then  the response status is 200
    And   the response "data" field is an empty array []
    And   the response "meta.total" equals 0

  # ── Data Persistence ─────────────────────────────────────────────────────
  # Test ID: DOMAIN-WORKFLOW-BE-INT-004

  Scenario: SC-XXX Created record persists in database
    Given [setup]
    When  I POST /api/v1/[endpoint] with valid payload
    Then  the response status is 201
    And   a record exists in the [table] table with the correct values
    And   the record has [deleted_at] equal to null

  # ── Monetary Contract ─────────────────────────────────────────────────────
  # Test ID: DOMAIN-WORKFLOW-BE-API-001

  Scenario: SC-XXX Monetary values are strings in API response
    Given [a record with monetary fields exists]
    When  I request GET /api/v1/[endpoint]
    Then  the field "[monetary_field]" in the response is a JSON string
    And   the field "[monetary_field]" is not a JSON number

  # ── Soft Delete ───────────────────────────────────────────────────────────
  # Test ID: DOMAIN-WORKFLOW-BE-INT-005

  Scenario: SC-XXX Delete soft-deletes the record (does not hard delete)
    Given [a record exists with id N]
    When  I DELETE /api/v1/[endpoint]/N
    Then  the response status is 200
    And   the record with id N still exists in the database
    And   the record has [deleted_at] set to a timestamp
    And   GET /api/v1/[endpoint] no longer returns the deleted record

  # ── Scenario Outline (parametrised) ──────────────────────────────────────

  Scenario Outline: SC-XXX [name] handles multiple input cases
    Given [setup]
    When  I [action] with <input>
    Then  the response is <expected>

    Examples:
      | input    | expected |
      | valid    | 200      |
      | empty    | 422      |
      | too_long | 422      |
