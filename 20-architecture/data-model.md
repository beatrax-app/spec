# Data model

**Status:** Accepted

One file per installation, holding the application schema, the queue tables, the
cache and lock tables, and sessions — all co-resident, all in write-ahead
journal mode ([ADR-0005](../00-overview/decisions/0005-sqlite-wal.md)).

This page describes the schema at the level the architecture depends on: who
owns what, which columns carry trust-boundary semantics, and which have state
machines.

## Structural rules

| Rule | Requirement |
|------|-------------|
| Every user-scoped table carries a user reference | [ARCH-R6](README.md#the-arch-r-namespace) |
| Every monetary value is a minor-unit integer plus a currency code | [ARCH-R7](README.md#the-arch-r-namespace) |
| Every state column has exactly one sanctioned mutator | [ARCH-R5](README.md#the-arch-r-namespace) |
| Migrations are per-module and append-only | [ARCH-R10](README.md#the-arch-r-namespace) |

Migrations sort globally by timestamp, so cross-module references work — but a
column on a table belongs in its **owning** module's migrations, and adding one
elsewhere is wrong by definition.

## Tables by owner

### Core

Users; sessions; system alerts; user preferences.

The user record carries the owner and developer flags, the forced-change flag,
and the per-user settings the product accumulated: theme, currency view, period
start day, detection windows, thresholds, drop-folder behaviour, close
behaviour, community settings, tax country, and the activation and backfill
anchors.

The framework's password-reset token table exists and goes unused
([ADR-0010](../00-overview/decisions/0010-recovery-codes-no-smtp.md)).

### Auth

Recovery codes, hashed, unique per user and hash, with a state machine on
consumption. Provider secrets, encrypted at rest and written through a single
repository.

### Ledger — the canonical store

Accounts; transactions; categories; merchants; merchant memories; currencies;
import runs; statement summaries; card statements and their credits; split legs.

**Transactions** carry: the user and account references; booking, posting, and
value dates; the native and settled amounts with their currencies and the
derived rate; optional counterparty and category references; the transaction and
payment type enums; the fingerprint; the source reference; the append-only
provenance trail; the pair pointer; the raw parser payload; the note; the field
provenance map; and the reconciliation status.

### Counterparties

Counterparties, unique per user and slug, with a trigger-enforced type enum and
a per-type metadata payload.

### Categorization

Rules with their condition and action child tables; merchant aliases; merchant
memories; pending enrichment conflicts.

### Recurring · DriftAlerts · Anomaly

Series, their occurrences, and their transition audit trail. Drift alerts and
their transitions. Anomaly alerts — unique per transaction, aggregating reasons
— and suppression rules.

### Forecasting

Runs with their result payload; scenarios, unique per user and name; scenario
mutations; derived shortfall windows.

### Chains

The chain-link ledger with its confidence and evidence payload; resolution-run
audit records; the learnt identifier alias bridge.

### Budgets · Goals · Pots · Tax

Envelope assignments, moves, and settings. The legacy flat budget table, now
write-dead. Goals. Pot movements — **no pot balance column exists**; a pot's
balance is the signed sum of its movements. Tax tags, optionally scoped to a
split leg.

### EmailScan · Receipts

Inboxes; inbox messages; per-inbox scan state; known and discovered senders.
File-import records.

### Sync

Operation-log entries; the quarantine; clock state; the device registry; pairing
tokens; sessions; the relay mailbox; encryption state.

### Search · Reports · Migration · Community · Onboarding · DevMode

The search document table and its full-text index. Saved reports. Migration runs,
staging tables, the source map, and the import baseline. The community mapping
corpus, whose global tier deliberately has no user reference. Wizard progress.
The developer audit trail.

### Framework

Queue, batch, and failed-job tables; cache and lock tables — the lock table is
where overlap guards live.

## Trust-boundary columns

A handful carry semantics the rest of the codebase treats as load-bearing:

| Column | Semantics |
|--------|-----------|
| **The fingerprint** | Unique per user, account, and value. This index is what makes idempotent import structural rather than procedural. Changing its algorithm is a forward migration that re-derives every row. |
| **The provenance trail** | Append-only. Never overwritten; each enrichment appends. |
| **The pair pointer** | Written **only** by the chain resolver and the transfer matcher. Every other write is forbidden by architecture test. |
| **The payment type** | A typed enum; every literal must live in the enum, enforced by architecture test. |
| **The raw payload** | Kept for debugging and future re-derivation. Not read by application logic at runtime. Encrypted at rest. |
| **The field provenance map** | Records whether each field came from a rule or from the user. Rule re-application reads it and skips manual fields. |
| **The reconciliation status** | Reconciled rows are locked against every mutation. |
| **The key epoch** | Which encryption generation a row's ciphertext belongs to. |

## State columns and their machines

Each has exactly **one** sanctioned mutator, enforced by architecture test and,
where the store supports it, by paired triggers that reject an out-of-enum
value.

| Column | Lifecycle |
|--------|-----------|
| Recurring series state | pending → approved \| rejected \| snoozed; snoozed → pending \| approved \| rejected; approved ↔ cadence-changed; rejected → pending |
| Drift alert state | open → acknowledged \| snoozed \| dismissed-as-cancelled; snoozed → open \| acknowledged \| dismissed-as-cancelled |
| Anomaly alert state | as drift, **plus** dismissed → open, the undo edge |
| Inbox scan state | idle → discovering → scanning → idle; any → error; error → idle; needs-reauth terminal but for idle |
| Card statement state | open → partially settled → settled \| overpaid |
| Chain link state | candidate → confirmed \| rejected |
| Resolution run state | pending → running → complete \| failed |
| Forecast run state | pending → running → complete \| failed |
| Recovery code state | unused → consumed |
| Pairing state | pending → awaiting confirmation → confirmed; → expired |
| Notification state | open → resolved |
| Transaction status | uncleared → cleared → reconciled; reconciled → cleared |
| Import run status | previewed → confirmed \| discarded |
| Migration run status | parsed → confirmed \| discarded \| needs attention |
| Wizard step status | pending \| in progress \| done \| skipped |
| Pot status | active ↔ archived |

Where a lifecycle has an audit trail — recurring series, drift alerts, anomaly
alerts — every transition writes an append-only row recording the from-state,
the to-state, the time, and the actor.

## Encryption at rest

A single registry defines the encrypted set
([ADR-0018](../00-overview/decisions/0018-amounts-plaintext-at-rest.md)):

**Encrypted** — transaction description, counterparty name and identifier, raw
payload, and note; counterparty display name, merchant name, and identifier; tax
notes; split-leg notes; notification title, body, parameters, and trigger kind.

**Plaintext, deliberately** — amounts, dates, account references, type enums,
and the search index body.

**Knowingly-accepted plaintext exceptions** — the recurring cluster key, the
migration baseline value, and the stored and incoming values on
enrichment-conflict rows. Named rather than hidden.

## Migrations are append-only

Never modify a shipped migration. A schema change is a new forward migration.

The canonical example is the fingerprint version change, which shipped as a
separate migration that re-derived every row rather than as an edit to the
original.

This matters because a user upgrading from an earlier version runs the new
migrations **on top of their populated database**. The only way to guarantee
they apply cleanly is for every change to be its own forward step.

## Related

- [ADR-0005](../00-overview/decisions/0005-sqlite-wal.md) · [ADR-0008](../00-overview/decisions/0008-multi-user-belongstouser.md) · [ADR-0009](../00-overview/decisions/0009-brick-money-multi-currency.md) · [ADR-0018](../00-overview/decisions/0018-amounts-plaintext-at-rest.md)
- [component-model.md](component-model.md) · [data-flow.md](data-flow.md)
- [contracts/op-log.md](contracts/op-log.md)
