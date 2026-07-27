# User journeys

**Status:** Accepted

Seven journeys. Each is an end-to-end path a real person takes, and each names
the features it exercises.

**Journeys are the acceptance tests.** A feature can be individually correct and
still leave a journey broken — the seams between features are where products
fail, and a journey is the only artefact that looks at a seam.

| ID | Journey | Read this if… |
|----|---------|---------------|
| [J1](j1-first-run.md) | First run | …you want to understand the product's hardest moment |
| [J2](j2-daily-use.md) | Daily use | …you want to know what the routine actually is |
| [J3](j3-monthly-reconcile.md) | Monthly reconcile | …you are working on the ledger or reconciliation |
| [J4](j4-tax-year-end.md) | Tax year end | …you are working on tax, exports, or splits |
| [J5](j5-adding-a-device.md) | Adding a device | …you are working on sync |
| [J6](j6-recovery.md) | Recovery | …you are working on auth, backup, or anything that can go wrong |
| [J7](j7-migrating.md) | Migrating from another tool | …you are working on the migration importers |

## How to read one

Each journey states its **precondition**, walks the path step by step, names the
**features exercised**, and lists what it would take for the journey to fail —
the failure modes, not just the happy path.

A journey that only documents the happy path is a screenshot, not a test.
