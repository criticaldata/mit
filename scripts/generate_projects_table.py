#!/usr/bin/env python3
"""
Generate a projects summary table from data/projects/*/project.yaml.
Run from the repo root. Prints Markdown to stdout.
"""

import sys
import io
import yaml
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

PROJECTS_DIR = Path("data/projects")
PEOPLE_DIR   = Path("data/people")

STATUS_ORDER = ["active", "on-hold", "completed", "archived"]
STATUS_LABELS = {
    "active":    "Active",
    "on-hold":   "On Hold",
    "completed": "Completed",
    "archived":  "Archived",
}


def load_projects():
    by_status = {s: [] for s in STATUS_ORDER}
    for yaml_file in sorted(PROJECTS_DIR.glob("*/project.yaml")):
        with open(yaml_file, encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                print(f"YAML error in {yaml_file}: {e}", file=sys.stderr)
                continue
        if not data or not data.get("title"):
            continue
        data["_slug"] = yaml_file.parent.name
        status = data.get("status", "")
        if status in by_status:
            by_status[status].append(data)
    return by_status


def resolve_lead(slug):
    if not slug:
        return ""
    person_file = PEOPLE_DIR / slug / "person.yaml"
    if person_file.exists():
        with open(person_file, encoding="utf-8") as f:
            p = yaml.safe_load(f) or {}
        name = p.get("name", slug)
        return f"[{name}](../people/{slug}/)"
    return slug


def tags_cell(tags):
    if not tags:
        return ""
    return ", ".join(f"`{t}`" for t in tags)


def projects_table(projects):
    rows = ["| Project | Lead | Tags | GitHub |", "|---|---|---|---|"]
    for p in projects:
        slug = p["_slug"]
        title = f"[{p['title']}]({slug}/project.yaml)"
        lead  = resolve_lead(p.get("lead"))
        tags  = tags_cell(p.get("tags") or [])
        repo  = p.get("github_repo", "")
        if repo:
            repo = f"[repo]({repo})"
        rows.append(f"| {title} | {lead} | {tags} | {repo} |")
    return "\n".join(rows)


def main():
    if not PROJECTS_DIR.exists():
        sys.exit(f"Directory not found: {PROJECTS_DIR}. Run from the repo root.")

    by_status = load_projects()
    total = sum(len(v) for v in by_status.values())

    print("# Projects\n")
    for status in STATUS_ORDER:
        projects = by_status[status]
        if not projects:
            continue
        label = STATUS_LABELS[status]
        table = projects_table(projects)
        if status == "active":
            print(f"## {label} ({len(projects)})\n")
            print(table)
            print()
        else:
            print(f"<details>\n<summary><strong>{label} ({len(projects)})</strong></summary>\n")
            print(table)
            print("\n</details>\n")

    print(f"---\n_Generated from `data/projects/` — {total} records total._")


if __name__ == "__main__":
    main()
