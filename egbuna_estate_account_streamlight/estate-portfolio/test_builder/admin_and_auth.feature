Feature: Manage domain codes and control access
  As an admin
  I want to maintain the list of taxonomy domain codes and gate access to the tool
  So that the taxonomy stays current and only authorized testers can use the tool

  Background:
    Given I am logged in with the shared application password

  Scenario: Add a new domain code
    Given the domain code list does not contain "OBSD"
    When I go to the "Admin: Domain Codes" page
    And I add code "OBSD" with label "Obsidian Import"
    Then "OBSD" appears in the domain dropdown on the "Add Test Cases" page

  Scenario: Reject a duplicate domain code
    Given the domain code list already contains "AUTH"
    When I attempt to add code "AUTH" with label "Duplicate Auth"
    Then I see the error "Domain code AUTH already exists"
    And the domain code list is unchanged

  Scenario: Edit an existing domain code label
    Given the domain code list contains "CHAT" with label "AI ChatBot"
    When I change the label for "CHAT" to "AI ChatBot (intent router, response)"
    Then the dropdown shows the updated label for "CHAT"
    And existing test cases using "CHAT" are unaffected

  Scenario: Reject access with the wrong password
    Given I am on the login page
    When I enter an incorrect password
    Then I see the error "Invalid credentials"
    And I am not granted a session

  Scenario: Session expires after inactivity
    Given I have an active session
    When 12 hours pass with no activity
    Then my session is invalidated
    And I am redirected to the login page on my next request
