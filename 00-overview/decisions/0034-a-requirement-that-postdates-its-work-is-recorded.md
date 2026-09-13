# ADR-0034: A requirement that postdates its work is recorded, not cited

**Status:** Accepted
**Date:** 2026-09-13

## Context

The canonical-spec rule says every change cites an identifier that already
exists here ([GOV-R2](../../50-governance/README.md#the-gov-r-namespace),
[GOV-R3](../../50-governance/README.md#the-gov-r-namespace)), and
[GOV-R4](../../50-governance/README.md#the-gov-r-namespace) orders a
behavioural change so that the identifier exists in time to be cited.

Eleven requirements locked into the [v2.0.0
manifest](../../70-operations/versions/2.0.0.toml) are cited by nothing in the
product repository, and the cause is the same in nine of them: the requirement
was written to *describe* work that had already merged, so no trailer on the
implementing commit could have named it. Two are measurable to the second —
`E2-R22`'s implementation merged at 20:31:49 and the requirement was minted at
21:02:33; `E5-R27`'s implementation merged twenty-six seconds *after* the
specification change that created it. `A5-R18` ran the same way by sixty-three
minutes. The remaining two are ordinary slips: the specification merged first,
correctly, and the trailer named a sibling identifier instead.

Three facts make this unfixable by the obvious routes.

**A later citation does not reach backwards.** `spec_check.py` runs per pull
request against that pull request's own text. A subsequent pull request naming
the identifier passes for itself and leaves the original exactly as uncited as
it was. The product repository recorded all eleven in one page and its author's
own verdict was that *"it records the id, it does not cite the work"*. That is
correct.

**Amending the merged commits was considered and rejected** by the owner:
published history is not traded for one word per commit.

**Four of the eleven were graded uncited for the shape of their documentation,
not for its absence.** `A3-R23`, `E5-R27`, `E6-R14` and `E6-R16` are named in a
pull-request body sentence rather than on a `Spec:` line. `spec_check.py` keeps
only identifiers standing on a line matching `^\s*Spec:`, so prose is invisible
to it — a guard keyed on a line format silently reclassifying *documented
differently* as *not documented*.

On a strict reading of the [definition of
done](../../40-quality/definition-of-done.md), `releasable` was unreachable for
v2.0 and would stay unreachable however much work was done, because the only
change that could satisfy the rule has already merged.

## Decision

**Three parts, taken together. None of them is the whole answer.**

1. **A record satisfies the citation box where a citation was impossible.**
   Where a requirement did not exist on this repository's default branch at the
   time the work it describes merged, a record in the implementing repository —
   naming the identifier, the seam that implements it, and the commit that
   merged it — ticks the definition of done's citation box for that requirement
   ([GOV-R26](../../50-governance/README.md#the-gov-r-namespace)).

   The record is not a citation and does not pretend to be one. What it buys is
   the one thing that was genuinely missing: an identifier appearing nowhere
   cannot be told apart from an identifier nobody implemented, and separating
   those two otherwise costs every future audit a hand re-derivation of all
   eleven seams. That cost is real — of the eleven derivations that prompted
   this, two came back different from the audit that had attributed them.

   It is bounded, and the bound is the point. A trailer that *could* have
   carried the identifier and did not is a missing trailer, and no record
   repairs it ([definition of
   done](../../40-quality/definition-of-done.md#when-the-requirement-postdates-the-work)).

2. **The ordering rule is restated about the requirement, not about the
   change.** A requirement exists on the default branch before the work it
   describes merges, so the implementing change can cite it
   ([GOV-R27](../../50-governance/README.md#the-gov-r-namespace)). GOV-R4
   ordered a *behavioural change*; a requirement written only to describe
   existing behaviour is not one, which is exactly the gap nine of the eleven
   walked through. The single legitimate way to arrive late is the founding
   one — this specification was written for a product that already existed —
   and that case is recorded under GOV-R26 rather than excused.

3. **The gate names what it read.** `spec_check.py` still accepts a citation
   only from a `Spec:` trailer, and now reports an identifier the text names
   anywhere else as *named but not cited*, on both the failing and the passing
   path ([GOV-R28](../../50-governance/README.md#the-gov-r-namespace)). It can
   no longer say "uncited" about an identifier written three lines above.

## Alternatives

| Alternative | Why it lost |
|-------------|-------------|
| **Hold the release until every requirement is cited by the change that implemented it** | Unreachable by construction. The changes in question have merged; nothing a future pull request does makes a past one cite anything. It is a rule that can only be satisfied by rewriting history, which is the next row. |
| **Amend the eleven merged commits to add the trailers** | Rejected by the owner, and rightly: it rewrites published history, invalidates every reference to those hashes, and buys one word per commit. It would also make the record *less* true — a trailer back-dated onto a commit written before the identifier existed asserts something that did not happen. |
| **Re-derive the eleven seams at every audit instead of writing them down** | This is the status quo, and it has a measured error rate: two of eleven attributions in the first derivation were wrong, both crediting the pull request that touched the seam last rather than the one that implemented the requirement. Paying that cost repeatedly, and getting a different answer each time, is worse than paying it once in public. |
| **Widen the gate to accept an identifier named in prose** | A sentence names an identifier without citing it. *"Unlike A3-R23"* and *"superseded by A3-R23"* would both pass, and the gate would be grading changes as cited on a reading no reviewer agreed to. The trailer is a deliberate, parseable act; that is its whole value. Reporting prose distinctly gets the information without spending the guarantee. |
| **Withdraw the eleven identifiers and mint new ones after the fact** | Forbidden ([GOV-R8](../../50-governance/README.md#the-gov-r-namespace), [GOV-R10](../../50-governance/README.md#the-gov-r-namespace)), and it would be a fabrication: the requirements are correct and the work is done. Renumbering to make a gate happy is the tail wagging the dog. |
| **Let the exception cover the slips too, and close all eleven** | It would close the release cleanly and it is exactly the abuse this record has to refuse. A trailer that could have named the identifier and did not is the case the citation rule exists for; an exception that swallows it is not an exception, it is a repeal. Two of the eleven stay open because of this, and that is the correct answer. |

## Consequences

### Positive

- The nine requirements that could never have been cited have a stated,
  bounded way to satisfy the definition of done, with the reason attached.
- The gap GOV-R4 left — a descriptive requirement is not a behavioural change
  — is closed rather than relied on not to recur.
- The gate stops misreporting *documented in the wrong shape* as *not
  documented*, and stops passing in silence when a squash trims a multi-id
  `Spec:` line down to one.
- An audit asking *"what implements this?"* gets an answer that was derived
  once, against the seam, rather than re-derived differently each time.

### Negative

- Two of the eleven — `A3-R23`, and the second half of `E6-R14` — are slips,
  not inversions, and this record deliberately does not close them. They need a
  later change on the same seam carrying the trailer, or a recorded override
  ([overrides.md](../../50-governance/overrides.md)). The release question they
  belong to is not settled here.
- GOV-R26 and GOV-R27 are both verified in review and by nothing else. The gate
  checks that a cited identifier exists, never when it came to exist. A rule
  enforced by vigilance decays, and these two now depend on it.
- "Satisfies the citation box" is a second route to a box that previously had
  one route. Every such route is a place a future contributor can stand while
  arguing, which is why the disqualifying cases are enumerated rather than
  implied.

### Neutral

- No merged commit changes. No version manifest changes, and no version's
  status moves; whether v2.0.0 becomes `releasable` depends on more than this.
- Consumer repositories change nothing about how they cite. The gate is
  stricter in what it says and identical in what it accepts.

## Revisit if

- Ordering becomes machine-checked — the [open
  question](../../90-appendix/open-questions.md) that would retire most of
  GOV-R27's reliance on review.
- A second batch of requirements arrives needing the GOV-R26 record. Once is
  history being caught up with; twice is GOV-R27 not working.
- The *named but not cited* warning turns out to fire on ordinary prose often
  enough that readers learn to skip it, in which case it belongs on the failing
  path only.

## Related

- [50-governance/canonical-spec.md](../../50-governance/canonical-spec.md) ·
  [50-governance/change-lifecycle.md](../../50-governance/change-lifecycle.md)
- [40-quality/definition-of-done.md](../../40-quality/definition-of-done.md#when-the-requirement-postdates-the-work)
- [ADR-0030](0030-the-tag-governs-the-workflow-not-what-it-reads.md) — the same
  shape one layer down: a guard that was not reporting what it did and did not
  cover
