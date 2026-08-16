# Brand rules

**Status:** Accepted

## The name

**Beatrax**, capitalised, always — a proper noun written with a capital B
everywhere, including mid-sentence ([DES-R1](README.md#the-des-r-namespace)).

It is named after the maintainer's mother, Bea. That is worth knowing because it
explains the product's register: it was built for someone specific, and it reads
that way.

The publisher is **NightWorks.io**.

### Not the name

`diederik` appears as an internal codename in some historical artefacts and
command names in the product repository. It is not the product's name and should
not appear in anything user-facing
([00-overview/glossary.md](../00-overview/glossary.md#deliberately-not-used)).

## Voice

British-leaning English. Calm and precise
([DES-R6](README.md#the-des-r-namespace)).

| Do | Do not |
|----|--------|
| State what happened and what to do next | State what happened and stop |
| Use the user's vocabulary | Use implementation vocabulary |
| Say the uncomfortable thing plainly | Soften a limitation into vagueness |
| Let a good number speak for itself | Congratulate the user for having money |
| Write full sentences in explanatory copy | Write telegraphic fragments to seem efficient |

**No exclamation marks in system copy. No manufactured urgency. No cheerful
euphemism for a failure** ([DES-R7](README.md#the-des-r-namespace)).

One voice across the product, the website, and this specification. A user who
reads the site and then opens the application should not feel handed off between
two teams.

### Honesty is a brand rule, not only a governance one

Copy never claims a protection the implementation does not provide
([DES-R8](README.md#the-des-r-namespace),
[G5](../10-functional/features/g-ux/g5-plain-language.md)).

For a privacy product this is the whole brand. A single overstatement that a
knowledgeable reader can disprove costs more than every accurate claim earns.

## Visual character

**Calm and content-first.** The interface is mostly tables, forms, and a few
charts, and it should look like a well-set document rather than a control panel.

| Principle | In practice |
|-----------|-------------|
| Content over chrome | Navigation recedes; the numbers do not |
| Restraint in colour | Colour marks meaning, not decoration |
| Quiet charts | Sober defaults, no gradients for their own sake |
| Restrained motion | Transitions orient; nothing performs ([DES-R9](README.md#the-des-r-namespace)) |
| Density that suits the surface | Dense where scanning matters; airy where deciding matters |

## Primitives

Colour, type scale, spacing, radius, elevation, and motion are defined **once**
and consumed by every surface
([DES-R2](README.md#the-des-r-namespace),
[20-architecture/contracts/design-tokens.md](../20-architecture/contracts/design-tokens.md)).

A new primitive is a change to the shared set, reviewed as such — not a local
addition that quietly becomes a second system.

Every primitive has a light **and** a dark value
([DES-R3](README.md#the-des-r-namespace)). Neither theme is the real one with a
filter over it.

## Money on screen

Formatted for the user's locale — separators and symbol position both
([DES-R10](README.md#the-des-r-namespace)). A user who reads a comma as a
decimal separator sees one.

Direction carries a sign, not only a colour. Where a figure is converted, the
rate, its source, and its as-of date are available on it
([B10](../10-functional/features/b-ledger/b10-multi-currency.md)).

## Screenshots

Public screenshots come from the product repository and show a version that
exists ([DES-R12](README.md#the-des-r-namespace)). A release that materially
changes a surface should refresh them.

**This is a release-checklist item, not an automated gate**, and calling it a
gate would overstate it
([20-architecture/contracts/design-tokens.md](../20-architecture/contracts/design-tokens.md#screenshots-are-shared-assets)).

## Related

- [surface-mapping.md](surface-mapping.md) · [accessibility.md](accessibility.md) · [trademark.md](trademark.md)
- [G5 Plain language](../10-functional/features/g-ux/g5-plain-language.md)
