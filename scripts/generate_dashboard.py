#!/usr/bin/env python3
"""
Generate DASHBOARD.md — weekly lab meeting dashboard.

Covers three record types: projects, funding, events.
Each type has its own section with the same tier system:

  🔴 Urgent    — most recent update has priority: urgent
  🟡 Blocked   — current state is type: blocked (cleared by type: resolved)
  🟢 This week — last update within 7 days
  ⚪ Stale     — no update in 7+ days; 14+ days flagged more strongly
  🗄️ Archived  — inactive status, or past events

Inactive statuses by type:
  projects  → completed, on-hold, archived
  funding   → rejected, withdrawn
  events    → completed, cancelled, OR event date has passed
"""

import re
from datetime import date
from pathlib import Path

import yaml

PROJECTS_DIR = Path("data/projects")
FUNDING_DIR  = Path("data/funding")
EVENTS_DIR   = Path("data/events")
OUTPUT       = Path("DASHBOARD.md")
TODAY        = date.today()
REPO_URL     = "https://github.com/criticaldata/mit"

PROJECT_INACTIVE = {"completed", "on-hold", "archived"}
FUNDING_INACTIVE = {"rejected", "withdrawn"}
EVENT_INACTIVE   = {"completed", "cancelled"}


# ── parsing ───────────────────────────────────────────────────────────────────

def parse_update(path):
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


def as_date(val):
    """Coerce a yaml value (already a date, or a string) to date, or None."""
    if val is None:
        return None
    if isinstance(val, date):
        return val
    try:
        return date.fromisoformat(str(val))
    except ValueError:
        return None


def load_updates(record_dir):
    updates_dir = record_dir / "updates"
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
    return updates


# ── loaders ───────────────────────────────────────────────────────────────────

def load_projects():
    records = []
    for d in sorted(PROJECTS_DIR.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        yaml_path = d / "project.yaml"
        if not yaml_path.exists():
            continue
        data = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
        data["_slug"] = d.name
        data["_url"]  = f"{REPO_URL}/tree/main/data/projects/{d.name}"
        data["_type"] = "project"
        data["updates"] = load_updates(d)
        records.append(data)
    return records


def load_funding():
    records = []
    for d in sorted(FUNDING_DIR.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        yaml_path = d / "funding.yaml"
        if not yaml_path.exists():
            continue
        data = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
        data["_slug"] = d.name
        data["_url"]  = f"{REPO_URL}/tree/main/data/funding/{d.name}"
        data["_type"] = "funding"
        data["updates"] = load_updates(d)
        records.append(data)
    return records


def load_events():
    records = []
    for year_dir in sorted(EVENTS_DIR.iterdir()):
        if not year_dir.is_dir() or year_dir.name.startswith("."):
            continue
        for d in sorted(year_dir.iterdir()):
            if not d.is_dir() or d.name.startswith("."):
                continue
            yaml_path = d / "event.yaml"
            if not yaml_path.exists():
                continue
            data = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
            data["_slug"] = d.name
            data["_year"] = year_dir.name
            data["_url"]  = f"{REPO_URL}/tree/main/data/events/{year_dir.name}/{d.name}"
            data["_type"] = "event"
            data["updates"] = load_updates(d)
            records.append(data)
    return records


# ── classification ────────────────────────────────────────────────────────────

def blocked_update(record):
    for u in record["updates"]:
        t = u["fm"].get("type", "")
        if t == "blocked":
            return u
        if t == "resolved":
            return None
    return None


def event_is_past(record):
    """True if the event's end date (or start date) has already passed."""
    end   = as_date(record.get("date_end"))
    start = as_date(record.get("date_start"))
    if end:
        return end < TODAY
    if start:
        return start < TODAY
    return False  # undated — not past


def classify(record, inactive_statuses):
    status = record.get("status", "")

    if status in inactive_statuses:
        return "inactive"
    if record["_type"] == "event" and event_is_past(record):
        return "inactive"

    updates = record["updates"]
    latest  = updates[0] if updates else None

    if latest and latest["fm"].get("priority") == "urgent":
        return "urgent"
    if blocked_update(record):
        return "blocked"
    if latest and (TODAY - latest["date"]).days <= 7:
        return "this_week"
    return "stale"


# ── rendering ─────────────────────────────────────────────────────────────────

def age_str(record, flag_stale=True):
    updates = record["updates"]
    if not updates:
        return "⚠️ **No updates yet**" if flag_stale else "—"
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


def full_card(record):
    title    = record.get("title") or record["_slug"]
    url      = record["_url"]
    age      = age_str(record)
    updates  = record["updates"]

    lines = [f"### [{title}]({url})"]

    # Event date hint
    if record["_type"] == "event":
        start = as_date(record.get("date_start"))
        if start:
            days_until = (start - TODAY).days
            if days_until == 0:
                hint = "today"
            elif days_until > 0:
                hint = f"in {days_until}d ({start})"
            else:
                hint = str(start)
            lines.append(f"_📅 {hint} · {age}_")
        else:
            lines.append(f"_📅 date TBD · {age}_")
    else:
        lines.append(f"_{age}_")

    blocking = blocked_update(record)
    if blocking:
        lines.append(f"\n> **Blocked since {blocking['date']}**")

    if updates and updates[0]["body"]:
        lines.append("")
        lines.append(updates[0]["body"])

    return "\n".join(lines)


def stale_row(record):
    title = record.get("title") or record["_slug"]
    url   = record["_url"]
    age   = age_str(record)

    if record["_type"] == "event":
        start = as_date(record.get("date_start"))
        date_col = str(start) if start else "TBD"
        return f"| [{title}]({url}) | {date_col} | {age} |"
    return f"| [{title}]({url}) | {age} |"


def inactive_item(record):
    title  = record.get("title") or record["_slug"]
    url    = record["_url"]
    status = record.get("status", "")
    if record["_type"] == "event":
        start = as_date(record.get("date_start"))
        extra = f" · {start}" if start else ""
        return f"- [{title}]({url}) _{status}{extra}_"
    return f"- [{title}]({url}) _{status}_"


def render_full_cards(records):
    return "\n\n".join(full_card(r) for r in records)


def render_stale_table(records):
    has_events = any(r["_type"] == "event" for r in records)
    if has_events:
        header = ["| Record | Date | Last update |", "|---|---|---|"]
    else:
        header = ["| Record | Last update |", "|---|---|"]
    rows = [stale_row(r) for r in records]
    return "\n".join(header + rows)


def render_inactive_list(records):
    return "\n".join(inactive_item(r) for r in records)


def render_section(emoji, label, records, renderer, empty_msg):
    if not records:
        return f"### {emoji} {label} (0)\n\n_{empty_msg}_"
    lines = [f"### {emoji} {label} ({len(records)})\n"]
    lines.append(renderer(records))
    return "\n".join(lines)


def render_domain(heading, records, inactive_statuses):
    if not records:
        return ""

    tiers = {k: [] for k in ("urgent", "blocked", "this_week", "stale", "inactive")}
    for r in records:
        tiers[classify(r, inactive_statuses)].append(r)

    # Sort each tier
    def by_latest_desc(r):
        u = r["updates"]
        return u[0]["date"] if u else date.min

    def by_title(r):
        return (r.get("title") or r["_slug"]).lower()

    def by_gap_desc(r):
        u = r["updates"]
        return (TODAY - u[0]["date"]).days if u else 9999

    def by_date_start_asc(r):
        d = as_date(r.get("date_start"))
        return d if d else date.max

    tiers["urgent"].sort(key=by_latest_desc, reverse=True)
    tiers["blocked"].sort(key=by_latest_desc, reverse=True)
    tiers["this_week"].sort(key=by_title)
    tiers["stale"].sort(key=by_gap_desc, reverse=True)
    tiers["inactive"].sort(key=by_date_start_asc if inactive_statuses == EVENT_INACTIVE else by_title)

    # For events, sort this_week and stale by date_start too
    if inactive_statuses == EVENT_INACTIVE:
        tiers["this_week"].sort(key=by_date_start_asc)
        tiers["stale"].sort(key=by_date_start_asc)

    inactive_count = len(tiers["inactive"])
    inactive_body  = (render_inactive_list(tiers["inactive"])
                      if tiers["inactive"] else "_None._")

    parts = [f"## {heading}\n"]
    parts.append(render_section("🔴", "Urgent",    tiers["urgent"],    render_full_cards, "No urgent items."))
    parts.append(render_section("🟡", "Blocked",   tiers["blocked"],   render_full_cards, "No blocked items."))
    parts.append(render_section("🟢", "This week", tiers["this_week"], render_full_cards, "No updates this week."))
    parts.append(render_section("⚪", "Stale",     tiers["stale"],     render_stale_table, "All up to date."))
    parts.append(
        f"<details>\n<summary>🗄️ Inactive ({inactive_count})</summary>\n\n"
        f"{inactive_body}\n\n</details>"
    )

    active = sum(len(tiers[k]) for k in ("urgent", "blocked", "this_week", "stale"))
    return "\n\n".join(parts), active, inactive_count


# ── main ──────────────────────────────────────────────────────────────────────

def generate():
    projects = load_projects()
    funding  = load_funding()
    events   = load_events()

    proj_md,  proj_active,  proj_inactive  = render_domain("Projects", projects, PROJECT_INACTIVE)
    fund_md,  fund_active,  fund_inactive  = render_domain("Funding",  funding,  FUNDING_INACTIVE)
    event_md, event_active, event_inactive = render_domain("Events",   events,   EVENT_INACTIVE)

    total = len(projects) + len(funding) + len(events)

    page = "\n\n---\n\n".join([
        f"# MIT Critical Data — Lab Dashboard\n\n"
        f"_Generated {TODAY.isoformat()} · "
        f"{len(projects)} projects · {len(funding)} grants · {len(events)} events · "
        f"[contributing guide](docs/contributing.md)_",
        proj_md,
        fund_md,
        event_md,
    ])

    OUTPUT.write_text(page + "\n", encoding="utf-8")
    print(f"Dashboard written -> {OUTPUT}  "
          f"({len(projects)} projects, {len(funding)} grants, {len(events)} events, "
          f"{total} total)")


if __name__ == "__main__":
    generate()
