# Contract — design tokens

**Status:** Accepted

The product and the website are two surfaces of one thing. This contract is what
stops them drifting into looking like two products.

## The contract

The brand's visual primitives — colour, type scale, spacing, radius, elevation,
and motion — are defined **once** and consumed by both surfaces. The definition
lives with the brand rules ([60-brand](../../60-brand/)) and the values are
carried in the product repository's own brand resources.

Neither surface may introduce a primitive of its own. A new colour, a new type
step, or a new spacing value is a change to the shared set, reviewed as such —
not a local addition that quietly becomes a second system.

## What each surface owns

| Surface | Owns | Does not own |
|---------|------|--------------|
| **Product** | Application layout, component composition, interaction states, the responsive behaviour in [G4](../../10-functional/features/g-ux/g4-pwa.md) | Brand primitives, the marks, the voice |
| **Website** | Marketing layout and page composition | Brand primitives, the marks, the voice |
| **This spec** | The rules both obey | The values themselves |

## Theme is part of the contract

Every primitive has a light value and a dark value. A surface that adopts a
light-mode primitive without its dark counterpart is incomplete, and in the
product that is enforced mechanically by architecture test
([G3](../../10-functional/features/g-ux/g3-accessibility.md)).

The website has no equivalent mechanical check today, and that asymmetry is
stated rather than assumed away.

## Screenshots are shared assets

Product screenshots used on the website come from the product repository. A
release that changes a surface materially should refresh them rather than
leaving the site showing a version that no longer exists.

**There is currently no automation for this** — it is a release-checklist item
([70-operations/releasing.md](../../70-operations/releasing.md)) rather than a
gate, and calling it a gate would overstate it.

## What is deliberately not shared

**Component code.** The product is server-rendered with its own component layer;
the website is a static site. Sharing components across that boundary would
couple two things with different lifecycles for the sake of a resemblance that
tokens already deliver.

## Open question

**There is no versioned token package.** Tokens are shared by convention and by
this contract, not by a dependency the build resolves. That is adequate at a
four-repository, one-maintainer scale, and it would not be at a larger one.

Whether to extract a package is undecided, and this page records the current
arrangement rather than describing an aspiration.

## Related

- [60-brand/](../../60-brand/) — the rules and the values
- [30-repos/website.md](../../30-repos/website.md)
- [G3 Accessibility](../../10-functional/features/g-ux/g3-accessibility.md) · [G4 Responsive PWA](../../10-functional/features/g-ux/g4-pwa.md)
