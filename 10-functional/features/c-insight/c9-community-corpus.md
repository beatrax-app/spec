# C9 — Community merchant corpus

**Status:** Accepted · **Area:** C — Insight and alerts

---

## Purpose

`ZTL*8829 AMS NL` is a merchant. Nobody's first import knows which one. A
crowd-sourced corpus of description fragments mapped to human-readable names
means the first user to identify a merchant saves everyone else the work.

The hard part is doing that without any of the user's data leaving their
machine.

## Behaviour

### Bundled, not fetched

The corpus ships **inside the application** as a data file and is seeded locally
on install. There is no corpus-fetch service, no call home to check for updates,
and no telemetry. A user who never enables anything still gets the corpus,
because it arrived with the download.

### Two tiers

A global tier from the bundle, and a per-user override tier. A user's own entry
always beats the global one for the same pattern.

Matching runs exact-first, then generalised, and every scan is bounded so a
large corpus cannot turn a page render into a table walk.

Patterns are literal substrings by default. A pattern may declare itself a
regular expression, in which case a malformed expression is logged and treated
as a non-match rather than being allowed to throw.

### Contribution is opt-in, and it never sends data

Contributing is off by default. When enabled, the user can suggest a mapping for
a description they have identified. **What is sent is the user's own typed
review — a pattern and a name — never their transactions, amounts, dates, or
counterparties.**

The submission opens the project's own repository in the browser with the
suggestion pre-composed, so the user sees exactly what they are contributing
before anything is published, and publishes it themselves.

The branch identifier is derived deterministically from the pattern, so
iterating on the same suggestion re-uses the same branch rather than spawning a
new one each time.

### The external-link gate

Opening an external URL passes two gates: it must be HTTPS, and its host must be
on an allow-list. Any other scheme is rejected outright — including ones a
general URL validator would accept.

That gate is the **only** sanctioned way anything in the product opens an
external link, enforced by architecture test. Outside the desktop shell it falls
back to a no-op that logs the URL rather than launching anything.

### Three toggles, all off by default

Consult the shared list, offer to contribute, and update the shared list on
application updates. The third currently does nothing and says so — it reserves
the setting for a future update mechanism rather than pretending one exists.

The contribution affordance is gated **server-side**: when contribution is off,
the component renders nothing at all. Hiding it with styling would leave it in
the page.

### The corpus is advisory

The categoriser never reads the corpus automatically. It is consulted for
**display names** ([B4](../b-ledger/b4-counterparties.md)) and can be imported
into a user's own rules by explicit action — but a bundled mapping never assigns
a category on its own.

### Support resources

A related corpus maps counterparty names to help, cancellation, and
cheaper-plan resources, which is what [C3](c3-drift-alerts.md) offers alongside
a drift alert. Matching is word-based rather than substring — both names are
reduced to word lists with legal-entity suffixes dropped, and a resource matches
when its words are a leading prefix of the counterparty's. The longest match
wins. Brand qualifiers are deliberately not stripped, because a premium tier is
a different product.

A contact link is refused if the recipient contains characters that would permit
header or recipient injection.

### Failures degrade

A missing or malformed corpus file logs a warning and yields an empty corpus;
the application boots and works without one. A malformed individual entry is
skipped, not fatal to the rest. Data files are parsed with object instantiation
disabled.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| No corpus files present | Warning logged; empty corpus; the app works. |
| A malformed entry | Skipped; the rest of the corpus seeds. |
| An entry naming an unknown category | Seeded with the category cleared, and the mismatch logged so it is visible. |
| Re-running the install | Idempotent; nothing duplicates. |
| A user editing a suggestion they already made | The deterministic branch identifier means the same branch is re-used. |
| Toggling contribution off mid-session | The affordance disappears on the next render; corpus reads are unaffected. |
| A generalised pattern colliding with another entry's exact pattern | Exact is evaluated first and wins. |
| Running outside the desktop shell | External-link opening no-ops with a logged URL. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **C9-R1** | The corpus MUST ship inside the application and MUST be seeded locally; no corpus fetch may occur. |
| **C9-R2** | A per-user override MUST beat the global entry for the same pattern. |
| **C9-R3** | Matching MUST evaluate exact patterns before generalised ones. |
| **C9-R4** | Every corpus scan MUST be bounded. |
| **C9-R5** | A malformed regular-expression pattern MUST be logged and treated as a non-match, never allowed to throw. |
| **C9-R6** | Contribution MUST be off by default. |
| **C9-R7** | A submission MUST contain only the user's typed pattern and name; no transaction data may be included. |
| **C9-R8** | The user MUST see the composed submission before it is published, and MUST publish it themselves. |
| **C9-R9** | The submission branch identifier MUST be derived deterministically from the pattern. |
| **C9-R10** | External URLs MUST pass both an HTTPS check and a host allow-list before being opened. |
| **C9-R11** | A non-HTTPS scheme MUST be rejected explicitly, including schemes a general URL validator would accept. |
| **C9-R12** | Exactly one sanctioned path MUST exist for opening an external URL, enforced by architecture test. |
| **C9-R13** | Outside the desktop shell, external-link opening MUST no-op with a logged URL. |
| **C9-R14** | The contribution affordance MUST be gated server-side and MUST render nothing when disabled. |
| **C9-R15** | A setting that currently does nothing MUST say so rather than implying a behaviour. |
| **C9-R16** | The categoriser MUST NOT read the corpus automatically; import into a user's own rules MUST be an explicit action. |
| **C9-R17** | Support-resource matching MUST be word-based with legal-entity suffixes dropped and the longest match winning. |
| **C9-R18** | Brand qualifiers MUST NOT be stripped during support-resource matching. |
| **C9-R19** | A contact link MUST be refused where the recipient contains injection-capable characters. |
| **C9-R20** | A missing or malformed corpus MUST log a warning and yield an empty corpus without preventing boot. |
| **C9-R21** | Data files MUST be parsed with object instantiation disabled. |
| **C9-R22** | Seeding MUST be idempotent across repeated installs. |

## Related

- [B4 Counterparties](../b-ledger/b4-counterparties.md) — the display-name consumer
- [B2 Categorisation](../b-ledger/b2-categorisation.md) — why the corpus is advisory
- [C3 Drift alerts](c3-drift-alerts.md) — the support-resource consumer
- [G1 Privacy stance](../g-ux/g1-privacy.md)
