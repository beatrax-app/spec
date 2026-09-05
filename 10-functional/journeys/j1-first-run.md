# J1 — First run

**Status:** Accepted

> The hardest moment in the product. Someone has downloaded an application from
> a maintainer they do not know, and now has to hand it their entire banking
> history. Everything about this journey has to earn that.

---

## Precondition

A downloaded installer. No account, no data, no configuration.

## The path

### 1. Install

The installer runs. On macOS and on Windows it carries a paid developer
identity — with notarisation on macOS — and the release build refuses to publish
one that does not, so the first-launch dialogue those two platforms used to
raise is gone
([ADR-0032](../../00-overview/decisions/0032-all-four-stores-additive-to-direct-download.md),
[F8-R2](../features/f-platform/f8-app-store-distribution.md#acceptance-criteria)).
Linux ships unsigned and raises no such dialogue.

Where a platform does warn, the published install instructions walk the exact
click sequence and **explain why the warning appears** rather than telling the
user to ignore it. A user who is told to click past a security warning without a
reason has learned a bad habit; one who is told why has learned something true.
That was the whole of this step until paid identities were adopted
([the rationale](../../90-appendix/license-rationale.md#why-no-paid-signing-certificates)),
and it is kept because it is still how the honesty is meant to work, not because
the warning is still there.

*Exercises: [F1](../features/f-platform/f1-desktop-shell.md).*

### 2. First launch

The shell boots, migrations run, the application key is minted behind its
sentinel, and the first window opens. All of it idempotent, so a crash and a
relaunch is not a special case.

*Exercises: [F1](../features/f-platform/f1-desktop-shell.md).*

### 3. Create the owner account

Username and password. Then **ten recovery codes, shown once**, with an
acknowledgement that they have been saved. There is no email in this product, so
this is genuinely the recovery path and the copy says so
([G5](../features/g-ux/g5-plain-language.md)).

Signup closes behind them.

*Exercises: [F3](../features/f-platform/f3-auth-and-app-lock.md).*

### 4. The setup wizard

Nine steps. The connector steps are skippable; someone with only a bank export
is not blocked by a card step.

For each connector the user chooses a source format and uploads the file they
already have. Each upload is **staged**, not committed.

*Exercises: [F2](../features/f-platform/f2-setup-wizard.md), [A1](../features/a-ingestion/a1-source-formats.md), [A2](../features/a-ingestion/a2-import-wizard.md).*

### 5. Name the accounts

The first upload contains account identifiers Beatrax has never seen. Rather than
failing, the preview collects them, de-duplicates them, and asks for a name for
each. Naming creates the account and re-runs the preview.

Card and payment-processor sources carry no bank account number, so their
accounts are created with synthetic identifiers before the preview runs — the
ordering matters.

*Exercises: [A2](../features/a-ingestion/a2-import-wizard.md), [B1](../features/b-ledger/b1-transactions.md).*

### 6. Confirm starting balances

Where a statement carries an opening balance it is detected and offered for
confirmation. Where it does not — a CSV, a processor export — the user is asked.
Where two sources disagree, both are shown and the user chooses.

*Exercises: [A9](../features/a-ingestion/a9-starting-balances.md).*

### 7. Review everything, then commit once

The consolidated preview shows every staged source grouped by format with a
sample of each. **Nothing has touched the ledger yet.**

Committing is all-or-nothing: every import, every starting balance, and the
wizard's own progress land in one transaction.

*Exercises: [F2](../features/f-platform/f2-setup-wizard.md), [A2](../features/a-ingestion/a2-import-wizard.md), [A3](../features/a-ingestion/a3-idempotency.md).*

### 8. The system goes to work

After the commit — never inside it — chain resolution, transfer pairing,
counterparty resolution, categorisation, recurring detection, and the first
forecast all run.

This is the moment the product either delivers or does not: a payment-processor
charge and its funding debit become one chain; a bulk card settlement decomposes
into the merchant lines it covered; the fixed monthly payments appear as a set.

*Exercises: [B2](../features/b-ledger/b2-categorisation.md), [B4](../features/b-ledger/b4-counterparties.md), [B5](../features/b-ledger/b5-chain-resolution.md), [B6](../features/b-ledger/b6-transfers.md), [C2](../features/c-insight/c2-recurring.md), [C5](../features/c-insight/c5-forecasting.md).*

### 9. Budget and tax steps

A first month of envelope assignments is seeded — an empty grid is not a useful
starting state — and a tax country seeds the deduction corpus. Both skippable.

*Exercises: [D1](../features/d-money/d1-envelope-budgeting.md), [D4](../features/d-money/d4-tax.md).*

### 10. The dashboard

In, out, net for the period. Top categories. What needs attention: uncategorised
transactions, unknown counterparties, chain candidates, recurring suggestions.

The queues are populated and that is correct — a first import produces things
the system is not sure about, and saying so is [P4](../../00-overview/vision.md#p4--precision-over-recall-and-never-a-silent-guess).

*Exercises: [C1](../features/c-insight/c1-dashboard.md).*

## Features exercised

[F1](../features/f-platform/f1-desktop-shell.md) ·
[F2](../features/f-platform/f2-setup-wizard.md) ·
[F3](../features/f-platform/f3-auth-and-app-lock.md) ·
[A1](../features/a-ingestion/a1-source-formats.md) ·
[A2](../features/a-ingestion/a2-import-wizard.md) ·
[A3](../features/a-ingestion/a3-idempotency.md) ·
[A9](../features/a-ingestion/a9-starting-balances.md) ·
[B1](../features/b-ledger/b1-transactions.md) ·
[B2](../features/b-ledger/b2-categorisation.md) ·
[B4](../features/b-ledger/b4-counterparties.md) ·
[B5](../features/b-ledger/b5-chain-resolution.md) ·
[B6](../features/b-ledger/b6-transfers.md) ·
[C1](../features/c-insight/c1-dashboard.md) ·
[C2](../features/c-insight/c2-recurring.md) ·
[C5](../features/c-insight/c5-forecasting.md) ·
[D1](../features/d-money/d1-envelope-budgeting.md) ·
[D4](../features/d-money/d4-tax.md) ·
[G2](../features/g-ux/g2-error-model.md) ·
[G5](../features/g-ux/g5-plain-language.md)

## How this journey fails

| Failure | Why it is fatal |
|---------|-----------------|
| An install warning that is raised is not explained | The user either abandons, or learns to click past warnings. Both are bad outcomes. |
| A wrong format selection produces a stack trace | The user concludes the product is broken on their first interaction. |
| Recovery codes are shown without an acknowledgement | The user loses them and discovers it a year later. |
| The first import partially commits | A state nobody designed, in the ledger, before the user has any way to judge what is wrong. |
| Chain resolution finds nothing | The product's central claim is unproven at exactly the moment it needs proving. |
| The triage queues are framed as errors | The user reads a working system as a broken one. |
| Uploading the same file twice creates duplicates | The idempotency promise fails at its first test. |

## Related

- [J2 Daily use](j2-daily-use.md) — what this leads into
- [J7 Migrating from another tool](j7-migrating.md) — the alternative first run
- [00-overview/vision.md](../../00-overview/vision.md)
