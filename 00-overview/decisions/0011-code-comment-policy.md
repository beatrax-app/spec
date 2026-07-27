# ADR-0011: Code comment policy — readable code, architecture in documentation

**Status:** Accepted
**Date:** 2026-07-21

## Context

The codebase had drifted toward comment-heavy source: single-line notes
restating what the next line does, block comments duplicating what belongs in
the documentation tree, workflow provenance tokens scattered through docblocks,
and PHPDoc summary paragraphs a reader must reconcile against both the code and
the architecture docs.

That works against two positions the project already holds:

- Code should be readable on its own; naming and structure carry intent, not
  prose.
- Architecture lives in Markdown, linked from code — not re-explained inline
  where it rots out of sync ([ADR-0001](0001-modular-architecture.md)).

A convention was needed that is enforceable in CI so it does not depend on
reviewer vigilance, draws a clean line between machine directives that must be
kept and prose that must go, and is portable into other projects on the same
stack.

## Decision

Adopt the convention in [40-quality/code-comments.md](../../40-quality/code-comments.md),
enforced at two levels:

- **Mechanical rules M1–M6**, guarded by an architecture test that walks backend
  production PHP and asserts on comment tokens using the PHP tokeniser rather
  than a regex, because the tokeniser natively distinguishes the three comment
  species. No lone single-line comment; inline blocks are two to four lines; no
  informative block comments; docblocks are tag-only with no descriptive prose;
  no deferral or provenance tokens; every documentation link resolves to a real
  file.
- **Judgment rules J1–J5**, binding on every contributor — human or AI — but not
  machine-checkable: prefer self-documenting code, comment only genuinely
  complex *why*, architecture goes in the docs, nothing is deferred in a comment.

Documentation links use one tag for documentation paths and another for code
symbols; the two are never mixed. Scope is backend production PHP, excluding
tests and migrations. Frontend and template files are out of scope.

## Alternatives considered

| Option | Why it lost |
|--------|-------------|
| **Leave it to reviewer judgment** | It had already failed — the drift is what produced the problem. |
| **A formatter rule** | The formatter governs style, not comment semantics, and cannot express "prose belongs in the docs". |
| **A judgment-only document with no test** | Unenforceable, so it would drift exactly as the previous convention did. |

## Consequences

### Positive

- **The test is the binding invariant.** New backend code violating a mechanical
  rule fails CI.
- **Documentation links are verified.** A moved or deleted page breaks the build
  rather than rotting silently.
- **Portable by design.** The convention file and its reference test are the
  unit of reuse; they carry no project-specific assumptions beyond the scope
  roots.

### Negative

- **A one-time sweep was required**, and it was large: roughly 1 435 backend
  files, read and corrected per file rather than by blind find-and-replace, so
  no genuine *why* was lost. Eighteen plans across one phase.
- **PHPDoc becomes structural, not narrative.** Class purpose is carried by the
  class name plus a documentation link. That deepens the reliance on the
  documentation being accurate and current — which is a feature if the docs are
  maintained and a liability if they are not.
- A handful of type-narrowing docblocks were removed during the sweep, exposing
  literal-union type gaps that static analysis would otherwise have enforced.
  Those are tracked as follow-up work rather than silently reinstated as prose.

### Neutral

- The directive allow-list — static-analysis ignores, coverage markers, inline
  type annotations — is deliberately small. Adding to it is a reviewed change.

## Revisit if

- The mechanical rules produce enough false positives during ordinary work that
  contributors start reaching for the allow-list rather than restructuring code.

## Related

- [ADR-0001](0001-modular-architecture.md) · [ADR-0002](0002-di-only-rule.md) —
  the same enforce-by-test posture applied to structure
- [40-quality/code-comments.md](../../40-quality/code-comments.md) — the
  convention itself, with the mechanical and judgment rule tables
- [50-governance/ai-contributors.md](../../50-governance/ai-contributors.md) —
  the judgment rules bind AI-assisted contributions identically
