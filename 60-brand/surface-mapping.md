# Surface mapping

**Status:** Accepted

The identity is one thing. Its expression differs by surface, and this page says
how.

## The surfaces

| Surface | What it is | Owns |
|---------|-----------|------|
| **Desktop application** | The primary surface | Application layout, component composition, interaction states |
| **Phone (installed)** | The same interface at phone width, in a native shell | Its responsive patterns ([G4](../10-functional/features/g-ux/g4-pwa.md)) |
| **Website** | The public site | Marketing layout and page composition ([30-repos/website.md](../30-repos/website.md)) |
| **Documentation site** | This specification, published | Nothing brand-specific — it inherits |
| **Installers and store listings** | The first thing a user sees | Icon, name, and description |
| **Release notes** | Generated from the commit history | The voice, applied to change |

None of them own primitives ([DES-R2](README.md#the-des-r-namespace)).

## Desktop and phone

The **same** interface, not two designs. The phone applies documented responsive
patterns rather than a reduced feature set
([G4](../10-functional/features/g-ux/g4-pwa.md)):

| Desktop | Phone |
|---------|-------|
| Dense tables | Card lists |
| Side navigation | Drawer and top bar |
| Modals | Bottom sheets |
| Wide power surfaces | The same, scrolling inside their own container |
| Paged lists | Infinite scroll, capped |

**Every** authenticated surface works at phone width. Not a subset.

## Website

The one surface where overstating is tempting, and the one where it costs most.
Its obligations are requirements rather than guidance
([30-repos/website.md](../30-repos/website.md)):

- Source-available, **not** open source.
- Local-first, with the outbound surface **named** rather than merely claimed.
- Sync described accurately, including what a relay can observe.
- Installers described as unsigned, with the reason.
- No analytics, no tracking, no third-party embeds.

## Documentation site

Built from this repository. It inherits the voice and needs no separate identity
— it is a specification, and looking like one is correct.

## Installers and store listings

Icon, name, and one-line description. The description says what the product is
for a household, not what it is technically.

Store listings are **not yet scoped**
([00-overview/roadmap.md](../00-overview/roadmap.md#open-questions)); when they
are, they inherit every rule on this page.

## Release notes

Generated from the commit history
([70-operations/releasing.md](../70-operations/releasing.md)), which means the
commit subject is written **in the user's language**, not the implementer's.

"Envelope carryover fold now anchored at activation" is a commit message.
"Money you set aside now rolls forward correctly from the month you switched
envelopes on" is a release note.

A breaking change gets **prominence**, not a line
([J4](../10-functional/journeys/j4-tax-year-end.md#a-note-on-the-v20-upgrade)).

## The seam that fails first

Screenshots. The site shows a version; the product moves on; nobody notices
because both look fine in isolation.

That is why refreshing them is on the release checklist
([brand-rules.md](brand-rules.md#screenshots)) — and why it being a checklist
item rather than a gate is stated rather than glossed.

## Related

- [brand-rules.md](brand-rules.md) · [accessibility.md](accessibility.md)
- [20-architecture/contracts/design-tokens.md](../20-architecture/contracts/design-tokens.md)
- [20-architecture/platform-matrix.md](../20-architecture/platform-matrix.md)
