# Phase 0 — Idea Capture

## What This Phase Produces
1. Problem Statement (one paragraph)
2. Vision Statement (one sentence)
3. User List with roles and capabilities
4. Out-of-Scope List (minimum 5 items)

These feed directly into `.context/project-overview.md` in Phase 1.

---

## Questions to Ask (Group 1 — The Problem)

Ask these together:

> "Let's start with the problem. Answer these three questions in your
> own words — don't overthink it:
>
> 1. What is broken or missing today that this project will fix?
> 2. Who has this problem — is it just you, or other people too?
> 3. What do people use instead right now (even if it's a bad solution)?"

After the user answers, synthesise into a one-paragraph problem statement
and show it to them for confirmation.

---

## Questions to Ask (Group 2 — The Vision)

> "Now give me one sentence that describes the system when it is
> complete. Not what it does — what it IS.
>
> Example: 'A self-hosted personal Nigerian investment management system
> that tells me what I own, what it is worth, and what I need to do.'
>
> Your turn:"

If the user writes more than two sentences, help them distill it:
> "That's good. Can we trim it to one sentence that captures the core?"

---

## Questions to Ask (Group 3 — Users and Roles)

> "Who uses this system? For each type of user, tell me:
> - What they can DO (create, edit, delete, view)
> - What they CANNOT do
>
> Start with: who is the primary user?"

Follow up for each additional role they mention.
Produce a simple table:

| Role | Can Do | Cannot Do |
|------|--------|-----------|
| Admin | ... | ... |
| Viewer | ... | ... |

---

## Questions to Ask (Group 4 — Out of Scope)

> "Name at least 5 things this system will NEVER do. These are
> deliberate decisions — you are pre-answering future scope creep.
>
> Examples from similar projects:
> - No real-time data feeds
> - No mobile native app
> - No automated filing or external submissions
> - No social sharing features
> - No multi-tenant SaaS
>
> What are yours?"

If the user gives fewer than 5, prompt:
> "Can you think of two more? Consider: integrations you will NOT build,
> platforms you will NOT support, user types you will NOT serve."

---

## Document to Produce

After all four groups are answered, produce `.context/project-overview.md`
using the template in `assets/feature-spec-template.md`.

Then ask:
> "Phase 0 complete. This gives us the foundation for every
> decision that follows. Ready to move to Phase 1 — Project Foundation?"
