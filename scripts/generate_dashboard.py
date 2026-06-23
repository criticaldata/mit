#!/usr/bin/env python3
"""
Generate DASHBOARD.md — weekly lab meeting dashboard.

Tiers (display order):
  🔴 Urgent    — most recent update has priority: urgent
  🟡 Blocked   — current state is type: blocked (cleared by type: resolved)
  🟢 This week — last update within 7 days (not urgent or blocked)
  ⚪ Stale     — no update in the past 7 days; 14+ days gets a visual flag
  🗄️ Archived  — project status in {completed, on-hold, archived}

Update frontmatter fields recognised:
  priority: urgent          # promotes to 🔴 tier
  type: weekly|adhoc|blocked|resolved
"""

import re
from datetime import date
from pathlib import Path

import yaml

PROJECTS_DIR = Path("data/projects")
OUTPUT = Path("DASHBOARD.md")
TODAY = date.today()

INACTIVE_STATUSES = {"completed", "on-hold", "archived"}
REPO_URL = "https://github.com/criticaldata/mit"


# ── parsing ───────────────────────────────────────────────────────────────────

def parse_update(path):
    """Return (frontmatter_dict, body_str) from a Markdown update file."""
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1]) or {}
            return fm, parts[2].strip()
    return {}, text.strip()


def update_date_from_name(path):
    m = re.match(r"(\d{4}-\d{2}-\d{2})", path.stem)
    if m:
        try:
            return date.fromisoformat(m.group(1))
        except ValueError:
            pass
    return None


def load_project(slug):
    yaml_path = PROJECTS_DIR / slug / "project.yaml"
    if not yaml_path.exists():
        return None

    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
    data["slug"] = slug

    updates_dir = PROJECTS_DIR / slug / "updates"
    updates = []
    if updates_dir.exists():
        for p in sorted(updates_dir.iterdir()):
            if p.name == ".gitkeep" or p.suffix != ".md":
                continue
            d = update_date_from_name(p)
            if d is None:
                continue
            fm, body = parse_update(p)
            updates.append({"date": d, "fm": fm, "body": body})

    updates.sort(key=lambda u: u["date"], reverse=True)
    data["updates"] = updates
    return data


# ── classification ────────────────────────────────────────────────────────────

def blocked_update(project):
    for u in project["updates"]:
        t = u["fm"].get("type", "")
        if t == "blocked":
            return u
        if t == "resolved":
            return None
    return None


def classify(project):
    if project.get("status", "active") in INACTIVE_STATUSES:
        return "inactive"

    updates = project["updates"]
    latest = updates[0] if updates else None

    if latest and latest["fm"].get("priority") == "urgent":
        return "urgent"

    if blocked_update(project):
        return "blocked"

    if latest and (TODAY - latest["date"]).days <= 7:
        return "this_week"

    return "stale"


# ── rendering ─────────────────────────────────────────────────────────────────

def project_url(slug):
    return f"{REPO_URL}/tree/main/data/projects/{slug}"


def age_str(project, flag_stale=True):
    updates = project["updates"]
    if not updates:
        return "⚠️ **No updates yet**" if flag_stale else "no updates"
    days = (TODAY - updates[0]["date"]).days
    if days == 0:
        return "updated today"
    if days == 1:
        return "updated 1d ago"
    if days <= 7:
        return f"updated {days}d ago"
    if days >= 14 and flag_stale:
        return f"⚠️ **{days}d since last update**"
    return f"{days}d ago"


def full_card(project):
    """Render a project as a full card with update body (for urgent/blocked/this-week)."""
    slug = project["slug"]
    title = project.get("title") or slug
    url = project_url(slug)
    age = age_str(project)

    lines = [f"### [{title}]({url})"]
    lines.append(f"_{age}_")

    blocking = blocked_update(project)
    if blocking:
        lines.append(f"\n> **Blocked since {blocking['date']}**")

    updates = project["updates"]
    if updates and updates[0]["body"]:
        lines.append("")
        lines.append(updates[0]["body"])

    return "\n".join(lines)


def stale_row(project):
    slug = project["slug"]
    title = project.get("title") or slug
    url = project_url(slug)
    age = age_str(project)
    return f"| [{title}]({url}) | {age} |"


def inactive_item(project):
    slug = project["slug"]
    title = project.get("title") or slug
    url = project_url(slug)
    status = project.get("status", "")
    return f"- [{title}]({url}) _{status}_"


def render_tier(emoji, label, projects, renderer):
    if not projects:
        return ""
    lines = [f"## {emoji} {label} ({len(projects)})\n"]
    lines.append(renderer(projects))
    lines.append("\n---")
    return "\n".join(lines)


def render_full_cards(projects):
    return "\n\n".join(full_card(p) for p in projects)


def render_stale_table(projects):
    rows = ["| Project | Last update |", "|---|---|"]
    rows += [stale_row(p) for p in projects]
    return "\n".join(rows)


def render_inactive_list(projects):
    return "\n".join(inactive_item(p) for p in projects)


# ── main ──────────────────────────────────────────────────────────────────────

def generate():
    slugs = sorted(
        d.name for d in PROJECTS_DIR.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )
    projects = [p for s in slugs if (p := load_project(s)) is not None]

    tiers = {k: [] for k in ("urgent", "blocked", "this_week", "stale", "inactive")}
    for p in projects:
        tiers[classify(p)].append(p)

    def by_latest_desc(p):
        u = p["updates"]
        return u[0]["date"] if u else date.min

    def by_title(p):
        return (p.get("title") or p["slug"]).lower()

    def by_gap_desc(p):
        u = p["updates"]
        return (TODAY - u[0]["date"]).days if u else 9999

    tiers["urgent"].sort(key=by_latest_desc, reverse=True)
    tiers["blocked"].sort(key=by_latest_desc, reverse=True)
    tiers["this_week"].sort(key=by_title)
    tiers["stale"].sort(key=by_gap_desc, reverse=True)
    tiers["inactive"].sort(key=by_title)

    sections = [
        f"# MIT Critical Data — Lab Dashboard\n",
        f"_Generated {TODAY.isoformat()} · {len(projects)} projects · "
        f"[contributing guide](docs/contributing.md)_\n",
        "---",
    ]

    sections.append(render_tier("🔴", "Urgent", tiers["urgent"], render_full_cards)
                    or "## 🔴 Urgent (0)\n\n_No urgent items._\n\n---")

    sections.append(render_tier("🟡", "Blocked", tiers["blocked"], render_full_cards)
                    or "## 🟡 Blocked (0)\n\n_No blocked projects._\n\n---")

    sections.append(render_tier("🟢", "This week", tiers["this_week"], render_full_cards)
                    or "## 🟢 This week (0)\n\n_No updates this week._\n\n---")

    sections.append(render_tier("⚪", "Stale", tiers["stale"], render_stale_table)
                    or "## ⚪ Stale (0)\n\n_All projects up to date._\n\n---")

    inactive_count = len(tiers["inactive"])
    inactive_body = (render_inactive_list(tiers["inactive"])
                     if tiers["inactive"] else "_No archived projects._")
    sections.append(
        f"<details>\n<summary>🗄️ Archived / Inactive ({inactive_count})</summary>\n\n"
        f"{inactive_body}\n\n</details>"
    )

    OUTPUT.write_text("\n\n".join(sections) + "\n", encoding="utf-8")
    print(f"Dashboard written -> {OUTPUT}  ({len(projects)} projects, "
          f"{len(tiers['urgent'])} urgent, {len(tiers['blocked'])} blocked, "
          f"{len(tiers['this_week'])} this week, {len(tiers['stale'])} stale, "
          f"{len(tiers['inactive'])} inactive)")


if __name__ == "__main__":
    generate()
