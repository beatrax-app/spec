# G6 — Keyboard and command palette

**Status:** Accepted · **Area:** G — Cross-cutting UX

---

## Purpose

Categorising forty transactions, or triaging thirty unknown counterparties, is a
high-repetition task. Doing it with a pointer is the difference between five
minutes and twenty. The keyboard surface is what makes the monthly routine
tolerable.

## Behaviour

### The command palette

One shortcut from anywhere opens a palette that filters across navigation
destinations, actions, and — for developers only — development commands.

It is **backed by the same search service** the transactions surface uses
([B9](../b-ledger/b9-search.md)), so a search from the palette finds the same
things a search from the list does, in separate sections for transactions and
entities.

Typed filter tokens autocomplete. Recent searches are remembered per user, in a
bounded list with a bounded lifetime.

Development rows are filtered out **server-side, as the data is produced** —
never merely hidden in the client. A non-developer's palette payload does not
contain them at all.

### Triage is keyboard-complete

The counterparty triage queue is operable end to end from the keyboard: accept,
reject, skip and requeue, advance, and close. The categorisation inbox assigns a
category with a number key, moves with arrow keys, and commits a batch.

Skip re-queues at the end rather than dropping the item, so a pass over the
queue is a genuine pass.

### Shortcuts never fight text entry

A shortcut handler **must not fire while focus is inside a text input, a text
area, or an editable region**. Typing a merchant name that happens to contain a
shortcut letter must never trigger the shortcut.

This is the single most important rule here, because getting it wrong makes the
whole surface hostile.

### Discoverability

Shortcuts are shown where they apply, on the surface that offers them, rather
than only in a help page. A user who has never read the documentation should
still discover that a number key assigns a category.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| Typing in a field | Shortcuts do not fire. |
| Skipping an item in triage | Re-queued at the end. |
| A non-developer opening the palette | No development rows in the payload. |
| A palette search with no results | The same no-results treatment as the search surface. |
| A recent search list growing | Bounded in count and lifetime. |
| A shortcut on a surface that does not offer it | Nothing happens; no error. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **G6-R1** | A single shortcut MUST open a command palette from any authenticated surface. |
| **G6-R2** | The palette MUST filter across navigation destinations and actions. |
| **G6-R3** | The palette MUST be backed by the same search service as the transactions surface, with separate transaction and entity sections. |
| **G6-R4** | Typed filter tokens MUST autocomplete in the palette. |
| **G6-R5** | Recent searches MUST be remembered per user, bounded in count and lifetime. |
| **G6-R6** | Development rows MUST be filtered server-side as the payload is produced, never only hidden in the client. |
| **G6-R7** | Only the safe tier of development commands may appear in the palette at all. |
| **G6-R8** | The counterparty triage queue MUST be operable end to end from the keyboard. |
| **G6-R9** | The categorisation inbox MUST support assigning a category by number key, moving by arrow keys, and committing a batch. |
| **G6-R10** | Skipping an item MUST re-queue it at the end rather than dropping it. |
| **G6-R11** | Shortcut handlers MUST NOT fire while focus is in a text input, text area, or editable region. |
| **G6-R12** | Available shortcuts MUST be discoverable on the surface that offers them. |

## Related

- [B9 Full-text search](../b-ledger/b9-search.md) — the backing service
- [B2 Categorisation](../b-ledger/b2-categorisation.md) · [B4 Counterparties](../b-ledger/b4-counterparties.md) — the triage surfaces
- [F5 Developer mode](../f-platform/f5-dev-console.md) — the gated rows
- [G3 Accessibility](g3-accessibility.md)
