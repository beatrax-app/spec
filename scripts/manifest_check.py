#!/usr/bin/env python3
"""Validate every version manifest, on every push — OPS-R14, OPS-R15, OPS-R16.

`check_stageable.py` asserts OPS-R14 once, at the moment a `planned` manifest is
staged, and exits on the first line for a manifest in any other status. A staged
manifest's goals then keep changing — a goals change is a reviewed change, not a
frozen one (OPS-R17) — and nothing reads them again. `2.0.0.toml` is also not a
file `integrity.py` looks at: its citing set is Markdown, workflows and scripts.
So the identifiers a release is committed to delivering were the one body of
citations in this repository that no always-on check had ever resolved, and an
entry claiming a requirement had landed when it had not survived there.

What this refuses:

  - a goal that is not a requirement identifier the specification defines,
    in any manifest, at any status (OPS-R14)
  - a goal listed twice in one manifest
  - a status outside the lifecycle, or a second version staged or releasable
    while another already is (OPS-R15, OPS-R16)
  - a goal still marked *(Open)* on its own feature page sitting under a group
    heading that asserts `(landed)` without qualification
  - a goal marked *(Open)* that the manifest names nowhere a reader would look:
    neither in its header comment nor in its own group heading
  - a goal the manifest's own header lists as outstanding, not satisfied or
    unproven, sitting under an unqualified `(landed)` heading — the file
    disagreeing with itself
  - a goal the roadmap lists as still outstanding sitting under an unqualified
    `(landed)` heading — the two pages disagreeing about one identifier
  - a requirement marked *(Open)* anywhere in the specification that no manifest
    and no roadmap bucket names at all

The last four make the *(Open)* marker and the roadmap's buckets load-bearing.
They cannot see a requirement that is unsatisfied and marked as neither: for
that, the feature page has to be honest first, and only a reader can make it so.

The last one is the roadmap's own rule turned into a check. Four requirements
were once in neither the outstanding list nor the backlog nor the goals, and
that was found by a reader rather than by a gate. A requirement in no bucket is
not unclassified, it is invisible: nothing schedules it and nothing has declined
it. Naming it — as a goal, as backlog, or as an acknowledged omission awaiting a
ruling — is what clears this; being quietly unsatisfied is not.

Exit 0 = clean, 1 = problems found.
"""
from __future__ import annotations
import re, sys, tomllib, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
VERSIONS = ROOT / "70-operations" / "versions"
ROADMAP = ROOT / "00-overview" / "roadmap.md"

REQ_DEF = re.compile(r"^\|\s*\*\*([A-Z]+\d*-R\d+)\*\*\s*\|(.*)$", re.M)
REQ_CITE = re.compile(r"\b([A-Z]+\d*-R\d+)\b")
BARE_R = re.compile(r"\bR(\d+)\b")
# `X-Rn .. X-Rm` in the header, `Rn-Rm` or `Rn\u2013Rm` in a group heading. Both
# name a block, and a block named as an exception has to be read as one.
RANGE = re.compile(r"\b([A-Z]+\d*)-R(\d+)\s*(?:\.\.|\u2013|-{1,2})\s*(?:\1-)?R?(\d+)\b")
BARE_RANGE = re.compile(r"\bR(\d+)\s*(?:\.\.|\u2013|-{1,2})\s*R?(\d+)\b")
# A group heading: `  # ── Some words (parenthetical) ─────────`.
HEADING = re.compile(r"^\s*#\s*─+\s*(.*?)\s*─*\s*$")
GOAL_LINE = re.compile(r'"([A-Z]+\d*-R\d+)"')
STATUSES = ("planned", "staged", "releasable", "released", "yanked")
LANDED = re.compile(r"\blanded\b", re.I)
# The header's own lists of what it does not claim, and any other list heading
# that ends one of them.
UNMET_HEADING = re.compile(r"^#\s*(NOT SATISFIED|UNPROVEN|OUTSTANDING)\b[^:]*:\s*$")
OTHER_HEADING = re.compile(r"^#\s*[A-Z][A-Z ,]{3,}\b[^:]*:\s*$")


def requirements() -> dict[str, tuple[str, bool]]:
    """Every requirement the spec defines -> (page, is it marked open)."""
    found: dict[str, tuple[str, bool]] = {}
    for md in ROOT.rglob("*.md"):
        if ".git" in md.parts:
            continue
        rel = str(md.relative_to(ROOT))
        for m in REQ_DEF.finditer(md.read_text(encoding="utf-8", errors="ignore")):
            found[m.group(1)] = (rel, "*(Open)*" in m.group(2))
    return found


def named_ids(text: str, prefixes: set[str]) -> set[str]:
    """Identifiers a passage names — written out, as a range, or bare `R12`
    inside a heading whose group carries exactly one prefix."""
    named = set(REQ_CITE.findall(text))
    for pre, lo, hi in RANGE.findall(text):
        named.update(f"{pre}-R{n}" for n in range(int(lo), int(hi) + 1))
    if len(prefixes) == 1:
        only = next(iter(prefixes))
        named.update(f"{only}-R{n}" for n in BARE_R.findall(text))
        for lo, hi in BARE_RANGE.findall(text):
            named.update(f"{only}-R{n}" for n in range(int(lo), int(hi) + 1))
    return named


def parse(manifest: pathlib.Path):
    """The header comment, and each goal with the group heading above it.

    tomllib discards comments, and the comments are where this file makes its
    claims — `(landed)` is an assertion, not decoration."""
    header: list[str] = []
    groups: dict[str, str] = {}
    order: list[str] = []
    heading = ""
    in_goals = False
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not in_goals:
            if line.lstrip().startswith("#"):
                header.append(line)
            if line.startswith("goals"):
                in_goals = True
            continue
        m = HEADING.match(line)
        if m:
            heading = m.group(1)
            continue
        for gid in GOAL_LINE.findall(line):
            groups[gid] = heading
            order.append(gid)
    return "\n".join(header), groups, order


def header_unmet(header: str) -> set[str]:
    """Identifiers the header's own unmet lists name.

    Three commits in a row edited this block and left the group headings below
    it untouched, so the file said the whole sync block was satisfied twelve
    lines above a heading calling three of it outstanding. Whichever half is
    right, they cannot both be."""
    unmet: set[str] = set()
    collecting = False
    for line in header.splitlines():
        if UNMET_HEADING.match(line):
            collecting = True
            continue
        # A blank comment line closes the list. Prose after it is commentary,
        # and an id it happens to mention is not a claim that the id is unmet.
        if re.match(r"^#\s*$", line):
            collecting = False
        elif OTHER_HEADING.match(line):
            collecting = False
        if collecting:
            unmet |= named_ids(line, set())
    return unmet


def roadmap_outstanding() -> set[str]:
    """Identifiers the roadmap still lists under what has to close first.

    The page keeps a closed item in place rather than deleting it, marked
    `**done**` — twice, by its own convention — so that a reader arriving from
    an old link is told what happened to it. A paragraph carrying that marker
    is a record of something closed, not a claim that it is outstanding."""
    if not ROADMAP.is_file():
        return set()
    text = ROADMAP.read_text(encoding="utf-8")
    start = text.find("## Remaining before v2.0 can ship")
    if start < 0:
        return set()
    end = text.find("\n## ", start + 1)
    section = text[start:end if end > 0 else len(text)]
    return {rid
            for para in section.split("\n\n") if "**done**" not in para
            for rid in REQ_CITE.findall(para)}


def check(manifest: pathlib.Path, reqs, in_flight, outstanding) -> list[str]:
    name = manifest.name
    problems: list[str] = []
    data = tomllib.loads(manifest.read_text(encoding="utf-8"))
    header, groups, order = parse(manifest)
    unmet = header_unmet(header)

    status = data.get("status")
    if status not in STATUSES:
        problems.append(f"{name}: status '{status}' is not one of {', '.join(STATUSES)}")
    if status in ("staged", "releasable"):
        in_flight.append(name)

    goals = data.get("goals", [])
    for gid, n in collections.Counter(goals).items():
        if n > 1:
            problems.append(f"{name}: goal listed {n}x: {gid}")

    # The comment scan and tomllib must agree, or the group a goal is claimed
    # under is not the group it is in.
    if order != list(goals):
        problems.append(f"{name}: goals array did not parse as written; "
                        "the group headings cannot be trusted")
        return problems

    prefixes: dict[str, set[str]] = collections.defaultdict(set)
    for gid in goals:
        prefixes[groups[gid]].add(gid.split("-R")[0])

    for gid in goals:
        if gid not in reqs:
            problems.append(f"{name}: goal not defined in the "
                            f"specification: {gid} (OPS-R14)")
            continue
        page, is_open = reqs[gid]
        heading = groups[gid]
        excepted = named_ids(heading, prefixes[heading])
        # A heading saying "landed" claims it of every goal beneath it except
        # the ones it names — which is how the one qualified heading in this
        # repository already reads, and the only way an exception is legible.
        claims_landed = bool(LANDED.search(heading)) and gid not in excepted

        if is_open and claims_landed:
            problems.append(
                f"{name}: {gid} is marked *(Open)* in {page} but is grouped under "
                f'"{heading}"')
        if is_open and not claims_landed:
            where = named_ids(header, set()) | named_ids(heading, prefixes[heading])
            if gid not in where:
                problems.append(
                    f"{name}: {gid} is marked *(Open)* in {page} and the manifest "
                    "names it in neither its header nor its group heading, so a "
                    "reader is not told this goal is unmet")
        if gid in excepted and LANDED.search(heading) and gid not in unmet:
            problems.append(
                f"{name}: \"{heading}\" excepts {gid} from what it says landed, "
                "and the header's unmet lists do not name it")
        if claims_landed and gid in unmet:
            problems.append(
                f"{name}: {gid} is grouped under \"{heading}\" and named in this "
                "file's own header as not satisfied")
        if claims_landed and gid in outstanding:
            problems.append(
                f"{name}: {gid} is grouped under \"{heading}\" but the roadmap "
                "still lists it under what has to close before v2.0 can ship")
    return problems


def unclassified(reqs, manifests) -> list[str]:
    """Every *(Open)* requirement has to be named somewhere a reader looks."""
    classified: set[str] = set()
    if ROADMAP.is_file():
        classified |= set(REQ_CITE.findall(ROADMAP.read_text(encoding="utf-8")))
    for manifest in manifests:
        text = manifest.read_text(encoding="utf-8")
        classified |= set(REQ_CITE.findall(text))
        for pre, lo, hi in RANGE.findall(text):
            classified.update(f"{pre}-R{n}" for n in range(int(lo), int(hi) + 1))
    return [f"{rid} is marked *(Open)* in {page} and is named in neither the "
            "roadmap nor any version manifest: nothing schedules it and nothing "
            "has declined it"
            for rid, (page, is_open) in sorted(reqs.items())
            if is_open and rid not in classified]


def main() -> int:
    reqs = requirements()
    outstanding = roadmap_outstanding()
    problems: list[str] = []
    in_flight: list[str] = []
    manifests = sorted(p for p in VERSIONS.glob("*.toml") if p.name != "TEMPLATE.toml")
    for manifest in manifests:
        problems += check(manifest, reqs, in_flight, outstanding)
    problems += unclassified(reqs, manifests)
    if len(in_flight) > 1:
        problems.append(f"{len(in_flight)} versions staged or releasable at once "
                        f"({', '.join(in_flight)}); the train is serial (OPS-R15)")
    if problems:
        for m in problems:
            print(f"::error::{m}")
        print(f"\n{len(problems)} manifest problem(s).")
        return 1
    goals = sum(len(tomllib.loads(m.read_text(encoding='utf-8')).get("goals", []))
                for m in manifests)
    print(f"version manifests: clean ({len(manifests)} manifest(s), {goals} goals)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
