#!/usr/bin/env python3
"""
Generate DASHBOARD.md — weekly lab meeting dashboard.

All record types (projects, funding, events) flow into a single unified
tier list:

  🔴 Urgent    — most recent update has priority: urgent
  🟡 Blocked   — current state is type: blocked (cleared by type: resolved)
  🟢 This week — last update within 7 days (overrides inactive status)
  ⚪ Stale     — no update in 7+ days and not inactive; 14+ days flagged
  🗄️ Inactive  — no recent update AND inactive status/past event

Inactive statuses by type:
  projects → completed, on-hold, archived
  funding  → rejected, withdrawn
  events   → completed, cancelled, OR event date has passed
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

TYPE_LABEL = {"project": "Project", "funding": "Grant", "event": "Event"}


# ── parsing ───────────────────────────────────────────────────────────────────

def parse_update(path):
    text = path.read_text(encoding="utf-8-sig").lstrip()
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

    # Active projects — flat under data/projects/<slug>/
    for d in sorted(PROJECTS_DIR.iterdir()):
        if not d.is_dir() or d.name.startswith(".") or d.name == "archive":
            continue
        yp = d / "project.yaml"
        if not yp.exists():
            continue
        data = yaml.safe_load(yp.read_text(encoding="utf-8")) or {}
        data.update(_slug=d.name, _type="project",
                    _url=f"{REPO_URL}/tree/main/data/projects/{d.name}",
                    _inactive=PROJECT_INACTIVE,
                    updates=load_updates(d))
        records.append(data)

    # Archived projects — data/projects/archive/<year>/<slug>/
    archive_dir = PROJECTS_DIR / "archive"
    if archive_dir.exists():
        for year_dir in sorted(archive_dir.iterdir()):
            if not year_dir.is_dir() or year_dir.name.startswith("."):
                continue
            for d in sorted(year_dir.iterdir()):
                if not d.is_dir() or d.name.startswith("."):
                    continue
                yp = d / "project.yaml"
                if not yp.exists():
                    continue
                data = yaml.safe_load(yp.read_text(encoding="utf-8")) or {}
                rel_path = f"data/projects/archive/{year_dir.name}/{d.name}"
                data.update(_slug=d.name, _type="project",
                            _url=f"{REPO_URL}/tree/main/{rel_path}",
                            _inactive=PROJECT_INACTIVE,
                            updates=load_updates(d))
                records.append(data)

    return records


def load_funding():
    records = []
    for d in sorted(FUNDING_DIR.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        yp = d / "funding.yaml"
        if not yp.exists():
            continue
        data = yaml.safe_load(yp.read_text(encoding="utf-8")) or {}
        data.update(_slug=d.name, _type="funding",
                    _url=f"{REPO_URL}/tree/main/data/funding/{d.name}",
                    _inactive=FUNDING_INACTIVE,
                    updates=load_updates(d))
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
            yp = d / "event.yaml"
            if not yp.exists():
                continue
            data = yaml.safe_load(yp.read_text(encoding="utf-8")) or {}
            data.update(_slug=d.name, _year=year_dir.name, _type="event",
                        _url=f"{REPO_URL}/tree/main/data/events/{year_dir.name}/{d.name}",
                        _inactive=EVENT_INACTIVE,
                        updates=load_updates(d))
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


def is_inactive(record):
    if record.get("status", "") in record["_inactive"]:
        return True
    if record["_type"] == "event":
        end   = as_date(record.get("date_end"))
        start = as_date(record.get("date_start"))
        cutoff = end or start
        if cutoff and cutoff < TODAY:
            return True
    return False


def classify(record):
    updates = record["updates"]
    latest  = updates[0] if updates else None
    recent  = latest and (TODAY - latest["date"]).days <= 7

    # Urgent and blocked always win, even for inactive records
    if latest and latest["fm"].get("priority") == "urgent":
        return "urgent"
    if blocked_update(record):
        return "blocked"

    # Recent update overrides inactive (per dashboard spec)
    if recent:
        return "this_week"

    if is_inactive(record):
        return "inactive"

    return "stale"


# ── rendering ─────────────────────────────────────────────────────────────────

def type_badge(record):
    return f"`{TYPE_LABEL[record['_type']]}`"


def age_str(record):
    updates = record["updates"]
    if not updates:
        return "no updates"
    days = (TODAY - updates[0]["date"]).days
    if days == 0:
        return "updated today"
    if days == 1:
        return "updated 1d ago"
    if days <= 7:
        return f"updated {days}d ago"
    if days >= 14:
        return f"⚠️ **{days}d since last update**"
    return f"{days}d ago"


def event_date_hint(record):
    start = as_date(record.get("date_start"))
    if not start:
        return "📅 date TBD"
    days_until = (start - TODAY).days
    if days_until == 0:
        return "📅 today"
    if days_until > 0:
        return f"📅 {start}"
    return f"📅 {start}"


def full_card(record):
    title   = record.get("title") or record["_slug"]
    url     = record["_url"]
    badge   = type_badge(record)
    age     = age_str(record)
    updates = record["updates"]

    meta = f"_{age}_"
    if record["_type"] == "event":
        meta = f"_{event_date_hint(record)} · {age}_"

    lines = [f"### {badge} [{title}]({url})", meta]

    blocking = blocked_update(record)
    if blocking:
        lines.append(f"\n> **Blocked since {blocking['date']}**")

    if updates and updates[0]["body"]:
        lines.append("")
        lines.append(updates[0]["body"])

    return "\n".join(lines)


def stale_row(record, include_date_col=False):
    title = record.get("title") or record["_slug"]
    url   = record["_url"]
    badge = type_badge(record)
    age   = age_str(record)
    if include_date_col:
        if record["_type"] == "event":
            start = as_date(record.get("date_start"))
            date_col = str(start) if start else "TBD"
        else:
            date_col = ""
        return f"| {badge} [{title}]({url}) | {date_col} | {age} |"
    return f"| {badge} [{title}]({url}) | {age} |"


def inactive_item(record):
    title  = record.get("title") or record["_slug"]
    url    = record["_url"]
    badge  = type_badge(record)
    status = record.get("status", "")
    if record["_type"] == "event":
        start = as_date(record.get("date_start"))
        extra = f" · {start}" if start else ""
        return f"- {badge} [{title}]({url}) _{status}{extra}_"
    return f"- {badge} [{title}]({url}) _{status}_"


def render_tier(emoji, label, records, empty_msg):
    count = len(records)
    header = f"## {emoji} {label} ({count})"
    if not records:
        return f"{header}\n\n_{empty_msg}_"

    # Full cards for urgent/blocked/this_week; table for stale; list for inactive
    if emoji in ("🔴", "🟡", "🟢"):
        body = "\n\n".join(full_card(r) for r in records)
    elif emoji == "⚪":
        # Mixed records: use two-col table for non-events, three-col for events
        has_events = any(r["_type"] == "event" for r in records)
        if has_events:
            rows = ["| Record | Date | Last update |", "|---|---|---|"]
        else:
            rows = ["| Record | Last update |", "|---|---|"]
        rows += [stale_row(r, include_date_col=has_events) for r in records]
        body = "\n".join(rows)
    else:
        body = "\n".join(inactive_item(r) for r in records)

    return f"{header}\n\n{body}"


# ── main ──────────────────────────────────────────────────────────────────────

def generate():
    all_records = load_projects() + load_funding() + load_events()

    tiers = {k: [] for k in ("urgent", "blocked", "this_week", "stale", "inactive")}
    for r in all_records:
        tiers[classify(r)].append(r)

    # Sort each tier
    def by_latest_desc(r):
        u = r["updates"]
        return u[0]["date"] if u else date.min

    def by_title(r):
        return (r.get("title") or r["_slug"]).lower()

    def by_gap_desc(r):
        u = r["updates"]
        # (0, -days) sorts updated records first, largest gap first.
        # (1, 0) sorts no-update records last.
        return (1, 0) if not u else (0, -(TODAY - u[0]["date"]).days)

    def by_type_then_title(r):
        order = {"project": 0, "funding": 1, "event": 2}
        return (order[r["_type"]], (r.get("title") or r["_slug"]).lower())

    def by_type_then_date(r):
        order = {"project": 0, "funding": 1, "event": 2}
        d = as_date(r.get("date_start")) if r["_type"] == "event" else None
        return (order[r["_type"]], d or date.max)

    tiers["urgent"].sort(key=by_latest_desc, reverse=True)
    tiers["blocked"].sort(key=by_latest_desc, reverse=True)
    tiers["this_week"].sort(key=by_type_then_title)
    tiers["stale"].sort(key=by_gap_desc)  # ascending: (0,-days) puts oldest first, (1,0) last
    tiers["inactive"].sort(key=by_type_then_date)

    inactive_body = (
        "\n".join(inactive_item(r) for r in tiers["inactive"])
        if tiers["inactive"] else "_None._"
    )
    inactive_section = (
        f"<details>\n<summary>🗄️ Inactive ({len(tiers['inactive'])})</summary>\n\n"
        f"{inactive_body}\n\n</details>"
    )

    total  = len(all_records)
    counts = (f"{len(load_projects())} projects · "
              f"{len(load_funding())} grants · "
              f"{len(load_events())} events")

    sections = [
        f"# MIT Critical Data — Lab Dashboard\n\n"
        f"_Generated {TODAY.isoformat()} · {total} records ({counts}) · "
        f"[contributing guide](docs/contributing.md)_",
        render_tier("🔴", "Urgent",    tiers["urgent"],    "No urgent items."),
        render_tier("🟡", "Blocked",   tiers["blocked"],   "No blocked items."),
        render_tier("🟢", "This week", tiers["this_week"], "No updates this week."),
        render_tier("⚪", "Stale",     tiers["stale"],     "All up to date."),
        inactive_section,
    ]

    OUTPUT.write_text("\n\n---\n\n".join(sections) + "\n", encoding="utf-8")
    print(f"Dashboard written -> {OUTPUT}  ({total} records: "
          f"{len(tiers['urgent'])} urgent, {len(tiers['blocked'])} blocked, "
          f"{len(tiers['this_week'])} this week, {len(tiers['stale'])} stale, "
          f"{len(tiers['inactive'])} inactive)")


if __name__ == "__main__":
    generate()
