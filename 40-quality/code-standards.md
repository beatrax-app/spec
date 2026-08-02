# Code standards

**Status:** Accepted

## Dependency injection only

All collaborators are constructor-injected
([ADR-0002](../00-overview/decisions/0002-di-only-rule.md),
[Q-R1](README.md#the-q-r-namespace)).

**Forbidden:** facade static calls and global helper functions —
authentication, request, configuration, container, time, view, database, cache,
log, storage, and dispatch accessors.

**Allowed:** models used directly. Instantiation, static lookup, relationship
traversal, and query building through a model instance. The model is a value
type the consumer may know about; only the global indirection is forbidden.

**Specifics:**

- Logging through an injected logger interface.
- Time through injected immutable instants, never a global clock call at the
  call site.
- Configuration through injected typed objects or a repository collaborator.
  Free-form configuration lookup is forbidden in module code.

**The one carve-out:** service providers and the console-bootstrap layer, which
run before the container can inject. That carve-out has its own invariants so it
cannot quietly widen.

## The module boundary

A module may import another's public surface and its models, and nothing else
([20-architecture/contracts/module-boundary.md](../20-architecture/contracts/module-boundary.md)).

Enforced by a custom static-analysis rule at analysis time and by architecture
tests at test time.

## Money

Every monetary value is an exact minor-unit integer plus a currency code
([ADR-0009](../00-overview/decisions/0009-brick-money-multi-currency.md)).

- **No floating-point number may appear on the money path**
  ([Q-R6](README.md#the-q-r-namespace)). Not as a parameter, not as a return
  type, not as an intermediate.
- Mixing currencies raises rather than producing a total.
- Reading an absent money column raises rather than returning zero.
- Rates read from storage are exact decimals from the moment they leave the
  database.
- Persisted columns cast through the money boundary; the columns themselves stay
  primitive.

## User scoping

Every user-scoped model carries the scoping trait
([ADR-0008](../00-overview/decisions/0008-multi-user-belongstouser.md)).

**The ambient scope is a safety net, not the primary guard.** It resolves the
current user and is a no-op in background and command-line contexts, so any code
that can run outside a request re-asserts ownership against an explicitly passed
user and bypasses the scope rather than trusting it.

Raw queries against user-scoped tables carry an explicit filter, enforced by
architecture test where those queries exist.

## State machines

Every state column has exactly one sanctioned mutator, enforced by architecture
test and, where the store supports it, by paired triggers that reject an
out-of-enum value.

Transitions take a row lock with a busy timeout and, where the lifecycle has an
audit trail, write a transition row recording from, to, when, and by whom.

Illegal transitions raise. There is no general escape hatch — idempotent no-ops
belong in the actions, not in the machine.

## Sanctioned writers

For each shared column or table there is exactly one write path
([20-architecture/contracts/module-boundary.md](../20-architecture/contracts/module-boundary.md)).
Adding a second is a specification change, not a refactor.

## Errors

Typed, never stringly ([G2](../10-functional/features/g-ux/g2-error-model.md)).
Callers branch on the kind of failure. A message can then be rewritten without
breaking behaviour.

**Fail silently where the failure is information; fail loudly where the failure
would corrupt a number.** Both halves are enumerated in
[G2](../10-functional/features/g-ux/g2-error-model.md).

## Bounded everything

- Transactions are bounded; nothing holds a transaction proportional to total
  history ([ARCH-R17](../20-architecture/README.md#the-arch-r-namespace)).
- Scans are bounded; a page render never becomes a table walk.
- Queries per render are bounded regardless of row count, and where that matters
  it is verified by test.
- Frames, blobs, retries, and walks all have caps.
- Background dispatch happens after the causing transaction commits, never
  inside it.

## Encryption-aware code

Every read of a registered sensitive column decrypts before matching, parsing,
or displaying
([ADR-0018](../00-overview/decisions/0018-amounts-plaintext-at-rest.md)).

Work needing the key runs where the key is, or **skips with a warning**. It never
silently produces a wrong result.

Adding a column that holds identifying text means registering it — in the
sensitive-column registry and in the merge registry. Forgetting is silent until
somebody sees ciphertext.

## Naming and shape

- Names carry intent; comments do not
  ([code-comments.md](code-comments.md)).
- Data objects are immutable.
- Public surfaces are narrow: a contract exposes what a consumer needs, not what
  an implementation happens to have.
- A class doing two things is two classes.

## Formatting and analysis

Formatting is the standard preset, applied, not argued about
([Q-R3](README.md#the-q-r-namespace)).

Static analysis runs at the **maximum level in strict mode**
([Q-R2](README.md#the-q-r-namespace)), with the custom boundary rule and the
strict rule set — which is where the global-accessor ban is enforced.

An analysis suppression is a reviewed exception with a reason, not a
convenience.

## Frontend

The interface is server-rendered with a thin client layer. Test investment goes
into backend correctness, and **frontend tests are not required**
([testing-strategy.md](testing-strategy.md)).

Themed views carry a dark companion for every light-mode colour utility,
enforced by architecture test
([G3](../10-functional/features/g-ux/g3-accessibility.md)).

Credentials and secrets never appear in a serialisable component property, so
they cannot reach a rendered snapshot — enforced by a registry-backed
architecture test.

Output is escaped. Where a value must be rendered as raw markup — an inline
vector image is the honest case, since escaping it stops it drawing — the
property holding it is locked against client mutation. A serialisable component
property is rehydrated from the client on every request, so "the server built
this markup" is true only of the first render; without the lock the raw sink
accepts whatever the client returns. The lock and the raw echo are a pair, and
neither is safe to add or remove alone.

## Related

- [ADR-0001](../00-overview/decisions/0001-modular-architecture.md) · [ADR-0002](../00-overview/decisions/0002-di-only-rule.md) · [ADR-0009](../00-overview/decisions/0009-brick-money-multi-currency.md) · [ADR-0018](../00-overview/decisions/0018-amounts-plaintext-at-rest.md)
- [code-comments.md](code-comments.md) · [testing-strategy.md](testing-strategy.md)
- [20-architecture/contracts/module-boundary.md](../20-architecture/contracts/module-boundary.md)
