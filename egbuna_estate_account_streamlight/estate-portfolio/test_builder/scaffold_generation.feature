Feature: Generate test folders and file scaffolds on disk
  As a QA tester
  I want submitted test cases to produce real folders and starter test files
  So that backend engineers find a ready-to-fill pytest stub in the right location

  Background:
    Given the app has a volume mounted at "/repo/tests"
    And test case "HOLD-CREATE-BE-INT-001" exists with domain "HOLD", workflow "CREATE", layer "BE", type "INT"

  Scenario: Generate folder structure matching the taxonomy
    When I click "Generate Test Scaffold" for "HOLD-CREATE-BE-INT-001"
    Then the path "/repo/tests/backend/holdings/create/integration/" exists
    And it is created if it did not already exist

  Scenario: Generate a populated pytest file stub
    When I click "Generate Test Scaffold" for "HOLD-CREATE-BE-INT-001"
    Then the file "/repo/tests/backend/holdings/create/integration/HOLD-CREATE-BE-INT-001.py" is created
    And the file's docstring header contains "Test ID:     HOLD-CREATE-BE-INT-001"
    And the file's docstring header contains "Domain:      Holdings"
    And the file contains one "async def test_HOLD_CREATE_BE_INT_001" function stub
    And the function body is not empty and contains no bare "pass" statement

  Scenario: Do not overwrite an existing test file without confirmation
    Given "/repo/tests/backend/holdings/create/integration/HOLD-CREATE-BE-INT-001.py" already exists on disk
    When I click "Generate Test Scaffold" for "HOLD-CREATE-BE-INT-001"
    Then I see a warning "File already exists - overwrite?"
    And the existing file is left untouched until I confirm

  Scenario: Generation fails gracefully when the mount is unwritable
    Given the volume at "/repo/tests" is mounted read-only
    When I click "Generate Test Scaffold" for "HOLD-CREATE-BE-INT-001"
    Then I see the error "Cannot write to /repo/tests - check volume permissions"
    And no partial files are left behind
