Feature: Execute test cases and record versioned results
  As a QA tester
  I want to record the steps I took, the expected result, and the actual result
  So that each test case has a traceable, repeatable history of executions

  Background:
    Given test case "HOLD-CREATE-BE-INT-001" exists in the database
    And I am on the "Execute Tests" page

  Scenario: Record a passing execution
    When I enter the execution path "Login as admin, POST /admin/holdings with valid payload"
    And I enter expected result "Holding created with status draft, 201 response"
    And I enter actual result "Holding created with status draft, 201 response"
    And I mark the result as "Passed"
    And I click "Save Result"
    Then a new row is created in "test_runs" for "HOLD-CREATE-BE-INT-001"
    And the run has status "Passed"
    And the run is stamped with the current timestamp and run number 1

  Scenario: Record a failing execution
    When I enter the execution path "Login as admin, POST /admin/holdings with valid payload"
    And I enter expected result "201 response with status draft"
    And I enter actual result "500 response, TypeError in response serializer"
    And I mark the result as "Failed"
    And I click "Save Result"
    Then a new row is created in "test_runs" for "HOLD-CREATE-BE-INT-001" with status "Failed"
    And a bug report markdown is auto-generated and linked to that run

  Scenario: Re-execute a test case keeps prior runs intact
    Given "HOLD-CREATE-BE-INT-001" already has 1 prior run with status "Failed"
    When I record a new execution and mark it "Passed"
    Then "HOLD-CREATE-BE-INT-001" has 2 runs in "test_runs"
    And the latest run shows status "Passed"
    And the prior "Failed" run is still visible in the run history

  Scenario Outline: Result must be one of the allowed statuses
    When I mark the result as "<status>"
    Then the system "<outcome>"

    Examples:
      | status   | outcome                                |
      | Passed   | accepts and saves the run              |
      | Failed   | accepts, saves the run, and generates a bug report |
      | Blocked  | rejects with "Invalid status: Blocked" |

  Scenario: Block saving a result with no actual result entered
    When I mark the result as "Passed"
    And I leave "actual result" empty
    And I click "Save Result"
    Then I see the error "Actual result is required"
    And no row is created in "test_runs"
