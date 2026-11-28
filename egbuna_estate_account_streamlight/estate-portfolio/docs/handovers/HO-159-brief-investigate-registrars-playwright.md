## Task: INVESTIGATE ONLY, no code changes. Registrar page layout on testdrive

You are the frontend agent (vision-capable). Look at the live staging site with Playwright screenshots and report what a
user sees. Do NOT edit, create or delete any tracked file. Do NOT commit. Do NOT run git write commands.

### Background
Product Owner reported: "the registrar is not populated, all the data I added has vanished" on
https://testdrive.epm.zubbystudio.site/registrars after PR #10 was deployed.
The orchestrator already verified: the database still has 36 registrars, and the page's DOM contains 36 registrar cards.
Hypothesis to confirm or refute: `RegistrarsLayout.tsx` puts a tall `RegistrarsDashboard` above the list/details area,
so on a normal screen the registrar list and the "Select a registrar to view details" panel are below the fold, inside
a nested scroller. Measured at a 245px-tall window: dashboard about 743px tall, list starts about 755px down.

### How to take the screenshots (already prepared, read-only)
Run exactly this from the epm directory of your worktree (the folder that contains `estate-portfolio-manager/`):

    node /tmp/claude-1000/-home-zubbyik-openagile-2-egbuna-estate-account-streamlight-estate-portfolio/4ef0d904-59f3-41e9-94e8-eb9be42dd925/scratchpad/pw/investigate.mjs ./.pw-out

- It uses a saved login session. If it prints `NO_AUTH` or `SESSION_EXPIRED`, STOP and report that; do not try to log in,
  do not look for credentials, do not read any .env file.
- It writes PNGs and `report.json` into `./.pw-out/` (inside the worktree, so you can open them). It visits `/registrars`
  at 1440x900, 1280x720 and 1920x1080, scrolls the main scroller step by step, selects the first registrar card, and also
  captures `/settings/registrars`.
- Do not write your own Playwright script that clicks anything else. Never click Add, Edit, Delete, Send test, Save or
  Upload: "Send test" sends a real email. Read-only navigation and screenshots only.
- No curl, wget or other network tools (they are denied). Do not run docker, git push, or anything outside this task.

### What to look at (open the PNGs with the Read tool and describe what you actually see)
1. First screen at each viewport (`*-00-fold.png`): what is visible without scrolling? Can a user tell registrars exist?
2. Scroll sequence (`*-0N-scroll.png`): at which scroll step does the registrar list first appear? Does the
   "Select a registrar" panel appear next to it? Any overlap, clipping, double scrollbars, or a list area with zero height?
3. Details view (`registrars-1440x900-10-details.png`): does selecting a registrar show its details?
4. `/settings/registrars`: does the page render the config status, the test-send card and the reminder log card?
5. `report.json`: quote `viewports[*].cards`, `dashboardTitleTopInScroller`, `registrarListTopInScroller`,
   `mainScroller`, plus `consoleErrors` and any `api` entries that are not 200.

### Report format (under 60 lines, no narrative)
- Table: viewport | registrar list visible on first screen (yes/no) | px from top to the list | notes
- Verdict on the hypothesis: CONFIRMED / REFUTED / PARTIAL, with the screenshot filenames that prove it
- Any other defect you saw (with filename), each tagged blocker / major / minor
- What you could NOT check
- Finish by deleting nothing and committing nothing; leave `./.pw-out/` in place for the orchestrator.
