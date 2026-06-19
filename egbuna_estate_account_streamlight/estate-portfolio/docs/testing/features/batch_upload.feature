Feature: Phase 3C Batch Historical Upload
  As an admin managing the estate portfolio
  I want to upload up to 30 NGX PDF files at once
  So that I can backfill historical price data efficiently without doing it one by one

  Background:
    Given I am authenticated as an admin user
    And I navigate to the Price Entry page ("/settings/price-entry")
    And I select the "Batch Upload (up to 30 PDFs)" tab in the right panel

  Scenario: SC-045 - Successfully upload multiple PDFs in chronological order
    When I drag and drop 5 valid NGX Daily Official List PDFs into the upload zone
    And the files have varying dates from "2026-04-01" to "2026-04-05"
    And I click the "Upload All" button
    Then the system should sort the files by date chronologically
    And process each PDF sequentially
    And write a price_history record for each detected price in every file
    And update the current_price on the Company model using ONLY the data from the most recent file ("2026-04-05")
    And the UI should display a success summary showing "5 files processed, 0 failed"
    And the price_history chart on the Price History page should immediately reflect the backfilled data

  Scenario: SC-046 - Partial failure during batch upload
    When I select 10 files to upload
    And 9 of them are valid NGX PDFs
    And 1 of them is an invalid PDF (e.g. corrupted or wrong format)
    And I click the "Upload All" button
    Then the system should process the 9 valid files successfully
    And skip the 1 invalid file without crashing the entire batch
    And the UI should display a summary showing "9 files processed, 1 failed"
    And the failed file should be listed with a clear error reason ("Invalid format" or "Unreadable PDF")
    And the 9 successful files should have their data written to the price_history table
