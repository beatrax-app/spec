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

## Conformance target

**The target is WCAG 2.2 Level AA. It is stated, and it does not gate a
release.**

The two halves of that are separate decisions and both were taken deliberately.

Naming AA is honest rather than aspirational: the requirements above already
carry most of it, and the contrast half was measured and closed — every
foreground/background pair in the palette was sampled through a canvas rather
than pattern-matched out of the stylesheet, and 664 failures against the AA
ratio were taken to zero in both themes. A regex over colour utilities cannot
read `oklch()`, and a light-only fix breaks dark mode; the measurement had to
be done on rendered colour, and it was.

Not gating a release is the honest half of the same statement. **No automated
audit runs in the pipeline**, so AA is a target the product is built to, not a
level any build has been certified against. Calling it a gate would mean a tag
could claim conformance that nothing measured — the failure this page exists to
avoid. Requirements G3-R1 through G3-R11 are individually enforced, several of
them by architecture test; AA is the standard they are chosen against.

Adding a pipeline audit and promoting AA to a release gate is a live option and
would be the natural next step. It is not a precondition for v2.0.

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **G3-R1** | Light and dark themes MUST both be fully supported on every themed surface. |
| **G3-R2** | Every light-mode colour utility on a themed surface MUST carry a dark companion, enforced by architecture test. |
| **G3-R3** | The theme MUST follow the operating system where reported, with an explicit user override. |
| **G3-R4** | Triage queues, the categorisation inbox, and the command palette MUST be fully operable from the keyboard. |
| **G3-R5** | Global shortcut handlers MUST NOT fire while focus is in a text input, text area, or editable region ([G6-R11](g6-keyboard.md)). |
| **G3-R6** | Status, direction, and severity MUST carry a non-colour signal in addition to colour. |
| **G3-R7** | Amounts MUST be formatted for the user's locale, including separators and symbol position. |
| **G3-R8** | Amount entry MUST accept both decimal-separator conventions. |
| **G3-R9** | Every authenticated surface MUST be legible and operable at phone width. |
| **G3-R10** | Wide content MUST scroll inside its own container; the page body MUST NOT scroll horizontally. |
| **G3-R11** | Animation MUST be restrained and MUST NOT be required to understand a surface. |
| **G3-R12** | A conformance target MUST be chosen and stated. It is WCAG 2.2 Level AA, and it MUST be stated as a target the product is built to rather than a level a build has been certified against, for as long as no audit runs in the pipeline ([Conformance target](#conformance-target)). |

## Related

- [G4 Responsive and installable PWA](g4-pwa.md) · [G6 Keyboard and command palette](g6-keyboard.md)
- [60-brand/accessibility.md](../../../60-brand/accessibility.md) — the visual side of the same contract
- [40-quality/testing-strategy.md](../../../40-quality/testing-strategy.md)
