#!/usr/bin/env python3
"""Spec-side integrity checks. Run in CI on the spec repo itself (GOV-R11).

Verifies:
  - every cited requirement/ADR identifier resolves to a definition, in the
    Markdown tree and in the shared workflow definitions
  - no requirement ID is defined twice (IDs are permanent and unique, GOV-R8)
  - every internal Markdown link resolves to a real file
  - every internal link's #fragment resolves to a heading in the target file
    (REPO-R55)

Scope of the fragment check: relative links between Markdown files in this
repository, and same-file anchors. It does not follow an absolute URL, so a
link into another repository's rendered pages is checked by lychee for the
page and by nobody for the anchor. It reads headings, not rendered HTML, so a
hand-written HTML anchor would not be found; none exist here.

Exit 0 = clean, 1 = problems found.
"""
from __future__ import annotations
import re, sys, pathlib, collections, functools

ROOT = pathlib.Path(__file__).resolve().parent.parent

REQ_DEF = re.compile(r"^\|\s*\*\*([A-Z]+\d*-R\d+)\*\*\s*\|", re.M)
REQ_CITE = re.compile(r"\b([A-Z]+\d*-R\d+)\b")
ADR_FILE = re.compile(r"^0*(\d{3,4})-.*\.md$")
ADR_CITE = re.compile(r"\bADR-(\d{3,4})\b")
LINK = re.compile(r"\[[^\]]*\]\((?!https?://|mailto:)([^)#]+)(?:#[^)]*)?\)")
# The same links, keeping the half LINK throws away. An empty first group is a
# same-file anchor.
LINK_FRAG = re.compile(r"\[[^\]]*\]\((?!https?://|mailto:)([^)#]*)#([^)]+)\)")
FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})(.*)$")
HEADING = re.compile(r"^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$")


def md_files():
    return [p for p in ROOT.rglob("*.md") if ".git" not in p.parts]


def citing_files():
    """Everything that may carry a citation. Workflow headers cite identifiers
    as freely as the prose does, and nothing read them: two invented ids and a
    third that had drifted sat there from the founding commit onwards.

    The gate scripts are the same class of file and were the same blind spot.
    Six invented identifiers sat in them, one of which check_stageable.py
    printed into the build's own error message — the script whose job is
    refusing a manifest that cites an identifier the spec does not define."""
    return (md_files()
            + sorted((ROOT / ".github" / "workflows").glob("*.yml"))
            + sorted((ROOT / "scripts").glob("*.py")))


def defined_reqs():
    defined = collections.Counter()
    for p in md_files():
        for m in REQ_DEF.findall(p.read_text(encoding="utf-8")):
            defined[m] += 1
    return defined


def defined_adrs():
    dec = ROOT / "00-overview" / "decisions"
    adrs = set()
    if dec.is_dir():
        for f in dec.iterdir():
            m = ADR_FILE.match(f.name)
            if m:
                adrs.add(int(m.group(1)))
    return adrs


def undefined_citations(defset, adrs):
    problems = []
    for p in citing_files():
        text = p.read_text(encoding="utf-8")
        # One line per file, naming every distinct stray it carries. Reporting
        # only the first hid a sibling in two of the four files that had one,
        # so a fix guided by the output left the file still failing.
        stray = sorted({r for r in REQ_CITE.findall(text) if r not in defset})
        if stray:
            problems.append(f"{p.relative_to(ROOT)}: cites undefined {', '.join(stray)}")
        stray_adrs = sorted({int(a) for a in ADR_CITE.findall(text) if int(a) not in adrs})
        if stray_adrs:
            named = ", ".join(f"ADR-{a:04d}" for a in stray_adrs)
            problems.append(f"{p.relative_to(ROOT)}: cites undefined {named}")
    return problems


def check_ids():
    defined = defined_reqs()
    problems = [f"duplicate requirement id defined {n}x: {i}"
                for i, n in sorted(defined.items()) if n > 1]
    problems += undefined_citations(set(defined), defined_adrs())
    return problems


def check_links():
    problems = []
    for p in md_files():
        for target in LINK.findall(p.read_text(encoding="utf-8")):
            target = target.strip()
            if not target or target.startswith(".docs/") or "/.docs/" in target:
                continue  # repo-local .docs live in cli, not here
            resolved = (p.parent / target).resolve()
            if not resolved.exists():
                problems.append(f"{p.relative_to(ROOT)}: broken link -> {target}")
    return problems


def heading_slug(raw: str) -> str:
    """The anchor a rendered heading gets. Matches GitHub's slugger, which is
    what the links in this tree are written against: inline markup is rendered
    away first, then everything but word characters, spaces and hyphens is
    dropped, then spaces become hyphens."""
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", raw)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\[[^\]]*\]", r"\1", text)
    text = text.replace("`", "").replace("*", "").strip().lower()
    return re.sub(r"\s", "-", re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE))


@functools.lru_cache(maxsize=None)
def anchors(path: str) -> frozenset[str]:
    """Every anchor a Markdown file offers. Fenced blocks are skipped: this
    tree fences shell transcripts and directory listings whose lines start with
    `#`, and counting those as headings would make a real dangling fragment
    pass. Two headings slugging the same take `-1`, `-2` in document order, as
    they do when the page is rendered."""
    found, seen, fence = set(), collections.Counter(), None
    for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        marker = FENCE.match(line)
        if marker:
            mark, info = marker.group(1), marker.group(2)
            if fence is None:
                fence = mark
            elif mark[0] == fence[0] and len(mark) >= len(fence) and not info.strip():
                fence = None
            continue
        if fence is not None:
            continue
        head = HEADING.match(line)
        if head:
            slug = heading_slug(head.group(1))
            seen[slug] += 1
            found.add(slug if seen[slug] == 1 else f"{slug}-{seen[slug] - 1}")
    return frozenset(found)


def check_fragments():
    """A link whose file half resolves and whose #fragment does not is the one
    breakage nothing here caught: two links to a heading that had moved to
    another file sat in the tree from the founding commit. check_links() reads
    the file half and drops the fragment; lychee is run without fragment
    checking; markdownlint's MD051 sees same-file anchors only, which is the
    half that was never broken (REPO-R55)."""
    problems = []
    for p in md_files():
        for rel, frag in LINK_FRAG.findall(p.read_text(encoding="utf-8")):
            rel, frag = rel.strip(), frag.strip()
            if rel.startswith(".docs/") or "/.docs/" in rel:
                continue
            target = p if not rel else (p.parent / rel).resolve()
            # A broken file half is check_links()' report to make, not this one's.
            if target.suffix.lower() != ".md" or not target.exists():
                continue
            if frag not in anchors(str(target)):
                where = rel or p.name
                problems.append(
                    f"{p.relative_to(ROOT)}: no heading '#{frag}' in {where}")
    return problems


def main() -> int:
    problems = []
    # De-dup the "cites undefined" one-per-file noise into unique messages.
    seen = set()
    for msg in check_ids() + check_links() + check_fragments():
        if msg not in seen:
            seen.add(msg)
            problems.append(msg)
    if problems:
        for m in problems:
            print(f"::error::{m}")
        print(f"\n{len(problems)} integrity problem(s).")
        return 1
    print("spec integrity: clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
