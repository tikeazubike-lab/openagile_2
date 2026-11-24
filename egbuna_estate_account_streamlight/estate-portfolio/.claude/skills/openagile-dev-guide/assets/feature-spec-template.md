# F-XXX: <Feature Name>

## Status
Draft | Specced | Testing (red) | Implementing | Green | Accepted

## Goal
<One paragraph: what can a user do after this ships that they couldn't before?>

## User Value
As a <role>, I want <capability>, so that <business value>.

## Scope

### In scope
- <bullet>

### Out of scope
- <bullet — explicitly naming what this feature does NOT cover prevents scope creep during
  implementation>

## API / Interface Changes
<Endpoints, function signatures, UI components — whatever's relevant. Be concrete: this feeds
directly into the Gherkin scenarios gherkin-spec-agent will author.>

## Data Model Changes
<New tables/fields, or "None">

## Dependencies
<Other F-XXX features this depends on, or "None". If a dependency doesn't have its own spec
yet, flag it explicitly here rather than silently assuming it exists.>

## Scenarios to cover (feeds gherkin-spec-agent)
- Happy path: <one line>
- Edge case: <one line>
- Auth/permission variation (if applicable): <one line>

## Notes
<Anything gherkin-spec-agent or the implementing agent should know that doesn't fit above>
