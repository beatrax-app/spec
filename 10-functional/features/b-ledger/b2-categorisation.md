# B2 — Categorisation and merchant memory

**Status:** Accepted · **Area:** B — The ledger

---

## Purpose

Every downstream number — budgets, reports, the spending breakdown, the tax
export — is a sum over categories. Getting categories right is therefore not a
convenience feature; it is the input to everything.

beatrax categorises deterministically, with no model and no cloud call, using
two cooperating layers: rules the user can read and edit, and a memory that
learns from their corrections.

## Behaviour

### Two layers, one winner

**Rules** match on description, counterparty, amount, or date and assign a
category. **Memory** records that this user, for this normalised merchant name,
chose this category — and grows every time they correct something.

Both layers produce candidates; the highest-scoring candidate wins. Scoring is
by specificity: an exact match beats memory, memory beats a prefix match, a
prefix beats a substring. At equal score the rule beats the memory, so an
explicit rule the user wrote always overrides a habit the system inferred.

All comparison is case-insensitive and Unicode-safe, and string matching happens
in application code rather than in SQL pattern syntax — which is both an
injection mitigation and the only way to get the Unicode semantics right.

Evaluation order is deterministic: a stable sort in the query, never a re-sort
afterwards.

### Uncategorised is an honest answer

If nothing clears the confidence bar, the transaction is left uncategorised and
lands in the triage queue. Assigning a wrong category silently mistrains the
memory layer and corrupts every downstream total, so beatrax would rather say
nothing.

The dashboard surfaces how many transactions need categorising, so the work does
not accumulate invisibly.

### Manual correction is the training signal

When the user categorises a transaction, that action records or strengthens a
merchant memory. The next similar transaction clears the bar on its own.

If a manual choice contradicts a rule that is still active, the user is told —
that is a signal their rule is wrong, and it is the only divergence worth
surfacing. Memory divergence is silent, because memory growing is the intended
behaviour rather than a conflict.

### Nothing is retroactive by default

Adding a rule does not silently re-walk history. The triage surface lets the
user re-categorise on demand, and the rules engine ([B3](b3-rules-engine.md))
offers an explicit, idempotent re-apply. Silent retroactive rewriting would
destroy the audit trail of what was decided when.

### The seed set is small and universal

A default set of rules seeds on first install, covering only merchants and
statement patterns that are universally true. It is deliberately small: high
precision on a handful of certainties, leaving everything else to the per-user
learning loop. A user can disable or edit any seed rule, and the scoring
tiebreak favours user-authored rules.

The default **category tree** is global — every user inherits the same starting
set — while rules are per-user.

### One buggy rule never breaks an import

Any exception from rule evaluation during import is caught: the row falls
through to uncategorised, a warning is logged with enough context to find the
rule, and the import continues.

### No cross-user training, ever

Merchant memories are strictly per-user. The optional community corpus
([C9](../c-insight/c9-community-corpus.md)) is a separate, opt-in dataset that
the categoriser never reads unless the user explicitly imports an entry into
their own rules.

### No model

The matchers are deterministic. The trade — visible explainability against the
higher recall a language model would offer — was made explicitly, and the
explainability is what lets a user fix a wrong categorisation at its source
instead of arguing with a black box.

### Provenance

Each automatic assignment records which rule or which memory made it. The triage
surface shows that provenance when the user re-categorises, so the correction can
be made at the rule or memory level rather than one row at a time.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| No rules and no memories | Everything lands uncategorised; the import still succeeds. |
| A transaction with the no-counterparty sentinel | The memory layer is skipped; only rules can match. |
| A rule with an unrecognised field or operator | Skipped silently by the evaluator; the database layer should have rejected it on write. |
| A user-authored rule that throws | Caught; the row falls back to uncategorised with a logged warning. |
| Concurrent imports matching the same rule | The rule's hit counter is incremented atomically, so it stays monotonic. |
| Re-running the seed on an existing install | Idempotent; an existing user-owned override with the same identity is never demoted. |
| A manual re-categorisation that changes nothing | No event, no memory write. |
| Corrupt provenance on a row | Treated as absent; the divergence check is skipped. |
| Deleting a category a rule references | The whole rule is deactivated, because a rule missing a required action is structurally invalid. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **B2-R1** | Categorisation MUST be deterministic; no model inference and no network call may be involved. |
| **B2-R2** | At most one category assignment MUST be produced per transaction, chosen by specificity score. |
| **B2-R3** | Exact matches MUST outrank memory, memory MUST outrank prefix matches, and prefix MUST outrank substring. |
| **B2-R4** | At equal score, a rule MUST beat a memory. |
| **B2-R5** | String matching MUST be case-insensitive, Unicode-safe, and performed in application code rather than SQL pattern syntax. |
| **B2-R6** | Evaluation order MUST be deterministic, established in the query and not re-sorted afterwards. |
| **B2-R7** | A transaction whose best candidate does not clear the confidence bar MUST be left uncategorised. |
| **B2-R8** | The count of uncategorised transactions MUST be surfaced to the user. |
| **B2-R9** | A manual categorisation MUST record or strengthen a merchant memory. |
| **B2-R10** | A manual choice contradicting a still-active rule MUST be surfaced to the user; a choice diverging only from memory MUST NOT be. |
| **B2-R11** | Adding or editing a rule MUST NOT retroactively re-categorise history; re-application MUST be an explicit user action. |
| **B2-R12** | Every rule and memory lookup MUST be scoped to the requesting user. |
| **B2-R13** | Merchant memories MUST NOT be shared between users under any circumstances. |
| **B2-R14** | An exception during rule evaluation at import MUST NOT abort the import; the row MUST fall back to uncategorised with a logged warning. |
| **B2-R15** | The default category tree MUST be global and shared; default rules MUST be per-user. |
| **B2-R16** | Re-running the default seed MUST be idempotent and MUST NOT demote a user-owned override. |
| **B2-R17** | Rule hit counters MUST be incremented atomically so they remain monotonic under concurrent imports. |
| **B2-R18** | Each automatic assignment MUST record which rule or memory produced it, and the triage surface MUST show it. |
| **B2-R19** | Categorisation MUST write the category only through the ledger's sanctioned category writer. |
| **B2-R20** | Deleting a category or counterparty a rule depends on MUST deactivate the whole rule. |
| **B2-R21** | A manual re-categorisation that changes nothing MUST emit no event and write no memory. |

## Related

- [B3 The rules engine](b3-rules-engine.md) — the generalised successor
- [B1 Transactions and the ledger](b1-transactions.md) — the sanctioned writer
- [C9 Community merchant corpus](../c-insight/c9-community-corpus.md) — opt-in, never automatic
- [A3 Idempotency and enrichment](../a-ingestion/a3-idempotency.md) — receipt-versus-statement conflicts
- [J2 Daily use](../../journeys/j2-daily-use.md)
