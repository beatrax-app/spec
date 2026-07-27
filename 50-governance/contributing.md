# Contributing

**Status:** Accepted

Contributions are welcome. This page is what to actually do.

## Before you start

**Read [canonical-spec.md](canonical-spec.md).** It is the one rule everything
else follows from, and it will change how you open your first pull request.

**Ask first if it is large.** Open a discussion, or ask in
[the Discord](https://discord.gg/FYuV9CbTHR). Agreeing on shape early is cheaper
than reworking a finished pull request.

## Setting up

The product's toolchain is containerised — the host needs only the container
runtime. Clone, install dependencies through the container, migrate, and run.
The exact commands live in the product repository's own setup documentation,
which is where they belong because they change with the toolchain.

The repository ships fixtures so you can exercise the ingestion paths without
owning accounts at any of the source institutions.

## The three gates

Every pull request passes all three before review starts:

1. **Formatting** — the standard preset.
2. **Static analysis** — maximum level, strict mode.
3. **Tests** — the full suite including architecture tests.

Run them locally first. Local hooks run the cheap ones automatically.

## Conventions that are not negotiable

These are enforced. Fighting them is a slower path than following them.

- **Dependency injection only.** No global accessors in module code
  ([ADR-0002](../00-overview/decisions/0002-di-only-rule.md)).
- **The module boundary.** Import another module's public surface or its models,
  never its interior
  ([20-architecture/contracts/module-boundary.md](../20-architecture/contracts/module-boundary.md)).
- **No floating-point money.** Anywhere on the money path.
- **The comment policy.** Mechanical rules are tested
  ([40-quality/code-comments.md](../40-quality/code-comments.md)).
- **Sanctioned writers.** One write path per shared column.
- **Cross-user tests.** Every user-scoped surface gets one.

## Commits

- Conventional subjects: a type, an optional scope, and a subject.
- **Signed off**, matching your author identity: commit with the sign-off flag
  ([dco.md](dco.md)).
- **A specification citation** in a trailer:

  ```text
  Spec: B5-R13
  ```

  Routine maintenance cites `GOV-R12`.

- Branch names follow a type-and-slug shape.
- The default branch requires **signed** commits; configure signing before you
  push.

## Opening a pull request

1. Target the default branch.
2. Fill in the template. **The specification citation goes in the body as well as
   in a commit** — the gate reads both.
3. Write the commit subject for the person who will read the release notes.
   The notes are assembled from the commits, so the subject is the entry.
4. Wait for the pipeline. A sticky comment will link each identifier you cited
   to its defining file.
5. Address feedback with new commits; avoid force-pushing during review unless
   asked.
6. Merges are squash or rebase; the head branch is deleted afterwards.

## Changing behaviour

**The specification change goes first.** Open a pull request here, get the
requirement reviewed and merged, then cite it from the implementation
([change-lifecycle.md](change-lifecycle.md)).

If that feels like friction — it is, and it is deliberate. The requirement gets
written by the person who understands the problem, at the moment they understand
it.

## What is welcome

- Bug fixes anywhere.
- Additional source-format adapters, especially for institutions not yet covered.
- Additional receipt matchers.
- Additional categorisation heuristics and merchant-resolution improvements.
- Performance work **with a benchmark or a profile** justifying it.
- Accessibility improvements.
- Documentation, especially worked examples.
- Corpus contributions, through the in-product suggestion flow
  ([C9](../10-functional/features/c-insight/c9-community-corpus.md)).

## What is not

- **Anything that phones home.** Not negotiable
  ([ADR-0004](../00-overview/decisions/0004-local-only-hosting.md)).
- **Anything that acts on the user's behalf** — cancelling, switching,
  initiating payments
  ([P7](../00-overview/vision.md#p7--it-informs-it-never-transacts)).
- **Foundational rework** — changing the store, the interface stack, or the
  module model. Those are decision-record conversations, not pull requests.
- Features already listed as non-goals in the [vision](../00-overview/vision.md).

If your idea is in the grey zone, ask. It is faster than writing code that will
not merge.

## AI-assisted contributions

Welcome, held to the same standard as every other contribution, and nothing
to declare. See [ai-contributors.md](ai-contributors.md).

## Code of conduct

The Contributor Covenant, in the organisation's community health repository.
Participating means agreeing to it, and to the licence.

## Related

- [canonical-spec.md](canonical-spec.md) · [change-lifecycle.md](change-lifecycle.md) · [dco.md](dco.md) · [issue-routing.md](issue-routing.md)
- [40-quality/](../40-quality/) · [30-repos/](../30-repos/)
