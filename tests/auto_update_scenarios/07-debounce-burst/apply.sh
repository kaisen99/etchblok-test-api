#!/usr/bin/env bash
# Push 3 small commits within 90 seconds. The 5-minute debounce should
# collapse them into a single workflow run that produces ONE PR with
# the combined diff. Exercises: debounce behavior + burst handling.
#
# Each commit touches a different model's docstring so we can verify
# all three changes show up in the combined PR.
#
# Unlike the other scenarios, this one commits + pushes itself rather
# than letting run-all.sh do it (we need 3 separate pushes).

set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

python3 <<'PY'
from pathlib import Path

# Each tuple: (file, old docstring fragment, new docstring fragment)
edits = [
    (
        "app/models/bookmark.py",
        "class Bookmark:\n",
        "class Bookmark:\n    # NOTE: bookmarks own their tag list directly; deletion of a tag must\n    # remove it from every bookmark referencing it.\n",
    ),
    (
        "app/models/collection.py",
        "class Collection:\n",
        "class Collection:\n    # NOTE: collections are ordered — bookmark IDs preserve insertion order.\n",
    ),
    (
        "app/models/tag.py",
        "class Tag:\n",
        "class Tag:\n    # NOTE: tag colors are an enum-backed string field; see TagColor.\n",
    ),
]

# Stage each edit + commit + push, with sleeps to land them inside the
# debounce window. Three commits in ~90s total.
import subprocess, time, sys

def run(cmd, check=True):
    r = subprocess.run(cmd, check=check, text=True, capture_output=True)
    if r.returncode != 0 and check:
        sys.stderr.write(r.stderr)
        sys.exit(r.returncode)
    return r

for i, (path, old, new) in enumerate(edits, 1):
    p = Path(path)
    content = p.read_text()
    if old not in content:
        print(f"WARN: {path}: anchor '{old.strip()[:40]}…' not found, skipping")
        continue
    if new in content:
        print(f"WARN: {path}: edit already applied, skipping")
        continue
    p.write_text(content.replace(old, new, 1))

    run(["git", "add", path])
    msg = f"docs: clarify {Path(path).stem} invariant (burst {i}/3)"
    run(["git", "commit", "-m", msg])
    run(["git", "push", "origin", "main"])
    print(f"burst commit {i}/3 pushed: {msg}")

    if i < len(edits):
        # Spread commits across ~90s. 30s gap keeps us inside debounce.
        time.sleep(30)

print("07-debounce-burst: 3 commits pushed inside the debounce window")
PY
