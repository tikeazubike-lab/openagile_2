---
type: HO
id: HO-122
title: Claude → OpenCode (deepseek-flash builder): F-TD-001 Teardown — Confirm Current testbuild State First
date: 2026-08-13
from: Claude Web (The Brain / Architect)
to: Hermes deepseek-flash (builder, OpenCode CLI)
protocol: OpenAgile Hybrid Framework v1.0
priority: NORMAL
---

# HO-122 — F-TD-001 Teardown: Investigation Before Any Removal

## Context

F-TD-001's spec already exists at
`.context/feature-specs/F-TD-001-test-checklist-teardown.md` (produced
2026-06-30, Phase A). Per `MASTER_CONTEXT.md`: `testdrive.epm.zubbystudio.site`
and `testbuild.zubbystudio.site` both currently point to the same running
container (`_v3`); `testbuild` additionally fronts an nginx
checklist-page-and-API-reverse-proxy layer that's now redundant since the
checklist moved to a real backend route (`/api/v1/checklist/test-checklist`,
confirmed working as of HO-121). Teardown removes that nginx/proxy layer
only — **not** the `_v3` container itself, which `testdrive` still depends
on.

## A discrepancy to resolve before touching anything

`MASTER_CONTEXT.md` states the domain as `testbuild.zubbystudio.site`
(implying it was migrated along with everything else on 2026-07-16). But
raw Traefik config pulled during the checklist-404 investigation (HO-113)
showed:

```
traefik.http.routers.epm-v3-testbuild-api.rule: Host(`testbuild.zubbystudio.shop`) && PathPrefix(`/api`)
```

That's the **retired `.shop` domain**, not `.site`. This could mean either:
(a) testbuild was never actually migrated (only testdrive was, and the
doc's wrong), or (b) there's a newer `.site` rule that HO-113 simply
didn't surface because it wasn't looking for it. Don't assume either —
confirm directly before planning any removal.

---

## Required — investigation only, no removal yet

1. **List every Traefik router rule referencing `testbuild`**, on both
   `.shop` and `.site`, raw output (`docker inspect` the relevant
   container/labels, or however routing config is actually queried in
   this environment):
   ```bash
   docker inspect estate_portfolio_v3 --format '{{json .Config.Labels}}' | python3 -m json.tool | grep -i testbuild
   ```
   (adjust as needed to get the real current labels)
2. **Confirm whether `testbuild.zubbystudio.shop` is even reachable at
   all right now** — given `.shop` expired at the registrar and is
   permanently retired (2026-07-16 incident), a rule referencing it may
   already be pointing at nothing. `curl -sI https://testbuild.zubbystudio.shop/`
   and report the actual result.
3. **If a `.site` rule for testbuild also exists**, show it too — list
   everything, don't assume only one exists.
4. **Confirm what the nginx layer actually does today**, concretely — the
   spec describes it as "nginx checklist page + API reverse-proxy," but
   given the checklist page itself has since moved to a real backend
   route, confirm whether the nginx layer is serving anything that
   still matters, or whether it's now purely dead weight forwarding to
   `_v3` for no remaining reason.
5. **Propose the actual teardown plan** based on what's found — which
   Traefik rules/labels to remove, which container/config (if any,
   beyond labels) to remove, and explicit confirmation that
   `testdrive.epm.zubbystudio.site`'s routing to `_v3` is entirely
   unaffected by the change. Do not execute yet — report the plan back
   first.

---

## Not required

- No removal of anything yet — this is confirm-then-plan, execution is a
  separate follow-up handover once the plan is reviewed
- No changes to `_v3` itself

---

## Reply format

Raw output per standing rule: actual Traefik labels/config, actual curl
result, not narrated conclusions.

Reply as **HO-123**.
