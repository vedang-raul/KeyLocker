---
name: External backend availability
description: How to reason about frontend issues when the app depends on a separately deployed API.
---

When a frontend calls a separately deployed API, test the API health endpoint and CORS preflight independently before treating a generic client error as a frontend defect.

**Why:** A local preview can render perfectly while the external service is hibernating, unavailable, or still running an older deployment.

**How to apply:** Make client errors actionable and retry transient failures, but do not claim the end-to-end feature is fixed until the backend change has been deployed and the live endpoint responds successfully.