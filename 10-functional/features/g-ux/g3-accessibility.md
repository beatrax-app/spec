# G3 — Accessibility

**Status:** Accepted · **Area:** G — Cross-cutting UX

---

## Purpose

A finance dashboard is used by people managing money late at night, on a phone,
in a hurry, with whatever eyesight and dexterity they have. Accessibility here
is not a compliance exercise — it is the difference between a tool someone can
use every day and one they can use when conditions are good.

## Behaviour

### Both themes are first-class

Light and dark are equal, not one with a filter over it. Every themed surface
carries a dark companion for every light-mode colour utility, and **this is
enforced by architecture test** — a view that sets a light background without
its dark counterpart fails the build.

That mechanical check exists because theme regressions are invisible to whoever
is not using the other theme, which is to say, invisible.

The theme follows the operating system where the shell reports it, with an
explicit user override ([F1](../f-platform/f1-desktop-shell.md)).

### Keyboard-first where it matters

The triage queues, the categorisation inbox, and the command palette are fully
operable from the keyboard ([G6](g6-keyboard.md)) — those are the
high-repetition surfaces where reaching for a pointer every row is the
difference between a five-minute task and a twenty-minute one.

Shortcut handlers **must not fire while a text field has focus**, so typing a
merchant name never triggers an action.

### Colour is never the only signal

Status, direction, and severity all carry a shape, a label, or an icon as well
as a colour. Counterparty types carry a labelled chip rather than a colour
alone. Alert severity carries text. Money direction carries a sign, not just
red and green.

### Numbers are legible

Amounts are formatted for the user's locale — the decimal separator, the grouping
separator, and the symbol position all follow it rather than a hard-coded
convention. A user who reads a comma as a decimal separator sees one.

Amount **entry** is equally forgiving, accepting both conventions
([A7](../a-ingestion/a7-cash-book.md)).

### Phone surfaces are usable, not merely rendered

Every authenticated surface is legible and operable at phone width
([G4](g4-pwa.md)). Dense tables become card lists; wide power surfaces scroll
horizontally inside their own container rather than making the page scroll;
modals become bottom sheets.

### Motion and density are calm

The product's visual language is calm by intent
([60-brand](../../../60-brand/)). Charts have quiet defaults, animation is
restrained, and nothing moves that does not need to.

## Open question

**No formal conformance target has been set.** The product repository's own
documentation records accessibility improvements as in scope for contributions
and enforces the theme-companion rule mechanically, but it does not name a
conformance level, and there is no automated audit in the pipeline.

Setting one — and deciding whether it gates a release — is undecided. This page
records the practices that are actually in force rather than claiming a standard
that is not being measured.

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **G3-R1** | Light and dark themes MUST both be fully supported on every themed surface. |
| **G3-R2** | Every light-mode colour utility on a themed surface MUST carry a dark companion, enforced by architecture test. |
| **G3-R3** | The theme MUST follow the operating system where reported, with an explicit user override. |
| **G3-R4** | Triage queues, the categorisation inbox, and the command palette MUST be fully operable from the keyboard. |
| **G3-R5** | Shortcut handlers MUST NOT fire while a text input has focus. |
| **G3-R6** | Status, direction, and severity MUST carry a non-colour signal in addition to colour. |
| **G3-R7** | Amounts MUST be formatted for the user's locale, including separators and symbol position. |
| **G3-R8** | Amount entry MUST accept both decimal-separator conventions. |
| **G3-R9** | Every authenticated surface MUST be legible and operable at phone width. |
| **G3-R10** | Wide content MUST scroll inside its own container; the page body MUST NOT scroll horizontally. |
| **G3-R11** | Animation MUST be restrained and MUST NOT be required to understand a surface. |
| **G3-R12** | *(Open)* A conformance target MUST be chosen and stated. Not yet decided — see [Open question](#open-question). |

## Related

- [G4 Responsive and installable PWA](g4-pwa.md) · [G6 Keyboard and command palette](g6-keyboard.md)
- [60-brand/accessibility.md](../../../60-brand/accessibility.md) — the visual side of the same contract
- [40-quality/testing-strategy.md](../../../40-quality/testing-strategy.md)
