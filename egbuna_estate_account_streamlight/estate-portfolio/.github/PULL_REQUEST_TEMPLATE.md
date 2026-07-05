---
name: Default PR
about: Standard merge request with human testing checklist
---

## Summary

Brief description of what this PR does.

## Type

- [ ] Feature
- [ ] Bug fix
- [ ] Refactor
- [ ] DevOps / CI
- [ ] Documentation

---

## Human Testing Checklist

Tick each box after verifying on the live site.

### F-017: Edit Toggle Removed

- [ ] **Holdings** — no "Viewing/Editing" toggle in the header
- [ ] **Registrars** — no toggle in the header
- [ ] **Companies** — no toggle in the header
- [ ] **User Management** — no toggle in the header
- [ ] **Price Entry** — no toggle in the header
- [ ] **Data Upload** — no toggle in the header
- [ ] **Admin user** — still sees action buttons (edit/delete, Add Holding)
- [ ] **Readonly user** — no action buttons visible (log out, log in as tester)

### F-016: Admin Restructure

- [ ] **User Management** — list of users loads correctly
- [ ] **Admin menu** — shows Price Entry, Data Upload, User Management
- [ ] **Sign out** — redirects to login page

### Data Integrity

- [ ] **Holdings** — positions and values display correctly
- [ ] **Price History** — loads without errors
- [ ] **Dashboard** — loads without errors
- [ ] **Companies** — full list loads, filter/search works

### Auth & Access Control

- [ ] **Login** — works with valid credentials
- [ ] **401** — visiting a protected page while logged out returns to login
- [ ] **403** — readonly user gets 403 on admin-gated endpoints

---

## Test Results

**Passed:** `0 / 20` — **Failed:** `0`

<!-- Update the counts above after testing -->

## Handover

- [ ] HO-026 filed and linked
- [ ] Progress tracker updated

## Sign-off

| Role | Name | Date |
|------|------|------|
| **QA (Human)** | | |
| **Merge** | | |
