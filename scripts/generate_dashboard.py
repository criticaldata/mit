#!/usr/bin/env python3
"""
Generate docs/index.html — weekly lab meeting dashboard.

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

import html
import re
from datetime import date, timedelta
from pathlib import Path

import yaml

PROJECTS_DIR = Path("data/projects")
OUTPUT = Path("docs/index.html")
TODAY = date.today()

INACTIVE_STATUSES = {"completed", "on-hold", "archived"}


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
    """Extract date from filenames like YYYY-MM-DD[...].md"""
    m = re.match(r"(\d{4}-\d{2}-\d{2})", path.stem)
    if m:
        try:
            return date.fromisoformat(m.group(1))
        except ValueError:
            pass
    return None


def load_project(slug):
    """Load project YAML + updates. Returns dict or None."""
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
    """Return the blocking update dict if project is currently blocked, else None."""
    for u in project["updates"]:
        t = u["fm"].get("type", "")
        if t == "blocked":
            return u
        if t == "resolved":
            return None
    return None


def classify(project):
    status = project.get("status", "active")
    if status in INACTIVE_STATUSES:
        return "inactive"

    updates = project["updates"]
    latest = updates[0] if updates else None

    if latest and latest["fm"].get("priority") == "urgent":
        return "urgent"

    if blocked_update(project):
        return "blocked"

    if latest:
        if (TODAY - latest["date"]).days <= 7:
            return "this_week"

    return "stale"


# ── rendering ─────────────────────────────────────────────────────────────────

def safe_body(text):
    """Convert freeform update body to safe HTML."""
    escaped = html.escape(text)
    paragraphs = re.split(r"\n\s*\n", escaped.strip())
    out = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        p = p.replace("\n", "<br>")
        p = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", p)
        p = re.sub(r"\*(.+?)\*", r"<em>\1</em>", p)
        out.append(f"<p>{p}</p>")
    return "\n".join(out)


def project_card(project, show_update=True):
    slug = project["slug"]
    title = html.escape(project.get("title") or slug)
    updates = project["updates"]
    latest = updates[0] if updates else None

    if latest:
        days = (TODAY - latest["date"]).days
        if days == 0:
            age = "Updated today"
        elif days <= 7:
            age = f"Updated {days}d ago"
        elif days >= 14:
            age = f'<span class="stale-flag">{days}d since last update</span>'
        else:
            age = f"{days}d ago"
    else:
        age = '<span class="stale-flag">No updates yet</span>'

    repo_url = f"https://github.com/criticaldata/mit/tree/main/data/projects/{slug}"

    blocked = blocked_update(project)
    blocked_html = ""
    if blocked:
        blocked_html = (
            f'<div class="blocked-badge">Blocked since {blocked["date"]}</div>'
        )

    body_html = ""
    if show_update and latest and latest["body"]:
        body_html = f'<div class="update-body">{safe_body(latest["body"])}</div>'

    return f"""<div class="card" id="{slug}">
  <div class="card-header">
    <span class="card-title"><a href="{repo_url}" target="_blank" rel="noopener">{title}</a></span>
    <span class="card-meta">{age}</span>
  </div>
  {blocked_html}{body_html}
</div>"""


def render_section(emoji, label, projects, show_update=True):
    if not projects:
        return ""
    cards = "\n".join(project_card(p, show_update=show_update) for p in projects)
    return f"""<section class="tier">
  <h2>{emoji} {html.escape(label)} <span class="count">({len(projects)})</span></h2>
  <div class="cards">{cards}</div>
</section>"""


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

    inactive_cards = (
        "\n".join(project_card(p, show_update=False) for p in tiers["inactive"])
        if tiers["inactive"]
        else "<p class='empty'>No archived projects.</p>"
    )
    inactive_count = len(tiers["inactive"])

    body_sections = "\n".join(filter(None, [
        render_section("🔴", "Urgent", tiers["urgent"]),
        render_section("🟡", "Blocked", tiers["blocked"]),
        render_section("🟢", "This week", tiers["this_week"]),
        render_section("⚪", "Stale", tiers["stale"]),
    ]))

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MIT Critical Data — Lab Dashboard</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #f6f8fa; color: #24292f; line-height: 1.6;
      padding: 2rem 1.5rem;
      max-width: 860px; margin: 0 auto;
    }}
    header {{ margin-bottom: 2rem; }}
    header h1 {{ font-size: 1.4rem; font-weight: 700; }}
    .meta {{ color: #57606a; font-size: 0.82rem; margin-top: 0.25rem; }}
    .tier {{ margin-bottom: 2.5rem; }}
    h2 {{ font-size: 1rem; font-weight: 600; margin-bottom: 0.75rem; }}
    .count {{ font-weight: 400; color: #57606a; }}
    .cards {{ display: flex; flex-direction: column; gap: 0.6rem; }}
    .card {{
      background: #fff; border: 1px solid #d0d7de; border-radius: 8px;
      padding: 0.9rem 1rem;
    }}
    .card-header {{
      display: flex; justify-content: space-between;
      align-items: baseline; gap: 1rem; flex-wrap: wrap;
    }}
    .card-title {{ font-weight: 600; font-size: 0.92rem; }}
    .card-title a {{ color: #0969da; text-decoration: none; }}
    .card-title a:hover {{ text-decoration: underline; }}
    .card-meta {{ font-size: 0.78rem; color: #57606a; flex-shrink: 0; }}
    .stale-flag {{ color: #cf222e; font-weight: 600; }}
    .blocked-badge {{
      display: inline-block; margin-top: 0.4rem;
      font-size: 0.75rem; font-weight: 500;
      background: #fff8c5; color: #9a6700;
      border: 1px solid #d4a72c; border-radius: 4px;
      padding: 0.15rem 0.5rem;
    }}
    .update-body {{
      margin-top: 0.65rem; padding-top: 0.65rem;
      border-top: 1px solid #f0f0f0;
      font-size: 0.88rem; color: #444d56;
    }}
    .update-body p {{ margin-bottom: 0.4rem; }}
    .update-body p:last-child {{ margin-bottom: 0; }}
    details {{ margin-top: 1rem; }}
    details summary {{
      cursor: pointer; user-select: none;
      font-size: 0.92rem; font-weight: 600;
      color: #57606a; list-style: none;
      display: flex; align-items: center; gap: 0.4rem;
    }}
    details summary::-webkit-details-marker {{ display: none; }}
    .chevron {{ font-style: normal; display: inline-block; transition: transform 0.15s; }}
    details[open] .chevron {{ transform: rotate(90deg); }}
    .archived-cards {{ margin-top: 1rem; display: flex; flex-direction: column; gap: 0.6rem; }}
    .empty {{ color: #57606a; font-size: 0.88rem; margin-top: 0.75rem; }}
    @media (prefers-color-scheme: dark) {{
      body {{ background: #0d1117; color: #e6edf3; }}
      .card {{ background: #161b22; border-color: #30363d; }}
      .card-title a {{ color: #58a6ff; }}
      .card-meta, .count, .meta {{ color: #8b949e; }}
      .update-body {{ color: #c9d1d9; border-top-color: #21262d; }}
      .blocked-badge {{ background: #2d2101; color: #d29922; border-color: #6e4c05; }}
      details summary {{ color: #8b949e; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>MIT Critical Data — Lab Dashboard</h1>
    <p class="meta">Generated {TODAY.isoformat()} &middot; {len(projects)} active projects</p>
  </header>

  {body_sections}

  <details>
    <summary><span class="chevron">›</span>&nbsp;🗄️ Archived / Inactive <span class="count" style="margin-left:0.25rem">({inactive_count})</span></summary>
    <div class="archived-cards">{inactive_cards}</div>
  </details>
</body>
</html>"""

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(page, encoding="utf-8")
    print(f"Dashboard written -> {OUTPUT}  ({len(projects)} projects, "
          f"{len(tiers['urgent'])} urgent, {len(tiers['blocked'])} blocked, "
          f"{len(tiers['this_week'])} this week, {len(tiers['stale'])} stale, "
          f"{len(tiers['inactive'])} inactive)")


if __name__ == "__main__":
    generate()
