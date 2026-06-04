#!/usr/bin/env python3
"""
Generate a summary README.md for each person in data/people/.
Each README lists all projects, events, funding, outputs, and talks
the person is involved in as lead or team member.

Run from the repo root:
    py scripts/generate_person_pages.py
"""

import io
import sys
import yaml
from pathlib import Path
from datetime import date, datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

PEOPLE_DIR  = Path("data/people")
PROJECTS_DIR = Path("data/projects")
EVENTS_DIR  = Path("data/events")
FUNDING_DIR = Path("data/funding")
OUTPUTS_DIR = Path("data/outputs")
TALKS_DIR   = Path("data/talks")


def load_yaml(path):
    with open(path, encoding="utf-8") as f:
        try:
            return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            print(f"YAML error in {path}: {e}", file=sys.stderr)
            return {}


def leads(record):
    """Return lead slug(s); supports `leads` list or single `lead` string."""
    if record.get("leads"):
        return [s for s in record["leads"] if s]
    lead = record.get("lead")
    return [lead] if lead else []


def members(record):
    """Return set of slugs involved in a record (leads + team)."""
    involved = set(leads(record))
    for m in record.get("team") or []:
        if m:
            involved.add(m)
    return involved


def role(record, slug):
    return "Lead" if slug in leads(record) else "Team"


# ── loaders ──────────────────────────────────────────────────────────────────

def load_projects():
    rows = []
    for f in sorted(PROJECTS_DIR.glob("*/project.yaml")):
        d = load_yaml(f)
        if not d.get("title"):
            continue
        d["_slug"] = f.parent.name
        d["_path"] = f"../../projects/{f.parent.name}/project.yaml"
        rows.append(d)
    return rows


def load_events():
    rows = []
    for f in sorted(EVENTS_DIR.glob("*/*/event.yaml")):
        d = load_yaml(f)
        if not d.get("title"):
            continue
        year = f.parent.parent.name
        slug = f.parent.name
        d["_slug"] = slug
        d["_year"] = year
        d["_path"] = f"../../events/{year}/{slug}/event.yaml"
        rows.append(d)
    return rows


def load_funding():
    rows = []
    for f in sorted(FUNDING_DIR.glob("*/funding.yaml")):
        d = load_yaml(f)
        if not d:
            continue
        d["_slug"] = f.parent.name
        d["_path"] = f"../../funding/{f.parent.name}/funding.yaml"
        rows.append(d)
    return rows


def load_outputs():
    rows = []
    for f in sorted(OUTPUTS_DIR.glob("*/output.yaml")):
        d = load_yaml(f)
        if not d.get("title"):
            continue
        d["_slug"] = f.parent.name
        d["_path"] = f"../../outputs/{f.parent.name}/output.yaml"
        rows.append(d)
    return rows


def load_talks():
    rows = []
    for f in sorted(TALKS_DIR.glob("*/*.yaml")):
        d = load_yaml(f)
        if not d.get("title"):
            continue
        d["_file"] = f.name
        d["_year"] = f.parent.name
        d["_path"] = f"../../talks/{f.parent.name}/{f.name}"
        rows.append(d)
    return rows


# ── markdown helpers ──────────────────────────────────────────────────────────

def fmt_date(val):
    if not val:
        return ""
    if isinstance(val, (date, datetime)):
        return val.strftime("%d %b %Y") if isinstance(val, date) else val.date().strftime("%d %b %Y")
    try:
        return datetime.strptime(str(val), "%Y-%m-%d").strftime("%d %b %Y")
    except ValueError:
        return str(val)


def projects_section(records, slug):
    lines = ["## Projects\n",
             "| Project | Role | Status |",
             "|---|---|---|"]
    for r in records:
        title = f"[{r['title']}]({r['_path']})"
        lines.append(f"| {title} | {role(r, slug)} | {r.get('status', '')} |")
    return "\n".join(lines)


def events_section(records, slug):
    lines = ["## Events\n",
             "| Event | Date | Role | Status |",
             "|---|---|---|---|"]
    for r in records:
        title = f"[{r['title']}]({r['_path']})"
        d = fmt_date(r.get("date_start"))
        lines.append(f"| {title} | {d} | {role(r, slug)} | {r.get('status', '')} |")
    return "\n".join(lines)


def funding_section(records, slug):
    lines = ["## Funding\n",
             "| Fund | Agency | Role | Status |",
             "|---|---|---|---|"]
    for r in records:
        name = r.get("title") or r["_slug"]
        title = f"[{name}]({r['_path']})"
        lines.append(f"| {title} | {r.get('agency') or ''} | {role(r, slug)} | {r.get('status', '')} |")
    return "\n".join(lines)


def outputs_section(records, slug):
    lines = ["## Outputs\n",
             "| Output | Type | Role | Status |",
             "|---|---|---|---|"]
    for r in records:
        title = f"[{r['title']}]({r['_path']})"
        lines.append(f"| {title} | {r.get('type', '')} | {role(r, slug)} | {r.get('status', '')} |")
    return "\n".join(lines)


def talks_section(records):
    lines = ["## Talks\n",
             "| Talk | Date | Status |",
             "|---|---|---|"]
    for r in records:
        title = r["title"]
        if r.get("slides_url"):
            title = f"[{title}]({r['slides_url']})"
        elif r.get("recording_url"):
            title = f"[{title}]({r['recording_url']})"
        else:
            title = f"[{title}]({r['_path']})"
        d = fmt_date(r.get("date"))
        lines.append(f"| {title} | {d} | {r.get('status', '')} |")
    return "\n".join(lines)


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    projects = load_projects()
    events   = load_events()
    funding  = load_funding()
    outputs  = load_outputs()
    talks    = load_talks()

    generated = 0

    for person_dir in sorted(PEOPLE_DIR.iterdir()):
        if not person_dir.is_dir():
            continue
        person_file = person_dir / "person.yaml"
        if not person_file.exists():
            continue
        p = load_yaml(person_file)
        if not p.get("name"):
            continue

        slug = person_dir.name

        p_projects = [r for r in projects if slug in members(r)]
        p_events   = [r for r in events   if slug in members(r)]
        p_funding  = [r for r in funding  if slug in members(r)]
        p_outputs  = [r for r in outputs  if slug in members(r)]
        p_talks    = [r for r in talks    if r.get("speaker_link") == slug]

        sections = []

        if p_projects:
            sections.append(projects_section(p_projects, slug))
        if p_events:
            sections.append(events_section(p_events, slug))
        if p_funding:
            sections.append(funding_section(p_funding, slug))
        if p_outputs:
            sections.append(outputs_section(p_outputs, slug))
        if p_talks:
            sections.append(talks_section(p_talks))

        name = p["name"]
        role_str  = p.get("role", "")
        status_str = p.get("status", "")
        inst  = p.get("institution", "")
        header_parts = [x for x in [role_str, status_str, inst] if x]

        readme = f"# {name}\n\n"
        if header_parts:
            readme += f"_{' · '.join(header_parts)}_\n\n"
        if sections:
            readme += "\n\n".join(sections)
        else:
            readme += "_No linked records found._"
        readme += f"\n\n---\n_Generated from lab records._\n"

        out_path = person_dir / "README.md"
        out_path.write_text(readme, encoding="utf-8")
        generated += 1

    print(f"Generated {generated} person README files.")


if __name__ == "__main__":
    main()
