#!/usr/bin/env python3
"""
One-shot migration: nest events and talks under year subdirectories.

  data/events/<slug>/         -> data/events/<year>/<slug-without-trailing-year>/
  data/talks/YYYY-MM-DD-*.yaml -> data/talks/<year>/YYYY-MM-DD-*.yaml

Events with no date_start and no year in slug go to data/events/undated/.
Trailing -YYYY suffix is stripped from event slugs when YYYY == the event year.

Usage:
    py scripts/migrate_year_dirs.py           # dry run (safe)
    py scripts/migrate_year_dirs.py --execute # apply changes
"""
import re
import shutil
import sys
from pathlib import Path

import yaml

DRY = "--execute" not in sys.argv
if DRY:
    print("Dry run — pass --execute to apply.\n")

EVENTS = Path("data/events")
TALKS  = Path("data/talks")


def year_from_slug(slug):
    m = re.search(r'(\d{4})', slug)
    return m.group(1) if m else None


def strip_trailing_year(slug, year):
    """Remove a trailing -YYYY suffix if YYYY matches the event year."""
    pattern = rf'-{year}$'
    return re.sub(pattern, '', slug)


# ── events ────────────────────────────────────────────────────────────────────

print("=== EVENTS ===")
conflicts = {}
moves = []

for folder in sorted(EVENTS.iterdir()):
    if not folder.is_dir() or folder.name == "updates":
        continue

    yaml_path = folder / "event.yaml"
    year = None

    if yaml_path.exists():
        with open(yaml_path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        date_start = str(data.get("date_start", ""))
        m = re.match(r'(\d{4})', date_start)
        if m:
            year = m.group(1)

    if not year:
        year = year_from_slug(folder.name) or "undated"

    new_slug = strip_trailing_year(folder.name, year)
    dest = EVENTS / year / new_slug

    moves.append((folder, dest))

    tag = "" if folder.name == new_slug else f"  (slug: {folder.name} -> {new_slug})"
    print(f"  {folder.name} -> {year}/{new_slug}{tag}")

    key = (year, new_slug)
    conflicts.setdefault(key, []).append(folder.name)

bad = {k: v for k, v in conflicts.items() if len(v) > 1}
if bad:
    print("\nCONFLICT — two slugs would collide after rename:")
    for (yr, slug), sources in bad.items():
        print(f"  {yr}/{slug} <- {sources}")
    sys.exit("Fix conflicts before running with --execute.")

if not DRY:
    for src, dst in moves:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
    print(f"\nMoved {len(moves)} event folders.")
else:
    print(f"\n{len(moves)} event folders would be moved.")


# ── talks ─────────────────────────────────────────────────────────────────────

print("\n=== TALKS ===")
talk_moves = []

for f in sorted(TALKS.iterdir()):
    if f.suffix != ".yaml":
        continue
    m = re.match(r'(\d{4})-', f.name)
    if not m:
        print(f"  SKIP (no date prefix): {f.name}")
        continue
    year = m.group(1)
    dest = TALKS / year / f.name
    talk_moves.append((f, dest))
    print(f"  {f.name} -> {year}/{f.name}")

if not DRY:
    for src, dst in talk_moves:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
    print(f"\nMoved {len(talk_moves)} talk files.")
else:
    print(f"\n{len(talk_moves)} talk files would be moved.")
