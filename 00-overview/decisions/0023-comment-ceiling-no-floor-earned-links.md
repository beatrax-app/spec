# ADR-0023: Comment blocks have a ceiling and no floor; documentation links are earned

**Status:** Accepted
**Date:** 2026-08-20
**Supersedes:** two parts of [ADR-0011](0011-code-comment-policy.md) — M1's
single-line floor, and the expectation that a class carries a documentation link
in place of a prose summary. Its remaining mechanical rules, its judgment rules,
and the position all of them serve stand unchanged.

## Context

ADR-0011 is right about the thing it exists for. Code should be readable on its
own, prose restating the next line is noise, and architecture rots when it is
written inline instead of linked. None of that is in question here.

Two of the rules it settled have now run for a month across roughly 5 300 backend
files, and both are producing the opposite of what they were written for. They
fail the same way: **a limit was written with a floor attached, and an exception
was written as an expectation.** Each turned a permission into an obligation, and
the obligation manufactures precisely the noise the policy exists to remove.

### The floor made the noise it was written to prevent

M1 forbade a lone single-line comment — an informative `//` had to be part of a
contiguous block of two to four lines. The ceiling is sound; four lines is about
where prose stops belonging beside the code. The floor never was.

A thought worth one line had two outcomes under M1: delete it, or pad it to two.
Deleting is right where there was no *why* to begin with, and that case was
already covered by J1 and J2, which bind anyway. Where the *why* was real, the
only mechanically compliant move left was to say it in more words than it needed.
The rule made padding the cheapest way to pass, inside a policy whose whole
purpose is to remove padding.

Measured on the product's default branch, using the same tokeniser and the same
block detection the enforcing test uses, across 5 317 in-scope files:

| Inline `//` block | Count | Share |
|-------------------|-------|-------|
| One line | 0 | — |
| Two lines | 1 270 | 27.4% |
| Three lines | 1 580 | 34.1% |
| Four lines | 1 786 | 38.5% |
| Over four | 0 | — |

4 636 blocks, and not one is a single line. The rule demanded that, so on its own
it proves nothing. The shape is the evidence: the distribution **rises** towards
the cap rather than falling away from it. A ceiling produces the opposite curve —
most comments short, a few pressing against the limit. "Two to four" was read as
a target to hit rather than a bound not to cross, and that reading is a fair one,
because a rule with a floor and a ceiling is a range, and a range is a target.

### The per-class link says what the file path already said

M4 held that a class's purpose is carried by its name plus a documentation link,
and J4 asked for a link wherever a class has a documented home. Read together
they instruct a contributor to put a link on every class. That is what happened.

| Measured across the same 5 317 files | |
|--------------------------------------|--|
| `@link` tags | 1 039 |
| Files carrying at least one | 1 003 |
| Distinct targets, once relative depth is normalised | 57 |
| Pointing at some module's `architecture.md` | 971 (93%) |
| Pointing at one file, the sync module's architecture page | 116 |
| Pointing at a section rather than a whole page | 57 |

A thousand tags resolving to 57 destinations is not a documentation index. A
class under a sync module directory that links to the sync module's architecture
page tells the reader what the file's own path told them before they opened it.
The reader who wanted that page could already find it; the reader who did not is
made to step over the line anyway, in every file.

The 116 is the sharpest version of it. One page is cited by 116 classes, so
following the link from any of them lands on a document about the module rather
than about the class — and a reader who has followed it once has no way to tell
that the other 115 occurrences lead to the same place.

### What ADR-0011 predicted, and what actually happened

ADR-0011's revisit condition was that the mechanical rules would throw enough
false positives that contributors would reach for the directive allow-list rather
than restructure code. That is not what happened. Contributors complied, and the
compliance is the damage: 1 270 blocks sitting on the floor and 1 039 links
pointing at 57 pages are what full compliance looks like.

A rule that is obeyed and still harmful does not announce itself the way an
evaded one does. That is why this took a month and a count to see, and it is the
part worth carrying forward: the next mechanical rule should be checked against
what compliance produces, not only against what evasion would.

## Decision

**An inline comment block has a ceiling and no floor.**

M1 is deleted. M2 keeps the cap it always carried and loses its floor clause: a
contiguous informative `//` block is **at most four lines**. One line is a valid
comment where one line is what the thought is worth. Anything needing more than
four still belongs in documentation, linked.

**A documentation link is written where it is worth following.**

A link points at something the reader could not have guessed — a specific page,
or a section within one. It is not expected on a class, and a class is complete
without one: its name and its position in the tree are its description. Where the
material is too involved to sit in four lines, it earns its own documentation
page, and the link points at that.

**M6 is unchanged, and is what makes this safe.** Fewer links, each still
verified: a link that is present MUST resolve to a real file, and a moved page
still breaks the build.

Numbers are not reassigned. M1's number stays vacant, because the enforcing test
names its cases by these numbers and a vacated number that acquires new text
resolves silently to a rule it was never written against. The gap means what a
gap always means here: look in git.

## Alternatives considered

| Option | Why it lost |
|--------|-------------|
| **Keep the floor; catch padding in review** | The mechanical layer exists so that shape does not depend on reviewer vigilance. A floor is machine-checkable in the wrong direction: it can force a second line, and nothing can check that the second line was worth writing. |
| **Rewrite M1 in place instead of deleting it** | The enforcing test names its cases by these numbers, and so does this record. A reused number resolves to a rule it was never written against. A gap is visible; a wrong match is not. |
| **Drop `@link` entirely and delete M6 with it** | The link was never the problem; the expectation was. Where a target is specific, the link is the most useful line in the file — and M6 is what keeps the survivors honest. |
| **Keep the per-class link and write a real page per class** | A thousand pages nobody would maintain, to treat a symptom. It also re-creates inline class description one directory away, which is what ADR-0011 moved out of the code in the first place. |
| **Keep the per-class link, but mechanically forbid a generic target** | "Specific enough" is a judgment, and making it mechanical is exactly how both rules under revision acquired their floors. It belongs in the judgment layer, and that is where it now sits. |

## Consequences

### Positive

- **A one-line comment is writable again.** The shortest honest form of a *why*
  is available, which is the form most of them have.
- **A link now carries information.** A reader who sees one learns something from
  it, so links stop being scenery and start being signal.
- **The documentation dependency narrows.** ADR-0011 named the deepened reliance
  on documentation being current as a cost of moving class purpose out of the
  code. Dropping the per-class expectation reduces that reliance to the pages
  something actually points at.

### Negative

- **The tree still carries the old shape.** Nothing here removes 1 270
  floor-padded blocks or 971 generic links. The policy stops requiring them;
  correcting them is ordinary work in the product repository, read per file as
  the original sweep was. Until that happens the source shows a convention this
  specification no longer asks for.
- **The one uniform thread from a class to its module's documentation goes
  away.** It was near-worthless per instance, but it was uniform, and uniformity
  is a discovery aid. Nothing replaces it: the module directory and the
  documentation tree are the index.
- **"Worth following" is a judgment**, and judgments drift. The failure mode is a
  tree with no links at all, which the revisit condition below watches for.

### Neutral

- M2's cap, M3, M5 and M6 are untouched. M4's tag-only assertion — what the test
  actually checks — is untouched; only its trailing clause naming a per-class
  link is removed, because that clause was the expectation, not the rule.
- Every judgment rule but J4 stands as written.
- The directive allow-list is unaffected.

## Revisit if

- Inline blocks drift back towards four lines, which would say the cap is being
  read as a target the way the range was.
- Documentation pages start going unreferenced from code entirely, which would
  say some structural link belongs after all.

## Related

- [ADR-0011](0011-code-comment-policy.md) — superseded in part; its remaining
  rules, and the position they serve, stand
- [40-quality/code-comments.md](../../40-quality/code-comments.md) — the
  convention itself, carrying these changes
- [ADR-0001](0001-modular-architecture.md) — architecture in documentation, the
  position both records serve
- [50-governance/ai-contributors.md](../../50-governance/ai-contributors.md) —
  the judgment rules bind AI-assisted contributions identically
