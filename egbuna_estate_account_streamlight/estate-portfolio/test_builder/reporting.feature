Feature: Generate markdown reports from test results
  As a QA tester
  I want a markdown summary of all executed test cases
  So that I can share results without manually formatting anything

  Background:
    Given the database contains 3 test cases with at least 1 run each

  Scenario: Generate a full markdown report after submitting all results
    Given all 3 test cases have a latest run status of either "Passed" or "Failed"
    When I click "Submit Results"
    Then a markdown report is rendered inline on the page
    And the report lists each Test ID, its latest status, expected result, and actual result
    And a "Download .md" button is shown
    And the rendered markdown is saved as a row in the "reports" table

  Scenario: Downloaded report matches the inline report
    Given a markdown report has been generated and saved to the "reports" table
    When I click "Download .md"
    Then a file named with the report's database ID and timestamp is downloaded
    And its contents match the "reports" table row exactly

  Scenario: Block report generation when a test case has no run yet
    Given 1 of the 3 test cases has zero rows in "test_runs"
    When I click "Submit Results"
    Then I see the error "All test cases must have at least one execution result"
    And no report is generated

  Scenario: Auto-generate a bug report markdown for a failed run
    Given a run for "PRIC-PDF-BE-INT-001" is saved with status "Failed"
    Then a bug report markdown is generated using the EPM Bug Report template
    And the "What Actually Happened" section is pre-filled from the run's actual result
    And the "Feature Affected" section is pre-filled from the test case's domain code
    And the bug report is shown inline, offered as a download, and saved to the "bug_reports" table

  Scenario: Passed runs never produce a bug report
    Given a run for "DIVD-CREATE-BE-INT-001" is saved with status "Passed"
    Then no row is created in the "bug_reports" table for that run
