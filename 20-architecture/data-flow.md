# Data flow

**Status:** Accepted

The end-to-end path from a source file to a figure on a screen, and the
boundaries that make each step safe to re-run.

## The ingestion pipeline

Every transaction Beatrax ever shows enters through the same pipeline. Source
formats feed in at parse; everything past parse is uniform.

```text
  source file
      │
      ▼
┌─────────────┐
│ 1  Parse    │  format-specific adapter → source rows.  No DB writes.
└─────────────┘
      │
      ▼
┌─────────────┐
│ 2  Account  │  which of the user's accounts owns this row?
│    resolve  │  unknown → a naming prompt, de-duplicated across the file
└─────────────┘
      │
      ▼
┌─────────────┐
│ 3  Normalise│  → one canonical shape: dates, exact money, both currencies,
└─────────────┘     the derived rate, counterparty, account, user
      │
      ▼
┌─────────────┐
│ 4  Classify │  income / expense / transfer direction / refund / fee /
│    type     │  adjustment — by prior classification, then two independent
└─────────────┘  cross-account identifier checks, then a source event map,
      │          then the subtractive income rule
      ▼
┌─────────────┐
│ 5  Payment  │  per-source hinters in registration order; the generic
│    type     │  fallback is registered last, by invariant
└─────────────┘
      │
      ▼
┌─────────────┐
│ 6  Category │  rules and merchant memory, above the confidence bar.
└─────────────┘  Below it: uncategorised, honestly.
      │
      ▼
┌─────────────┐
│ 7  Counter- │  the seven-step precedence chain; the resolved reference
│    party    │  rides into the persisted row
└─────────────┘
      │
      ▼
┌─────────────┐
│ 8  Finger-  │  new / duplicate / enriched.  ← the preview/confirm boundary
│    print    │
└─────────────┘
      │
      ▼
   PREVIEW  ─────────────── nothing has been written ───────────────
      │
      │  the user reviews, answers the naming prompts, and confirms
      ▼
   CONFIRM
      │
      ├─ phase 1: record, in bounded idempotent chunks (no outer transaction)
      │
      ├─ phase 2: apply enrichments + flip status  (one transaction)
      │
      └─ after commit, in order:
            promote card statements
            dispatch chain resolution + recurring detection
```

Per-row exceptions between stages 4 and 8 become error rows; the file continues.
An adapter-level failure becomes one error row for the whole file, so the wizard
still renders.

*Owned by [A1](../10-functional/features/a-ingestion/a1-source-formats.md),
[A2](../10-functional/features/a-ingestion/a2-import-wizard.md),
[A3](../10-functional/features/a-ingestion/a3-idempotency.md).*

### Why confirm splits into two phases

A full-year confirm must not be one transaction
([ARCH-R17](README.md#the-arch-r-namespace)). Recording therefore commits in
bounded chunks — a crash leaves committed rows a re-run completes idempotently.
Enrichment and the status change commit together, so a confirmed status always
implies the enrichments landed.

Dispatching inside the transaction would let a worker observe uncommitted state
([ARCH-R18](README.md#the-arch-r-namespace)).

## The receipt path

```text
  inbox scan  ──┐
                ├──▶ matcher registry ──▶ enrichment  ──▶ [A3] shared path
  dropped file ─┘         │                                    │
                          ├──▶ statement summary ──▶ shared path
                          └──▶ chain hints ──▶ [B5]
```

Receipts never write to the ledger directly. Everything goes through the shared
enrichment and statement paths, enforced by architecture test.

*Owned by [A4](../10-functional/features/a-ingestion/a4-email-scanning.md),
[A5](../10-functional/features/a-ingestion/a5-receipt-matching.md).*

## The post-commit passes

Dispatched after the import transaction, in order, and run where the at-rest key
is available:

```text
1  promote card statements     (idempotent, ungated on insert count)
2  retype by alias             ← the healing pass; corrects file-order damage
3  pair transfer orphans       ← now sees a corrected ledger
4  resolve settlements         ← decomposes bulk card settlements
5  resolve funding chains      ← three arms, deterministic → direct → fuzzy
6  detect recurring series
7  detect anomalies (queued)
8  evaluate drift
9  re-project forecasts
```

Ordering is load-bearing at every step. Step 2 must precede 3, 4, and 5 or they
iterate an empty set; step 1 must precede 4 or there is nothing to settle
against.

*Owned by [B5](../10-functional/features/b-ledger/b5-chain-resolution.md),
[B6](../10-functional/features/b-ledger/b6-transfers.md),
[C2](../10-functional/features/c-insight/c2-recurring.md)–[C5](../10-functional/features/c-insight/c5-forecasting.md).*

## The sync path

```text
  local mutation
      │
      ▼
  capture listener  ──▶ op-log entry, signed, clock-ordered
      │                        │
      │                        ▼
      │                   transport  ── LAN-direct, or relay
      │                        │
      │                        ▼
      ▼                    peer device
  local DB                     │
                               ▼
                          replayer ──▶ merge registry
                               │            │
                               │            ├─ last-writer-wins per field
                               │            ├─ grow-only counter
                               │            └─ observed-remove set
                               │
                               ├─ refused ──▶ quarantine (with a reason)
                               │
                               └─ applied ──▶ peer's DB + search index
```

The database is a materialised view: replaying the merged log from scratch
reproduces it ([ARCH-R11](README.md#the-arch-r-namespace)).

*Owned by [E1](../10-functional/features/e-sync/e1-change-capture.md)–[E4](../10-functional/features/e-sync/e4-at-rest-encryption.md).*

## The read path

Reads compose from public surfaces rather than from raw cross-module queries.

```text
  dashboard ──▶ position summary ──┬─▶ period aggregate      (Ledger)
                                   ├─▶ budget status         (Budgets)
                                   ├─▶ upcoming charges      (Recurring)
                                   └─▶ shortfall risk        (Forecasting)

  calendar  ──▶ recurring series + forecast + real history
  reports   ──▶ split-aware aggregation + currency mode + time buckets
  search    ──▶ full-text index (+ bounded fallback for short queries)
```

Each is bounded: the period aggregate is one read; badge counts are one pass;
the calendar fetches each account's forecast once per render, not once per day;
the fixed-payments view is bounded regardless of series count, verified by test.

## Where encryption sits

```text
  write:  plaintext ──▶ encrypt registered columns ──▶ store
  read:   store ──▶ decrypt registered columns ──▶ match / parse / display
```

**Every** read of a registered column decrypts before comparing. A predicate
against ciphertext never matches; a display of ciphertext shows gibberish. This
is the most common defect class in the design and it is guarded by a
registry-keyed regression test
([ARCH-R13](README.md#the-arch-r-namespace),
[ADR-0018](../00-overview/decisions/0018-amounts-plaintext-at-rest.md)).

Amounts, dates, and the search index stay plaintext because aggregation and
search depend on them.

## Related

- [component-model.md](component-model.md) · [data-model.md](data-model.md)
- [contracts/op-log.md](contracts/op-log.md)
- [A3 Idempotency](../10-functional/features/a-ingestion/a3-idempotency.md)
