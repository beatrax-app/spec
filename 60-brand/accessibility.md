# Accessibility — the visual contract

**Status:** Accepted

The checkable visual constraints. The behavioural half is
[G3](../10-functional/features/g-ux/g3-accessibility.md).

## Both themes are first-class

Light and dark are equal ([DES-R3](README.md#the-des-r-namespace)). Every
primitive has both values, and **every themed surface carries a dark companion
for every light-mode colour utility** — enforced by architecture test in the
product ([DES-R4](README.md#the-des-r-namespace)).

That mechanical check exists because theme regressions are invisible to whoever
is not using the other theme, which is to say invisible until a user reports a
white-on-white panel.

The theme follows the operating system where the shell reports it, with an
explicit user override. Outside the shell the browser's own preference is the
signal.

## Colour is never the only carrier

Status, direction, and severity each carry a label, a shape, or an icon as well
as a colour ([DES-R5](README.md#the-des-r-namespace)).

| Meaning | Non-colour carrier |
|---------|--------------------|
| Money direction | The sign, always |
| Counterparty type | A labelled chip |
| Alert severity | Text, and ordering |
| Reconciliation status | A labelled pill |
| Anomaly reasons | Reason chips, named |
| Sync status | Words, not a dot |

## Contrast

Text and meaningful non-text elements meet **WCAG 2.2 Level AA** in both themes.
Amounts and dates are read carefully, repeatedly, often on a phone in poor light,
so AA is the floor rather than the ambition — the bar is legibility for that, not
a minimum that technically passes.

This half was measured rather than asserted. Every foreground/background pair in
the palette was sampled through a canvas rather than pattern-matched out of the
stylesheet: a regex over colour utilities cannot read `oklch()`, and a fix
applied to light mode alone breaks dark mode. 664 failures against the AA ratio
were taken to zero across both themes.

## Numbers

Locale-formatted — separators and symbol position
([DES-R10](README.md#the-des-r-namespace)). Amount entry accepts both
conventions ([A7](../10-functional/features/a-ingestion/a7-cash-book.md)).

Tabular figures wherever amounts are stacked, so columns align on the decimal
rather than dancing.

## Motion

Restrained ([DES-R9](README.md#the-des-r-namespace)). Transitions orient the
user between states; nothing performs. Nothing is required to be seen in motion
to be understood.

## Focus and keyboard

Focus is always visible, in both themes. The high-repetition surfaces — the
triage queues, the categorisation inbox, the palette — are fully keyboard
operable, and shortcut handlers never fire while a text field has focus
([G6](../10-functional/features/g-ux/g6-keyboard.md)).

## Density

Dense where scanning matters — transaction lists, the budget grid. Airy where
deciding matters — the reconcile screen, the pairing ceremony, anything with a
confirmation.

Wide content scrolls inside its own container; the page never scrolls sideways
([G4](../10-functional/features/g-ux/g4-pwa.md)).

## Conformance target

**WCAG 2.2 Level AA, stated as the target, and not gating a release.** The
behavioural half of that decision, and the reasoning for both halves, is
[G3](../10-functional/features/g-ux/g3-accessibility.md#conformance-target); this
page carries the visual half.

What is in force here is checkable: the theme-companion architecture test, the
non-colour-carrier rule, tabular figures and locale formatting, visible focus in
both themes, and a contrast palette measured against the AA ratio rather than
eyeballed.

**No automated accessibility audit runs in the pipeline.** So AA is a standard
this page's constraints are chosen against, not a level any build has been
certified against, and this page states it that way. The distinction is the whole
point: a page claiming conformance nothing measures is the failure this one was
written to avoid ([DES-R8](README.md#the-des-r-namespace)). It is recorded as an
[accepted tension](../90-appendix/open-questions.md#a-conformance-level-is-named-that-nothing-measures)
rather than as a settled matter, because the pull between naming a standard and
measuring nothing is real and survives the decision.

## Related

- [G3 Accessibility](../10-functional/features/g-ux/g3-accessibility.md) · [G4 Responsive PWA](../10-functional/features/g-ux/g4-pwa.md) · [G6 Keyboard](../10-functional/features/g-ux/g6-keyboard.md)
- [brand-rules.md](brand-rules.md)
