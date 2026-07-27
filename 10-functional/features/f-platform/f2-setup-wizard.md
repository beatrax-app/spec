# F2 — First-run setup wizard

**Status:** Accepted · **Area:** F — Platform

---

## Purpose

The first session decides whether someone keeps using beatrax. It has to get
from an empty database to a populated dashboard in one guided pass, using files
the user already has, without asking anything it can work out for itself.

## Behaviour

### Nine steps, most of them skippable

Welcome → connect bank → connect payment processor → connect card → connect email
→ first import → budgets → tax country → done.

The connector steps and the budget and tax steps are **skippable** — a user who
only has a bank export should not be blocked by a card step. Welcome, the first
import, and the finish are not.

### Progress is per step, and resumable

Each step's state is recorded. Returning resumes at the first incomplete step —
any step already in progress wins, otherwise the first pending one. Progress
initialisation is insert-only, so a step added in a later version seeds as
skipped for a user who already finished rather than reopening their wizard.

Jumping to a step is guarded: the target must exist and every prior step must be
done or skipped, so a manipulated URL cannot skip the import.

### Staging, then one commit

Each connector step stages an import ([A2](../a-ingestion/a2-import-wizard.md))
and remembers its identifier. The first-import step then shows a **consolidated
preview** across every staged source, grouped by format with a sample of each.

Committing is **all or nothing**: every staged import, every starting-balance
entry, and the progress change land in one transaction. A partial first import
would leave a state nobody designed.

Chain resolution and recurring detection dispatch **after** that transaction
commits.

### Accounts are created as needed

A bank step encountering an unknown identifier creates the account and re-runs
the preview. The card and processor steps create their synthetic accounts before
previewing, because the preview needs somewhere to attribute rows to — the
ordering is load-bearing.

### Starting balances

Where a source carries a starting balance it is detected and offered for
confirmation; where it does not, the step asks
([A9](../a-ingestion/a9-starting-balances.md)). Confirmation is idempotent, and
an override far from the detected value warns rather than blocks.

### Email is a link, not a wizard

The email step launches the authorisation flow ([A4](../a-ingestion/a4-email-scanning.md))
rather than embedding it. The grant belongs to the provider's own flow.

### Budgets and tax

The budget step seeds a first month's envelope assignments
([D1](../d-money/d1-envelope-budgeting.md)), because an empty grid is not a
useful starting state. The tax step picks a country, seeding the deduction
corpus ([D4](../d-money/d4-tax.md)).

### Finishing

Reaching the end for the first time raises a completion event exactly once.

## States

Per step: `pending`, `in_progress`, `done`, `skipped` — enforced at the database
layer.

The starting-balance card has its own states, listed in
[A9](../a-ingestion/a9-starting-balances.md).

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| Closing mid-upload | The staged import identifier survives; the step resumes. |
| Re-running initialisation | Idempotent; nothing duplicates. |
| Two uploads in one step | The second replaces the first. |
| A fatal parse error | Surfaced from the preview directly, with the file named. |
| An override far from the detected balance | Warned, not blocked. |
| A manipulated step URL | Refused unless every prior step is done or skipped. |
| A step added in a later version | Seeds as skipped for users who already finished. |
| A commit failure | Everything rolls back together. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **F2-R1** | The wizard MUST cover welcome, the connector steps, first import, budgets, tax country, and a finish. |
| **F2-R2** | Connector, budget, and tax steps MUST be skippable; welcome, first import, and finish MUST NOT. |
| **F2-R3** | Per-step progress MUST be recorded and MUST resume at the first incomplete step. |
| **F2-R4** | Progress initialisation MUST be insert-only and MUST be idempotent. |
| **F2-R5** | A step added after a user completed the wizard MUST seed as skipped. |
| **F2-R6** | Jumping to a step MUST require that the step exists and every prior step is done or skipped. |
| **F2-R7** | Each connector step MUST stage an import and remember its identifier. |
| **F2-R8** | The first-import step MUST show a consolidated preview across every staged source, grouped by format. |
| **F2-R9** | The first-import commit MUST be all-or-nothing across every staged import, starting balance, and the progress change. |
| **F2-R10** | Downstream dispatch MUST occur after the commit transaction. |
| **F2-R11** | An unknown account identifier MUST cause the account to be created and the preview re-run. |
| **F2-R12** | Card and processor accounts MUST be created before their previews run. |
| **F2-R13** | Starting-balance confirmation MUST be idempotent and MUST warn rather than block on a divergent override. |
| **F2-R14** | Starting-balance cards MUST appear only for accounts the import touched. |
| **F2-R15** | The email step MUST launch the provider's own authorisation flow rather than embedding it. |
| **F2-R16** | The budget step MUST seed a first month's envelope assignments. |
| **F2-R17** | The tax step MUST seed the chosen country's deduction corpus. |
| **F2-R18** | Completion MUST raise exactly one event, the first time the user reaches the finish. |
| **F2-R19** | Step state MUST be enforced at the database layer. |
| **F2-R20** | A fatal parse error MUST be surfaced from the preview with the file named. |
| **F2-R21** | Cross-user access to a wizard surface MUST return not-found. |

## Related

- [A2 Import preview and confirm](../a-ingestion/a2-import-wizard.md) · [A9 Starting balances](../a-ingestion/a9-starting-balances.md)
- [A4 Email scanning](../a-ingestion/a4-email-scanning.md)
- [D1 Envelope budgeting](../d-money/d1-envelope-budgeting.md) · [D4 Tax](../d-money/d4-tax.md)
- [F3 Authentication](f3-auth-and-app-lock.md) — signup precedes the wizard
- [J1 First run](../../journeys/j1-first-run.md)
