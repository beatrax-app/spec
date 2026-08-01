# G7 — Interface localisation and language selection

**Status:** Accepted · **Area:** G — Cross-cutting UX

> **Forthcoming.** This feature is specified ahead of its implementation, to
> unblock the app-side work that introduces it. Nothing here ships in `v1.3.0`;
> every requirement below is therefore marked *(Open)* until the behaviour it
> describes lands. This is the same discipline [G5](g5-plain-language.md) applies
> to deferred behaviour — a specification may run ahead of the product, but it
> must say so plainly rather than describe an interface that does not yet exist.

---

## Purpose

The interface has always been English, and only English. The words the product
chooses are load-bearing — the whole of [G5](g5-plain-language.md) is about
saying the true thing in the user's own vocabulary — and that argument does not
hold if the user does not read English.

This feature makes the interface translatable and lets a household choose the
language it runs in. It starts with English and Dutch, the two the product's own
statement vocabulary already spans, and is built so a third costs a translation
rather than a rewrite.

It deliberately mirrors the existing theme preference
([F1](../f-platform/f1-desktop-shell.md)): a signal the environment can offer, a
per-user choice that overrides it, and a switch in Settings that sits in the same
family as Appearance.

## Behaviour

### Two languages to start, more without a rewrite

The interface ships in English (`en`) and Dutch (`nl`). English is the **source
locale**: it is the language keys are authored in, and the one every other locale
is measured against.

Adding a further language is a matter of registering its locale and supplying its
translations. The mechanism that detects, selects, and applies a language does
not change when a locale is added — nothing about switching is wired to the fact
that there happen to be two.

### Detection before choice

On a first visit, before the household has expressed any preference, the
interface picks its language from the environment: the browser or system
`Accept-Language` preference, resolved to the **best supported match**. A request
that prefers `nl` gets Dutch; one that prefers a language the product does not
carry falls through.

Where nothing in the request matches a supported locale, the interface uses
**English**. English is the floor, not an error state — an unmatched preference
is an ordinary outcome, not a failure to report.

This mirrors the theme signal exactly: the environment offers a preference, its
absence is itself a defined outcome, and neither is ever the last word.

### Choice beats detection

Language is a **per-user preference**, stored on the user record next to the
theme it mirrors ([data model](../../../20-architecture/data-model.md)). Once a
user has set it, that choice wins — on this session and every one after it,
regardless of what the environment reports. Detection applies only until a
preference exists; it never overrides one.

The preference persists the way every other user preference does. A user who
chose Dutch last month opens the application in Dutch, with no re-detection and
no drift back to the environment's language.

### The switch lives in Settings

The language switcher sits in Settings, in the **same family as Appearance** —
the surface that already owns the theme choice. It is an ordinary setting a user
can find where they would look for the theme, not a separate onboarding step or a
hidden flag. Changing it takes effect across the interface immediately, without
losing the user's place or data.

### Everything user-facing is translatable

Every string a user can read is translatable. No user-facing copy is pinned to a
single language in a way a locale cannot reach — the same completeness discipline
[G4](g4-pwa.md) applies to responsive layout, applied to language.

Where a key has no value in the active locale, the interface falls back to its
**English** value rather than showing a raw key, a blank, or a placeholder. A
partially translated locale therefore degrades to English in the gaps, never to
something broken — which is exactly the honesty [G5-R14](g5-plain-language.md)
requires: an untranslated string reads as English, not as a translated interface
that silently isn't.

### The active language is announced

The active locale is reflected in the document's language attribute, so a screen
reader announces content in the language it is actually written in
([G3](g3-accessibility.md)). A Dutch interface that a screen reader pronounces as
English is a defect, not a cosmetic one.

### It stays on the machine

Detection reads a request header the browser already sends and a preference the
user already stored; neither is sent anywhere. Language selection adds no
outbound call and no third-party translation service — consistent with the
privacy stance ([G1](g1-privacy.md)), translation is a local concern like every
other.

## States

The active locale for a request resolves in a fixed order, first match wins:

| Order | Source | When it applies |
|-------|--------|-----------------|
| 1 | The user's stored language preference | Whenever the user has set one. |
| 2 | The environment's `Accept-Language`, best supported match | First visit, before a preference exists, when the request names a supported locale. |
| 3 | English (`en`) | Whenever neither above yields a supported locale. |

Setting a preference moves a user permanently from rows 2–3 to row 1. There is no
transition back short of clearing the preference.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| `Accept-Language` prefers an unsupported language | Falls through to English; no error. |
| `Accept-Language` lists several languages | The best supported match is taken in the header's own priority order. |
| A supported locale with a region subtag (`nl-BE`) | Resolved to its base supported locale (`nl`). |
| A preference set, then the environment language changes | The preference still wins; detection does not re-run. |
| A key missing in the active locale | The English value is shown. |
| A key missing in English as well | A genuine defect — English coverage is the source locale's contract, not a fallback that may itself have holes. |
| Language changed mid-session | Applies immediately, without a reload that discards the user's place. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **G7-R1** | *(Open)* The interface MUST support English (`en`) and Dutch (`nl`), with English as the source and fallback locale. |
| **G7-R2** | *(Open)* Adding a further locale MUST require only its registration and its translations; the detect–select–apply mechanism MUST NOT change per locale. |
| **G7-R3** | *(Open)* On a first visit, before any preference exists, the active locale MUST be the best supported match against the request's `Accept-Language` preference. |
| **G7-R4** | *(Open)* Where `Accept-Language` yields no supported locale, the active locale MUST default to English, and this MUST NOT be treated as an error. |
| **G7-R5** | *(Open)* A language preference MUST be stored per user on the user record, alongside the existing theme preference. |
| **G7-R6** | *(Open)* Once a user language preference is set, it MUST take precedence over detection on every subsequent request. |
| **G7-R7** | *(Open)* Detection MUST apply only while no user preference exists; it MUST NOT override a stored preference. |
| **G7-R8** | *(Open)* The language preference MUST persist across sessions without re-detection. |
| **G7-R9** | *(Open)* A language switcher MUST live in Settings, in the same family as the Appearance/theme setting. |
| **G7-R10** | *(Open)* Changing the language MUST take effect across the interface immediately, without discarding the user's place or data. |
| **G7-R11** | *(Open)* Every user-facing string MUST be translatable; no user-facing copy may be pinned to a single language beyond a locale's reach. |
| **G7-R12** | *(Open)* A key absent in the active locale MUST fall back to its English value, never to a raw key, a blank, or a placeholder. |
| **G7-R13** | *(Open)* The active locale MUST be reflected in the document's language attribute for assistive technology. |
| **G7-R14** | *(Open)* Language detection and selection MUST NOT add an outbound call or send the user's locale off the machine. |

## Related

- [G5 Plain language and in-product help](g5-plain-language.md) — the voice these translations carry, and the honesty rule the English fallback satisfies
- [G3 Accessibility](g3-accessibility.md) — why the active locale must be announced
- [G1 Privacy stance](g1-privacy.md) — why selection stays on the machine
- [F1 Desktop shell](../f-platform/f1-desktop-shell.md) — the theme preference this mirrors
- [20-architecture/data-model.md](../../../20-architecture/data-model.md) — where the per-user preference lives
- [20-architecture/platform-matrix.md](../../../20-architecture/platform-matrix.md) — the language signal per platform
