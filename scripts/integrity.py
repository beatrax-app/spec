#!/usr/bin/env python3
"""Spec-side integrity checks. Run in CI on the spec repo itself (GOV-R11).

Verifies:
  - every cited requirement/ADR identifier resolves to a definition, in the
    Markdown tree and in the shared workflow definitions
  - no requirement ID is defined twice (IDs are permanent and unique, GOV-R8)
  - every internal Markdown link resolves to a real file

Exit 0 = clean, 1 = problems found.
"""
from __future__ import annotations
import re, sys, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent

REQ_DEF = re.compile(r"^\|\s*\*\*([A-Z]+\d*-R\d+)\*\*\s*\|", re.M)
REQ_CITE = re.compile(r"\b([A-Z]+\d*-R\d+)\b")
ADR_FILE = re.compile(r"^0*(\d{3,4})-.*\.md$")
ADR_CITE = re.compile(r"\bADR-(\d{3,4})\b")
LINK = re.compile(r"\[[^\]]*\]\((?!https?://|mailto:)([^)#]+)(?:#[^)]*)?\)")


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


def main() -> int:
    problems = []
    # De-dup the "cites undefined" one-per-file noise into unique messages.
    seen = set()
    for msg in check_ids() + check_links():
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
