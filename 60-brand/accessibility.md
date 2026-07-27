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

Text and meaningful non-text elements meet a contrast ratio sufficient for
sustained reading of numeric content in both themes. Amounts and dates are read
carefully, repeatedly, often on a phone in poor light — the bar is legibility for
that, not a minimum that technically passes.

**No conformance level is currently named as a gate**; see the open question
below.

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

## Open question

**No formal conformance target has been set, and there is no automated
accessibility audit in the pipeline.**

What is actually in force is the theme-companion architecture test, the
non-colour-carrier rule, the keyboard requirements, and the locale formatting.
That is a real set of practices — but it is not a standard, and this page will
not claim one it is not measuring.

Choosing a target, and deciding whether it gates a release, is undecided.

## Related

- [G3 Accessibility](../10-functional/features/g-ux/g3-accessibility.md) · [G4 Responsive PWA](../10-functional/features/g-ux/g4-pwa.md) · [G6 Keyboard](../10-functional/features/g-ux/g6-keyboard.md)
- [brand-rules.md](brand-rules.md)
