#!/usr/bin/env python3
"""
Sync GitHub Issue labels from project and funding folder names.

  data/projects/* -> label "proj-<slug>"  (blue)
  data/funding/*  -> label "fund-<slug>"  (green)

Labels with a proj-/fund- prefix that have no matching folder are deleted.
All other labels are left untouched.

Usage (local):
    GITHUB_TOKEN=ghp_... GITHUB_REPOSITORY=criticaldata/mit py scripts/sync_labels.py
    GITHUB_TOKEN=ghp_... GITHUB_REPOSITORY=criticaldata/mit py scripts/sync_labels.py --dry-run

In GitHub Actions both env vars are injected automatically.
"""

import json
import os
import sys
from pathlib import Path
import urllib.error
import urllib.request

PROJECTS_DIR = Path("data/projects")
FUNDING_DIR  = Path("data/funding")

COLORS = {
    "proj-": "0075ca",   # blue
    "fund-": "2ea44f",   # green
}

DESCRIPTIONS = {
    "proj-": "Project",
    "fund-": "Funding",
}

DRY_RUN = "--dry-run" in sys.argv


# ── GitHub API ────────────────────────────────────────────────────────────────

def api(method, endpoint, token, repo, payload=None):
    url = f"https://api.github.com/repos/{repo}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept":        "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type":  "application/json",
    }
    body = json.dumps(payload).encode() if payload else None
    req  = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read()) if resp.length != 0 else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if e.code == 404 and method == "DELETE":
            return {}
        print(f"  HTTP {e.code} {method} {endpoint}: {body}", file=sys.stderr)
        raise


def list_labels(token, repo):
    """Return {name: label_dict} for all labels in the repo."""
    labels, page = {}, 1
    while True:
        batch = api("GET", f"labels?per_page=100&page={page}", token, repo)
        if not batch:
            break
        for lbl in batch:
            labels[lbl["name"]] = lbl
        if len(batch) < 100:
            break
        page += 1
    return labels


# ── folder discovery ──────────────────────────────────────────────────────────

def record_slugs(directory):
    """Return sorted list of record folder names, skipping non-record dirs."""
    if not directory.exists():
        return []
    skip = {"updates"}
    return sorted(
        d.name for d in directory.iterdir()
        if d.is_dir() and d.name not in skip and not d.name.startswith(".")
    )


# ── sync ──────────────────────────────────────────────────────────────────────

def sync(token, repo):
    # Build expected label set
    expected = {}
    for slug in record_slugs(PROJECTS_DIR):
        name = f"proj-{slug}"
        expected[name] = {"prefix": "proj-", "slug": slug}
    for slug in record_slugs(FUNDING_DIR):
        name = f"fund-{slug}"
        expected[name] = {"prefix": "fund-", "slug": slug}

    print(f"Expected: {len(expected)} labels "
          f"({sum(1 for v in expected.values() if v['prefix']=='proj-')} proj, "
          f"{sum(1 for v in expected.values() if v['prefix']=='fund-')} fund)")

    existing = list_labels(token, repo)
    print(f"Existing: {len(existing)} total labels in repo\n")

    created = updated = deleted = 0

    # Create or update managed labels
    for name, meta in sorted(expected.items()):
        prefix = meta["prefix"]
        color  = COLORS[prefix]
        desc   = f"{DESCRIPTIONS[prefix]}: {meta['slug']}"

        if name not in existing:
            print(f"  + create  {name}")
            if not DRY_RUN:
                api("POST", "labels", token, repo,
                    {"name": name, "color": color, "description": desc})
            created += 1
        else:
            lbl = existing[name]
            if lbl.get("color") != color or lbl.get("description") != desc:
                print(f"  ~ update  {name}")
                if not DRY_RUN:
                    api("PATCH", f"labels/{urllib.parse.quote(name)}", token, repo,
                        {"color": color, "description": desc})
                updated += 1
            else:
                print(f"  = ok      {name}")

    # Delete stale managed labels (proj-/fund- with no matching folder)
    for name in sorted(existing):
        if not any(name.startswith(p) for p in COLORS):
            continue   # not a managed label — leave it alone
        if name not in expected:
            print(f"  - delete  {name}")
            if not DRY_RUN:
                api("DELETE", f"labels/{urllib.parse.quote(name)}", token, repo)
            deleted += 1

    tag = " (dry run)" if DRY_RUN else ""
    print(f"\n{created} created, {updated} updated, {deleted} deleted{tag}")


# ── main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    token = os.environ.get("GITHUB_TOKEN")
    repo  = os.environ.get("GITHUB_REPOSITORY")   # "owner/repo"

    if not token:
        sys.exit("Error: GITHUB_TOKEN env var not set.")
    if not repo:
        sys.exit("Error: GITHUB_REPOSITORY env var not set (e.g. criticaldata/mit).")

    # urllib.parse needed for label name encoding
    import urllib.parse

    if DRY_RUN:
        print("Dry run — no changes will be made.\n")

    sync(token, repo)
