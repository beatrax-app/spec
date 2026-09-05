# B4 — Counterparties and triage

**Status:** Accepted · **Area:** B — The ledger

---

## Purpose

A bank statement identifies the other side of a transaction as a string of
characters, an account number, or both, in a form that changes between
statements. Grouping those into one stable identity per merchant, person, bank,
or agency is what makes "how much did I spend at this shop this year" a question
with an answer.

This feature owns that identity: resolving it, typing it, letting the user
correct it, and keeping personal identifiers out of places they should not be.

## Behaviour

### Seven steps, first match wins

Resolution walks a fixed precedence chain and stops at the first hit. The order
is load-bearing:

1. **The user's own account** — a transfer between the user's accounts is not a
   counterparty at all. It short-circuits with no record created and routes to
   the account instead.
2. **A known institution identifier** — the payment processor's own account, the
   card issuer's settlement account. Typed as a bank. This must come before
   merchant matching, or a processor charge resolves as a merchant.
3. **Merchant resolution** — via the alias and corpus layers below.
4. **Personal-identifier heuristic** — a structurally valid account number,
   checksum-verified, paired with a name that lacks any company marker, on a
   transfer row. Typed as personal.
5. **Government keywords** — typed as government.
6. **Bank-fee keywords** — typed as bank, with a fee marker.
7. **Unresolved** — typed as unknown, with the identifier preserved for triage.

Merchant before personal is deliberate: a genuine merchant that happens to have
a domestic account number must never be typed as a person.

### The type drives the product

Six types — merchant, personal, bank, government, self-account, unknown — with
their own visual language, their own profile layout, and their own filters. The
type set is enforced at the database layer.

### Personal identifiers never enter a URL

The privacy default: a slug is derived from the display name alone. An account
number is preserved on the record for the profile page to show behind an
explicit action, but it never appears in a slug, a route, or the index view's
data shape. The index row type does not even carry the field.

Slugs are unique per user, resolved by a suffix walk on collision, with a
database-level guarantee underneath. Under at-rest encryption the walk decrypts
each candidate's stored name before comparing — comparing ciphertext would
fragment one merchant across an endless series of suffixed slugs.

### Triage is keyboard-first

Transactions whose counterparty could not be resolved land in a triage queue.
Each row shows the identifier, its recent activity, and a suggestion derived
from walking the recent descriptions through the merchant resolver and tallying
agreement — high, medium, or low confidence, or none.

The queue is driven from the keyboard: accept, reject, skip, next, close. Typing
into a field routes keys to the field rather than the shortcut handler.

Labelling one identifier labels every transaction that shares it.

### Merchant name resolution

A raw description becomes a friendly merchant name by a five-step precedence:
the user's exact alias, the user's generalised alias, the community corpus's
exact entry, the community corpus's generalised entry, and finally nothing — in
which case the raw description renders in a visually distinct way rather than
pretending to be a name.

Generalisation strips the parts of a description that vary per transaction —
the terminal identifier, the card tail, the reference prefixes, embedded amounts
and dates — and lower-cases the remainder. The output is always a literal
substring target, never a pattern language.

Resolution happens at render time. **The stored description is never rewritten.**

Aliases can be exported and imported as a file, with a diff that classifies each
entry as new, unchanged, or conflicting before anything is written, and the
whole application commits in one transaction. Aliases can also be merged, with
the surviving record keeping a record of what was absorbed.

An alias can be tested live against the user's own recent transactions before
being saved, showing how many rows it would match and a sample of them.

### Garbage collection is conservative

Counterparties with no recent activity are pruned daily — but a record survives
if **either** a transaction in the last year references it **or** an alias
anchors it. Both anchors must be absent before anything is removed.

Pruning **never deletes transactions**. The reference on affected transactions is
cleared first, in the same transaction, and only then is the counterparty
removed. History is never collateral damage.

Where the relevant column is encrypted and no key is available — the pruning job
runs on a schedule, without a user session — the ciphertext-dependent half of
the check is skipped with a warning rather than guessed at. Preserving data
under uncertainty is the correct default.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| No identifier, no description, no name | Unresolved; stays in triage. |
| A merchant renamed in the alias table | The stored slug does not move; the rename surfaces at render. |
| Two users each with the same merchant | Per-user slug uniqueness; each is invisible to the other. |
| An unknown record that becomes resolvable later | A new record is created; the stale unknown is pruned by the next sweep. |
| A personal record whose identifier is later recognised as an institution's | Later imports resolve it as a bank; the old record decays via pruning. |
| Pruning during an import | Recent-activity exclusion means a just-imported record cannot be pruned in the same pass. |
| An exception during resolution at import | Not caught — the chain is designed to be exception-free for valid input, so an exception is a defect worth surfacing. |
| An alias shorter than the minimum length | Rejected with an explanation. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **B4-R1** | Resolution MUST walk a fixed precedence chain and stop at the first match. |
| **B4-R2** | A transfer between the user's own accounts MUST resolve to the account and MUST NOT create a counterparty record; self_account is therefore a resolution outcome, never a stored row. |
| **B4-R3** | Known institution identifiers MUST be resolved before merchant matching. |
| **B4-R4** | Merchant matching MUST be attempted before the personal-identifier heuristic. |
| **B4-R5** | The personal-identifier heuristic MUST require a checksum-valid account number and the absence of company markers. |
| **B4-R6** | The type set MUST be closed and enforced at the database layer. Only the types resolution can store are reachable in a real install, and a reader-facing filter or profile for self_account MUST NOT be offered where it can only ever be empty. |
| **B4-R7** | A slug MUST be derived from the display name alone; an account identifier MUST NOT appear in any slug or route. |
| **B4-R8** | The index view's data shape MUST NOT carry an account identifier at all. |
| **B4-R9** | Slugs MUST be unique per user, resolved by suffix walk with a database-level guarantee underneath. |
| **B4-R10** | Under at-rest encryption, the slug collision walk MUST decrypt stored names before comparing. |
| **B4-R11** | Resolution MUST be idempotent: re-resolving the same transaction MUST return the same record and insert nothing. |
| **B4-R12** | Unresolved counterparties MUST surface in a triage queue with their recent activity and a confidence-rated suggestion. |
| **B4-R13** | Labelling one identifier MUST label every transaction sharing it. |
| **B4-R14** | Triage MUST be operable entirely from the keyboard, and shortcuts MUST NOT fire while a text field has focus. |
| **B4-R15** | Merchant-name resolution MUST follow the five-step precedence: user exact, user generalised, corpus exact, corpus generalised, none. |
| **B4-R16** | An unresolved name MUST render visually distinct from a resolved one. |
| **B4-R17** | Resolution MUST happen at render time; the stored description MUST NOT be rewritten. |
| **B4-R18** | Generalisation MUST produce a literal substring target, never a pattern language. |
| **B4-R19** | Alias import MUST produce a new-versus-unchanged-versus-conflicting diff before writing, and MUST apply in one transaction. |
| **B4-R20** | Merging aliases MUST preserve a record of what was absorbed. |
| **B4-R21** | An alias MUST be testable against the user's own recent transactions before being saved. |
| **B4-R22** | Garbage collection MUST preserve a record anchored by either recent activity or an alias. |
| **B4-R23** | Garbage collection MUST clear the transaction reference before deleting, and MUST NOT delete transactions. |
| **B4-R24** | Where garbage collection cannot decrypt a value it needs, it MUST skip that check with a warning rather than deleting. |
| **B4-R25** | Cross-user reads MUST return not-found, revealing nothing about whether another user owns the slug. |

## Related

- [B2 Categorisation](b2-categorisation.md) · [B3 The rules engine](b3-rules-engine.md) — the rename action
- [B5 Funding-chain resolution](b5-chain-resolution.md) — consumes the alias bridge
- [C9 Community merchant corpus](../c-insight/c9-community-corpus.md)
- [G1 Privacy stance](../g-ux/g1-privacy.md) · [G6 Keyboard](../g-ux/g6-keyboard.md)
