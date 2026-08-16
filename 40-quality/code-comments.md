# Code comments

**Status:** Accepted

Code should be readable on its own. Architecture belongs in documentation.
Comments are the exception, not the norm — reserved for the few places where
genuinely non-obvious code needs a *why* the code itself cannot carry.

This page is the single source of truth for what a backend comment may be. The
decision is [ADR-0011](../00-overview/decisions/0011-code-comment-policy.md).

## Philosophy

1. **Readable code first.** If a comment could be deleted by renaming a
   variable, extracting a method, or introducing a named constant — do that
   instead.
2. **Architecture lives in documentation.** System shape, data flow,
   cross-module contracts, and how the pieces fit are written in Markdown and
   linked from the class, never re-explained inline where they rot out of sync.
3. **Comments explain *why*, never *what*.** A comment restating the next line is
   noise. One capturing a non-obvious reason, constraint, or trap earns its
   place — and if it does, it is never a throwaway one-liner.
4. **Production-ready always.** Code that ships is finished. No deferral notes,
   no tickets, no "come back to this". If work remains, the work is not done.

## Scope

Backend production source. Explicitly **excluded**: test files, which may carry
explanatory rationale freely; framework-shaped migration scaffolding; and
templates and frontend assets, which are out of scope for this iteration.

## The two layers

Keep them distinct. Conflating them makes the test either toothless or
tyrannical.

- **Mechanical (`M*`)** — comment *shape*. Deterministic, greppable, enforced by
  test.
- **Judgment (`J*`)** — comment *worth*. Whether code is complex enough to
  deserve a comment at all. Only a reviewer can judge these; they are binding
  anyway.

## Mechanical rules

| # | Rule |
|---|------|
| **M1** | No lone single-line comment. An informative line comment must be part of a contiguous block of **two to four** lines. A one-line note means the code should say it instead — delete it, or expand it into a proper block if the *why* is real. |
| **M2** | A contiguous line-comment block is **two lines minimum, four maximum**. Anything needing more prose belongs in documentation, linked. |
| **M3** | No informative block comments. Only documentation blocks may use the block form. |
| **M4** | Documentation blocks are **tag-only**. No descriptive prose: no summary paragraph before the first tag, and no block whose content is prose with no tags. Multi-line continuations of a tag are fine. A class's purpose is carried by its name plus a documentation link, not a paragraph. |
| **M5** | No deferral or provenance tokens anywhere in a comment — no deferral markers, no ticket keys, no workflow references. |
| **M6** | Every documentation link naming a file must resolve to a real file. A broken link fails the build. |

### The directive allow-list

A small set of comments are **not** informative comments — they are machine
directives tooling reads, and they are exempt from M1 to M4 and must be
retained: static-analysis ignores and inline type annotations, coverage markers,
and style-checker directives.

The allow-list is deliberately small and precise. Adding to it is a reviewed
change, not a convenience.

## Judgment rules

| # | Rule |
|---|------|
| **J1** | Prefer self-documenting code. Exhaust rename, extract, and named constant before writing any comment. |
| **J2** | Write a comment block only where the code is genuinely complex or the *why* is non-obvious — a constraint, an ordering trap, a defended-against edge case. Never to narrate *what* the code does. |
| **J3** | Architecture, data flow, and cross-module contracts go in documentation, never inline. |
| **J4** | Where a class has a documented home, link it. The class needs no prose description — its name and that link are the documentation. |
| **J5** | Nothing is deferred in a comment. If it is not done, it is not production-ready — finish it or cut it. |

## Linking

Two tags, two purposes, never mixed:

- **A documentation link** points at a documentation path, relative to the source
  file. Greppable, and verified to exist by M6.
- **A symbol reference** points at a code symbol. Never a documentation path.

## Shape

A valid documentation block is tags only, with no preamble. A block opening with
a prose summary before any tag is a violation — everything that paragraph was
trying to say belongs in the linked page.

## Enforcement

The mechanical rules are enforced by a test that walks the in-scope files and
asserts on their comment tokens. It uses the language's **tokeniser** rather
than a comment-stripping pattern, because the tokeniser natively distinguishes
the three comment species:

| Token kind | Rules that apply |
|------------|------------------|
| Documentation block | M4, M5, M6 |
| Block comment | M3 — a violation by existing |
| Line comment | M1, M2, M5, unless allow-listed |

The reference implementation lives in the product repository's test suite. The
banned-token pattern and the directive allow-list are the two knobs that need
tuning against a real offender set.

## What adopting this costs

The one-time sweep is large and must be **manual per file** — every file read and
corrected, so no genuine *why* is lost. A blind find-and-replace would delete
real reasoning along with the noise. In Beatrax that sweep covered roughly 1 435
backend files across eighteen plans, and the test was activated only once the
sweep passed.

It also has a consequence worth naming: **class purpose moves into the
documentation**, which deepens the reliance on that documentation being accurate
and current. That is a feature where the docs are maintained and a liability
where they are not.

A handful of type-narrowing annotations were removed during the sweep, exposing
type gaps that static analysis would otherwise have enforced. Those are tracked
as follow-up work rather than quietly reinstated as prose.

## Portability

To adopt this elsewhere: copy this page, copy the reference test and adjust its
scope roots and allow-list, and record the decision as a decision record. The
rules carry no project-specific assumptions — only the scope roots do.

## Related

- [ADR-0011](../00-overview/decisions/0011-code-comment-policy.md)
- [code-standards.md](code-standards.md)
- [50-governance/ai-contributors.md](../50-governance/ai-contributors.md) — the judgment rules bind AI contributions identically
