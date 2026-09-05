# B9 — Full-text search

**Status:** Accepted · **Area:** B — The ledger

---

## Purpose

History is retained forever ([P3](../../../00-overview/vision.md#p3--imports-are-idempotent-history-is-permanent)),
which is only valuable if it is reachable. Search is how a user answers "when
did I last pay this person", "what was that charge in March", and "find every
transaction with this word in the note" across years of data, fast.

## Behaviour

### An index kept in lockstep with writes

A full-text index covers counterparty name, description, and tax note. It is
updated **synchronously, in the same transaction as the write that caused it** —
not on a queue, not on a schedule.

The writer does not swallow failures. A failed index write rolls back the import
chunk that produced it, so the index and the table can never silently diverge.
An index that is quietly stale is worse than an import that visibly failed.

Fields are concatenated with a separator that the tokeniser cannot index, so a
query cannot accidentally match across a field boundary.

The writer verifies that the caller-supplied user actually owns the row it is
indexing.

### Search behaviour

- A text query long enough to tokenise uses the index. A shorter one falls back
  to a **bounded** scan that decrypts and substring-matches, so short queries
  still work without an unbounded table walk.
- Typed tokens narrow by account, category, amount, and date bounds. The same
  filters are available as controls, so the tokens are a shortcut rather than a
  requirement.
- Results are paginated by cursor and show a highlighted snippet of the match.
- Zero results with a long enough query offer a single spelling suggestion.
- The summary strip shows totals for the matched set, so a search doubles as an
  ad-hoc report.

Highlighting is produced with sentinel markers that are escaped before becoming
markup, so a merchant name containing markup characters cannot inject anything.

### Reindexing is a supported operation

A reindex command clears and rebuilds the index in chunks and **exits non-zero
on a count mismatch**, so a partial rebuild is a failure rather than a quiet
success. The health check surfaces index problems.

### Under at-rest encryption

The index body is **plaintext**, written by decrypting the encrypted source
columns first. This is a knowingly-accepted disclosed shadow of the encrypted
data, recorded in
[ADR-0018](../../../00-overview/decisions/0018-amounts-plaintext-at-rest.md).
There is no way to have both a working full-text index and opaque stored text
without an encrypted-search design, which is not in scope.

### The palette

The keyboard palette ([G6](../g-ux/g6-keyboard.md)) is backed by the same search
service, returning transaction matches and entity matches in separate sections,
with token autocompletion and recent searches.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| A query too short to tokenise | Bounded decrypt-and-scan fallback. |
| Zero results | A single spelling suggestion, where the query is long enough to make one meaningful. |
| A merchant name containing markup characters | Escaped before highlighting; no injection. |
| An index write failure during import | The import chunk rolls back. Loud, not silent. |
| A reindex that ends with a count mismatch | Non-zero exit; treated as a failure. |
| An amount query | Matches against the stored minor-unit amounts directly, never a second money representation. |
| A tax note edited | The index updates in the same write. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **B9-R1** | The index MUST cover the counterparty name as stored, the description, and the tax note. It MUST NOT carry the alias-resolved display name (B4-R15), which has no write on the transaction to key a refresh to. |
| **B9-R18** | Where a stored name and its resolved display name differ, the search surface MUST say that matching is against the statement's own text, so a reader who renamed a merchant is not told the transactions do not exist. |
| **B9-R2** | The index MUST be updated synchronously in the same transaction as the write that caused it. |
| **B9-R3** | An index write failure MUST roll back the causing write; it MUST NOT be swallowed. |
| **B9-R4** | Indexed fields MUST be separated by a token the tokeniser cannot index, so matches cannot cross field boundaries. |
| **B9-R5** | The index writer MUST verify that the caller-supplied user owns the row being indexed. |
| **B9-R6** | A query too short to tokenise MUST fall back to a bounded scan, never an unbounded table walk. |
| **B9-R7** | Typed tokens for account, category, amount, and date bounds MUST be supported, and the same filters MUST also be available as controls. |
| **B9-R8** | Results MUST be cursor-paginated and MUST show a highlighted snippet. |
| **B9-R9** | Highlight markers MUST be escaped before becoming markup. |
| **B9-R10** | A zero-result query of sufficient length MUST offer one spelling suggestion. |
| **B9-R11** | The result summary MUST show totals for the matched set. |
| **B9-R12** | A reindex command MUST rebuild in chunks and MUST exit non-zero on a count mismatch. |
| **B9-R13** | The health check MUST surface index problems. |
| **B9-R14** | The index body MUST be plaintext, written by decrypting encrypted source columns, and this disclosure MUST be documented. |
| **B9-R15** | Amount matching MUST read the stored minor-unit amounts directly. |
| **B9-R16** | The command palette MUST be backed by the same search service and MUST separate transaction and entity results. |
| **B9-R17** | Every search MUST be scoped to the requesting user. |

## Related

- [G6 Keyboard and command palette](../g-ux/g6-keyboard.md)
- [ADR-0018](../../../00-overview/decisions/0018-amounts-plaintext-at-rest.md) — the disclosed plaintext shadow
- [B1 Transactions](b1-transactions.md) · [D4 Tax tagging](../d-money/d4-tax.md)
- [F5 Developer mode](../f-platform/f5-dev-console.md) — the health probe
