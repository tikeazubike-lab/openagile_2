---
type: ADR
id: ADR-005
title: Local Volume Storage
status: ACCEPTED
version: 1.0
created: 2026-05-06
deciders: [Claude, Grok]
supersedes: null
---

# [ADR] ADR-005 — Local Volume Storage
> **Type**: Architecture Decision · **Status**: 🟢 ACCEPTED

## Decision
Use Docker named volumes (`estate_data`) mapped to `/app/uploads` for persistent registrar document storage.
