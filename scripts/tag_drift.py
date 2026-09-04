#!/usr/bin/env python3
"""Does the moving major tag still point at what consumers should be running?

Every sibling repository calls the shared workflows as `@v1` (ADR-0021). The tag
is moved by hand after a shared workflow merges, and a forgotten move means the
fix reaches nobody, silently, until someone reads the tag.

Two modes:

  tag_drift.py                        the tag against the default branch
  tag_drift.py --pending BASE HEAD    whether merging a range will owe a move

Exit 0 = the tag is where it should be, 1 = it is not.
"""
from __future__ import annotations
import argparse, os, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
WORKFLOWS = ".github/workflows"
HEADING = "Shared workflow tags"
REF = re.compile(r"\A[0-9A-Za-z._/-]{1,255}\Z")
SHA = re.compile(r"\A[0-9a-f]{40}\Z")
MAJOR_TAG = re.compile(r"^v(\d+)$")
IMMUTABLE_TAG = re.compile(r"^v(\d+)\.\d+\.\d+$")
CHECKED_OUT = re.compile(r"\.spec-canonical/(\S+\.py)")
FETCHED = re.compile(r"raw\.githubusercontent\.com/beatrax-app/spec/main/(\S+?)[\s\"']")


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args],
                          capture_output=True, text=True, check=True).stdout.strip()


def git_ok(*args: str) -> bool:
    return subprocess.run(["git", "-C", str(ROOT), *args],
                          capture_output=True, text=True).returncode == 0


def read(ref: str, path: str) -> str:
    body = subprocess.run(["git", "-C", str(ROOT), "show", f"{ref}:{path}"],
                          capture_output=True, text=True)
    return body.stdout if body.returncode == 0 else ""


def reusable(ref: str) -> set[str]:
    """Workflows a sibling repository can call, so the ones the tag governs.

    A workflow without `workflow_call` is this repository's own business and its
    drift costs consumers nothing."""
    paths = git("ls-tree", "-r", "--name-only", ref, "--", WORKFLOWS).splitlines()
    return {p for p in paths
            if p.endswith((".yml", ".yaml")) and "workflow_call" in read(ref, p)}


def run_time_paths(ref: str) -> set[str]:
    """Files the shared workflows read from this repository's *default branch*
    while they run, rather than from the tag they were called at. They reach
    consumers on merge, so the tag does not govern them at all."""
    out = set()
    for path in reusable(ref):
        body = read(ref, path)
        out |= set(CHECKED_OUT.findall(body)) | set(FETCHED.findall(body))
    return out


def changed(a: str, b: str, *paths: str) -> list[str]:
    # An empty pathspec means "everything" to git, which would turn a question
    # about four files into an answer about the whole tree.
    if not paths:
        return []
    return [p for p in git("diff", "--name-only", a, b, "--", *paths).splitlines() if p]


def major_tags() -> list[str]:
    return sorted((t for t in git("tag", "--list").splitlines() if MAJOR_TAG.match(t)),
                  key=lambda t: int(MAJOR_TAG.match(t).group(1)))


def immutable_at(commit: str, major: str) -> list[str]:
    tags = git("tag", "--points-at", commit).splitlines()
    return [t for t in tags if (m := IMMUTABLE_TAG.match(t)) and m.group(1) == major]


class Report:
    def __init__(self) -> None:
        self.lines: list[str] = []
        self.failed = False

    def error(self, msg: str) -> None:
        self.failed = True
        print(f"::error::{msg}")
        self.lines.append(f"- **{msg}**")

    def notice(self, msg: str) -> None:
        print(f"::notice::{msg}")
        self.lines.append(f"- {msg}")

    def say(self, msg: str) -> None:
        print(msg)
        self.lines.append(msg)

    def flush(self) -> int:
        summary = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary:
            with open(summary, "a", encoding="utf-8") as fh:
                fh.write(f"## {HEADING}\n\n" + "\n".join(self.lines) + "\n")
        return 1 if self.failed else 0


def audit_tag(r: Report, tag: str, base: str, base_sha: str) -> None:
    major = MAJOR_TAG.match(tag).group(1)
    tag_sha = git("rev-list", "-n1", tag)
    behind = git("rev-list", "--count", f"{tag}..{base}")
    r.say(f"\n### `{tag}` → `{tag_sha[:9]}` · `{base}` → `{base_sha[:9]}` "
          f"· {behind} commit(s) behind")

    if not git_ok("merge-base", "--is-ancestor", tag_sha, base_sha):
        r.error(f"{tag} points at {tag_sha[:9]}, which is not an ancestor of "
                f"{base} ({base_sha[:9]}) — it was moved onto something else")
        return

    pinned = immutable_at(tag_sha, major)
    if pinned:
        r.say(f"immutable companion: {', '.join(pinned)}")
    else:
        r.error(f"{tag} sits on {tag_sha[:9]} with no v{major}.x.y tag on the same "
                f"commit — what {tag} points at today is not recoverable (ADR-0021)")

    shared = sorted((reusable(tag) | reusable(base)) &
                    set(changed(tag_sha, base_sha, WORKFLOWS)))
    if shared:
        r.error(f"{len(shared)} shared workflow(s) changed on {base} since {tag}; "
                f"every consumer still runs the {tag} copy — move the tag")
        for path in shared:
            stat = git("diff", "--shortstat", tag_sha, base_sha, "--", path)
            r.say(f"    - `{path}` — {stat or 'differs'}")
    else:
        r.say(f"no shared workflow differs between {tag} and {base}")

    # Not a tag problem and not fixed by moving the tag: these already reached
    # every consumer at merge. Reported because it is ADR-0021's guarantee not
    # holding, which is a decision to take rather than a chore to do.
    live = sorted(set(changed(tag_sha, base_sha, *run_time_paths(base_sha))))
    if live:
        r.notice(f"{len(live)} file(s) the shared workflows read from {base} at run "
                 f"time differ from {tag}, so they are already live on every "
                 f"consumer and no tag move governs them: {', '.join(live)}")


def audit(base: str) -> int:
    r = Report()
    tags = major_tags()
    if not tags:
        r.say("no moving major tag exists yet; nothing to check")
        return r.flush()
    base_sha = git("rev-parse", base)
    for tag in tags:
        audit_tag(r, tag, base, base_sha)
    return r.flush()


def pending(base_sha: str, head_sha: str) -> int:
    r = Report()
    if not all(SHA.match(v) for v in (base_sha, head_sha)):
        r.say("no pull-request commit range; nothing to check")
        return r.flush()
    shared = sorted((reusable(base_sha) | reusable(head_sha)) &
                    set(changed(base_sha, head_sha, WORKFLOWS)))
    if shared:
        moving = " / ".join(major_tags()) or "the major"
        r.notice(f"this pull request changes a shared workflow, so merging it obliges a "
                 f"{moving} move before any consumer sees the change: " + ", ".join(shared))
    else:
        r.say("no shared workflow changed; no tag move is owed")
    return r.flush()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--pending", nargs=2, metavar=("BASE", "HEAD"))
    args = ap.parse_args()
    # Every value below reaches git as an argv element. Nothing shaped unlike a
    # ref gets that far, whatever the caller passed.
    if args.pending:
        base, head = args.pending
        return pending(base if SHA.match(base) else "", head if SHA.match(head) else "")
    if not REF.match(args.base):
        sys.exit("tag_drift: --base must be a valid git ref")
    base = args.base if git_ok("rev-parse", "--verify", args.base) else "main"
    return audit(base)


if __name__ == "__main__":
    sys.exit(main())
