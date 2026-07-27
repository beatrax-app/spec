# Runbooks

**Status:** Accepted

The operational procedures, and where they live.

## Where the procedures live

**The executable procedures — with real commands, real paths, and real flags —
live in the product repository**, because they change with the code and must be
tested against it. A runbook in this repository would drift from the commands it
describes within one release.

**This page states what a runbook must guarantee.** The product's version states
how.

## The procedures

| Runbook | Must guarantee |
|---------|----------------|
| **Verify a release** | A user can reproduce, by hand, the same signature-and-hash chain the updater runs ([F6](../10-functional/features/f-platform/f6-updates.md)). |
| **Cut a release** | The pre-tag checklist, the tag, and the post-tag verification, in order ([releasing.md](releasing.md)). |
| **Operator recovery** | Restore from a backup without the recovery attempt destroying what is left. |
| **Force a password reset** | The last-resort path, on the machine, when recovery codes are gone ([F3](../10-functional/features/f-platform/f3-auth-and-app-lock.md)). |
| **Repository security setup** | Reproduce the branch ruleset, the platform security features, and the ownership generation from scratch. |

## The guarantees each must hold

### Verify a release

- Reproducible **by a user**, not only by a maintainer.
- Uses only what a release publishes: the checksums and the signed manifest.
- Verifies the **manifest signature first**, then the binary hash against the
  now-trusted manifest. Not the other way round.

### Cut a release

- The pre-tag checklist is complete before the tag is pushed.
- The ruleset's required checks are confirmed to still name the jobs that run
  ([OPS-R18](README.md#the-ops-r-namespace)).
- A stable release is published by a human from the draft.
- The manifest is verified by hand at least once.

### Operator recovery

**The ordering is the safety contract** and the runbook must not reorder it:

1. Decrypt and integrity-check to a temporary location. A wrong passphrase or a
   corrupt backup fails **before** the live database is touched.
2. Take a pre-restore snapshot, exempt from retention pruning.
3. Swap atomically.
4. Verify afterwards through the application's own connection, so the store's
   configuration is re-applied.

It must also cover the paths that are not a restore: stuck locks, a wedged
worker, a drifted store configuration, and the application-key sentinel.

### Force a password reset

- Requires access to the machine where the database lives. That is the point.
- States plainly that a user who cannot reach a terminal, has lost their
  recovery codes, and has no other owner **has no route back in**
  ([ADR-0010](../00-overview/decisions/0010-recovery-codes-no-smtp.md)).

### Repository security setup

- Reproducible from scratch on a new repository.
- Covers what is available only once a repository is public, and says which is
  which.
- Includes regenerating the ownership file from the registry rather than writing
  one.

## Writing a runbook

| Rule | Why |
|------|-----|
| Every step is a command or a decision, never a hint | A runbook is read under pressure. |
| Destructive steps are marked, and preceded by their safety step | The ordering is the contract. |
| Every step says what success looks like | Otherwise the operator cannot tell whether to continue. |
| A failure at any step says what to do | [G2](../10-functional/features/g-ux/g2-error-model.md) applies to operators too. |
| No step requires information the runbook has not told the operator to gather | The commonest reason a runbook stalls. |

## Related

- [releasing.md](releasing.md) · [staging.md](staging.md)
- [F4 Backup, restore and recovery](../10-functional/features/f-platform/f4-backup-restore.md) · [F6 Updates](../10-functional/features/f-platform/f6-updates.md)
- [J6 Recovery](../10-functional/journeys/j6-recovery.md)
- [30-repos/beatrax.md](../30-repos/beatrax.md)
