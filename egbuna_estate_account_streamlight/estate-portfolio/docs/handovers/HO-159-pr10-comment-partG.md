**Update: Part G — tabs on /registrars.** The head is now `19dffceee9ab85f0a269acd0d6928c05ad869b44`.

**Defect found on testdrive.** Playwright, logged in at 1440×900, found that the dashboard stacked above the registrar list squeezed the list to 32px and its scroll area to 0px. None of the 36 registrars could be seen or clicked. The data was never affected.

**Fix (Product Owner chose tabs).** `/registrars` now has two tabs: **Registrars** (the default, with the original list/details layout at full height) and **Dashboard**, which loads only when you open it. This is spec F-026 §9: AC-7 is reworded, and AC-8 and AC-9 are new.

| Commit | |
|---|---|
| `e02f465b8838ae1127c9fedeb265380205a44a2b` | spec amendment + brief |
| `8247c1029ce4fda7a54e959d6b05d78bbe4e7838` | G1 RED test |
| `04fb8910a21a2ded230901db184a221d83d8fc8d` | G2 tabs |
| `19dffceee9ab85f0a269acd0d6928c05ad869b44` | review responses |

**Checks:**
```
vitest:  Test Files 4 failed | 8 passed (12), Tests 32 passed (32)   (4 = pre-existing jest-dom)
tsc:     13 errors, all in untouched files
AC-9 Playwright, real build, live data:
  1280x720   list 612px, 36 registrars, click → details OK, Dashboard tab OK  PASS
  1440x900   list 792px                                                       PASS
  1920x1080  list 972px                                                       PASS
```

**Reviews:**
- **Auditor:** ALIGNED. It mutation-tested the AC-8 test.
- **DeepSeek (advisory):** SHIP.
- **Minor findings:** all are answered in HO-159. One new follow-up, FU-4: tab accessibility labels.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
