# B3 — The rules engine

**Status:** Accepted · **Area:** B — The ledger

---

## Purpose

Category assignment was only ever the first thing a user wanted a rule to do.
"Every charge from this payee should also be renamed, tagged, and noted" is the
natural next request, and answering it with three separate single-purpose
mechanisms would be three sets of ordering semantics to get wrong.

This feature generalises categorisation rules into conditional rules with
multiple conditions and multiple actions — set a category, rename a
counterparty, set a note or a tag, set other supported fields — running
deterministically on import and re-applicable to history on demand.

## Behaviour

### A rule is conditions plus actions

A rule carries at least one condition and at least one action. Conditions
combine with either *all* or *any*. Each condition names a field, an operator,
and one or two values; each action names a type and a payload.

The operator set is constrained per value type: text supports contains, equals,
and starts-with; amounts support greater-than, less-than, between, and equals;
dates support before, after, and between. A between comparison requires its
second value. Amount values are already signed minor-unit integers by the time
they are stored — parsing happens once, at the edge.

The combinator and the enums are enforced at the database layer as well as in
the application, so a bug that produces an invalid rule fails loudly.

### Writes are validated and atomic

Creating or updating a rule validates everything before writing: the structural
minimum, the combinator, the operator-and-type matrix, the between second value,
the field name, and — critically — that every identifier embedded in an action
resolves to something the caller can actually see. That last check is what stops
a rule from being used to probe for the existence of another user's records.

Updates reconcile child rows by a targeted diff that preserves identity rather
than deleting and re-inserting everything, so a rule's history survives an edit.
An identifier supplied by the caller that does not belong to the rule being
edited is treated as absent rather than adopted.

Deletion is a lookup-then-delete inside one transaction. **Deleting a rule never
retroactively un-categorises anything it matched** — the ledger records what was
decided, not what a rule currently says.

### Matching is pure

The matcher has no side effects and is shared, unchanged, by the import path and
the re-apply path. That sharing is the reason a re-apply produces the same
answer the import would have.

### Two application modes

**At import**, the rule's actions fold onto the in-flight transaction before it
is written. Nothing is logged to the sync op-log, nothing is written to the
database, and no event fires — because the transaction does not exist yet. Tax
tagging is skipped at import for exactly that reason: there is no transaction
identifier to tag.

**On re-apply**, every field write is delegated to the same public writers the
rest of the product uses. Rules are first reduced to one desired action per
type, so ordering resolves before any write happens.

Where two actions of the same type conflict, the last one wins by execution
order. That is a stated rule, not an accident.

### Manual edits are never overwritten

Each field records whether its current value came from a rule or from the user.
A re-apply reads that provenance once, up front, and **skips any field the user
set by hand**. A rule cannot silently undo a deliberate correction.

### Re-apply is explicit, idempotent, and bounded

Re-application is a user-triggered job, not a side effect of editing a rule. It
walks history in chunks, skips split transactions entirely (their legs carry
their own categories), skips reconciled rows (which are locked), and reports
progress. A row whose match or apply throws is skipped and counted, never
allowed to abort the run.

Running it twice changes nothing the first run did not already change.

### Under at-rest encryption

Matching decrypts the fields it needs before comparing, because comparing
ciphertext to a plaintext pattern never matches. Re-apply therefore runs where
the key is available; a context without the key logs a warning once per run
rather than silently producing an empty result.

### Migrating forward

Existing category-assignment rules migrate into the new shape with no behaviour
change. A user who never opens the rule builder sees exactly what they saw
before.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| A rule with no conditions or no actions | Rejected at write time. |
| A between condition with no second value | Rejected at write time. |
| An action referencing a record the caller cannot see | Rejected at write time. |
| A malformed action payload at apply time | That action is skipped and logged; the others still apply. |
| Two actions of the same type on one rule | Last by execution order wins. |
| A field the user set by hand | Never overwritten by re-apply. |
| A split transaction during re-apply | Skipped entirely. |
| A reconciled transaction during re-apply | Skipped. |
| Re-apply with no encryption key available | Warns once per run; does not silently return nothing. |
| Deleting a rule | Past assignments stand. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **B3-R1** | A rule MUST support multiple conditions combined by all-or-any, and multiple actions. |
| **B3-R2** | Supported actions MUST include setting a category, renaming a counterparty, and setting notes or tags. |
| **B3-R3** | Operators MUST be constrained per value type, and an invalid pairing MUST be rejected at write time. |
| **B3-R4** | A between condition MUST require a second value. |
| **B3-R5** | Amount values MUST be stored as signed minor-unit integers; parsing MUST happen at the edge, once. |
| **B3-R6** | The combinator and enum values MUST be enforced at the database layer as well as the application layer. |
| **B3-R7** | Every identifier embedded in an action MUST be validated as visible to the caller before any write. |
| **B3-R8** | Rule updates MUST reconcile child rows by an identity-preserving diff, never delete-all-then-reinsert. |
| **B3-R9** | An identifier supplied by the caller that does not belong to the rule being edited MUST be treated as absent. |
| **B3-R10** | Deleting a rule MUST NOT retroactively undo assignments it made. |
| **B3-R11** | The matcher MUST be side-effect-free and MUST be shared unchanged between the import and re-apply paths. |
| **B3-R12** | Rule and action ordering MUST be deterministic. |
| **B3-R13** | At import, actions MUST fold onto the in-flight transaction with no database write, no event, and no sync capture. |
| **B3-R14** | Tax tagging MUST be skipped at import and applied only on re-apply. |
| **B3-R15** | On re-apply, every field write MUST be delegated to the product's existing public writers. |
| **B3-R16** | Conflicting actions of the same type MUST resolve last-writer-wins by execution order. |
| **B3-R17** | Each field MUST record whether its value came from a rule or from the user. |
| **B3-R18** | Re-apply MUST skip any field whose provenance is manual. |
| **B3-R19** | Re-apply MUST be user-triggered, MUST be idempotent, and MUST NOT run as a side effect of editing a rule. |
| **B3-R20** | Re-apply MUST skip split transactions and reconciled transactions. |
| **B3-R21** | A row whose match or apply throws during re-apply MUST be skipped and counted, never abort the run. |
| **B3-R22** | Matching MUST decrypt encrypted fields before comparison. |
| **B3-R23** | Re-apply without an available encryption key MUST warn once per run rather than silently matching nothing. |
| **B3-R24** | Existing category-assignment rules MUST migrate forward with no behaviour change. |
| **B3-R25** | Cross-user rule reads and writes MUST return not-found. |

## Related

- [B2 Categorisation and merchant memory](b2-categorisation.md) — what this generalises
- [B4 Counterparties](b4-counterparties.md) — the rename target
- [B7 Splits](b7-splits.md) · [B8 Reconciliation](b8-reconciliation.md) — the two skip conditions
- [D4 Tax tagging](../d-money/d4-tax.md)
- [E4 At-rest encryption](../e-sync/e4-at-rest-encryption.md)
