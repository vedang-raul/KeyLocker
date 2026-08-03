---
name: Gateway authorization boundary
description: Security rule for the future provider-key proxy and usage gateway.
---

The API gateway must authenticate the caller and enforce admin/employee ownership server-side before forwarding any request with a paid provider credential.

**Why:** Frontend role checks are only presentation logic; a proxy that trusts them could expose provider keys or allow employees to access another employee’s usage and assignments.

**How to apply:** Keep provider credentials server-side, issue separate KeyLocker credentials, validate JWT identity and role on protected routes, and verify ownership before adding proxy forwarding or usage metering.