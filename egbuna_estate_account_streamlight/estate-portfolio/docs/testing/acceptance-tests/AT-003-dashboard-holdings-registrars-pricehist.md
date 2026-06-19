---
type: AT
id: AT-003
title: Acceptance Tests for Dashboard, Holdings, Registrars, Price History
status: IN_PROGRESS
version: 1.0
owner: Antigravity
---

# Acceptance Tests (AT-003)

## 1. Dashboard Page
| ID | Requirement | Status | Notes |
|---|---|---|---|
| SC-UI-001 | Edit mode toggle is hidden on the dashboard | [PASS] | Verified visually |
| SC-UI-002 | Top Holdings chart toggles between By Value and By Shares | [PENDING] | Toggle works correctly. There is no generated bar chart or graph visible on the page.  |
| SC-UI-003 | Navbar shows notification bell with action items | [PENDING] | Notification bell dropdown renders, but what are the default action items? It just shows empty action items.  |
| SC-UI-004 | system theme icon is visible at the top right navbar, but doesnt change from sun icon to moon icon once clicked, and it is supposed to the change at this moment or later phase, because it is currently not changing.| [PASS] | Verified visually |

## 2. Holdings Page
| ID | Requirement | Status | Notes |
|---|---|---|---|
| SC-UI-020 | All required columns visible | [PENDING] | All columns present. What do you mean by All columns visible, are you refering to the header and the columns below it, or header, columns and its contents? |
| SC-UI-021 | Annualised return header is exactly "Return[%]" | [PASS] | Header is correct |
| SC-UI-022 | Actions column only shown in Edit Mode | [PASS] | Actions toggle correctly |
| SC-UI-023 | Edit enables inline editing for that row only | [PASS] | Works |
| SC-UI-024 | Saving inline edit persists changes via API | [PASS] | API connected |
| SC-UI-027 | [+ Add Holding] inserts blank inline form at TOP | [PASS] | Form appears at top(It is very clunky, would prefer a modal, terrible UX) |
| SC-UI-028 | bug in the row editing functionality. | [PENDING] | If the inline edit button is clicked and row editing activated. The increment and decrement button of the affected cells are visible, suprisingly, when the said edit mode is exited to view mode, the button/double ended arrow button still shows and only returns to read only values once refreshed. The edit/view switch doesn't change it. |
| SC-UI-029 | Delete row does not persist changes via API. | [FAILED] | The delete row icon does not seem to persist changes in the API. |


## 3. Registrars Page
| ID | Requirement | Status | Notes |
|---|---|---|---|
| SC-UI-034 | Supports multiple contact fields dynamically | [PASS] | Form array implemented |
| SC-UI-035 | Allow adding/removing contact fields | [PASS] | Form array handles this |
| SC-UI-039 | Details view renders list of fields with icons | [PASS] | Details updated |

## 4. Price History Page
| ID | Requirement | Status | Notes |
|---|---|---|---|
| SC-UI-041 | Searchable company dropdown with placeholder(what does it means searchaeble, does it include  type some characters to search for a company to load it?) | [PENDING] | Implemented |
| SC-UI-042 | Selecting company loads line chart in lavender(What is the source of the this historical data. Is there any table in the database where old prices can be pulled from? Or is there a seprate api endpoint to get the historical data? I can suggest that i manually populate the table with historical data for now until a better solution is provided, with the the downloaded pdf from the NGX for the past 30 days till date, or what do you recommend?) | [PENDING] | Recharts LineChart configured |
| SC-UI-044 | "30D" date range filter works | [PENDING] | Range pills available. For obvious non availability of the data. As mentioned above I can manually upload 30 days data. I just want to make sure that the graph is working, before we make plans for automating the process of getting and populating the data |
| SC-UI-045 | Empty state shows appropriate message(What does this mean? how can i test this exactly? It just shows 'No data available' - is that it?) | [PENDING] | Handled |

## 5. UI/UX Improvements
Holdings page "[/holdings]"
` miscellaneous ui/ux improvements [PENDING] what are the roles of:
 - Average cost
 - Cost Basis
 - Return[%]
 - Status
 What formular should i test the results of each of the following with:
  - Cost Basis
  - Return[%] |
`
