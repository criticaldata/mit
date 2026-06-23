# How to Post a Project Update

This guide is for lab members who want to add a project update without using Git. Everything happens in the GitHub web interface — no command line needed.

---

## What an update is

Each project has an `updates/` folder. You drop a Markdown file there and the lab dashboard rebuilds automatically. Updates show up inline on the dashboard under the project name.

---

## Step-by-step: create an update via GitHub

1. **Go to your project folder** in the repo:
   `github.com/criticaldata/mit/tree/main/data/projects/<your-project>`

2. **Click into the `updates/` folder.**

3. **Click "Add file" → "Create new file"** (top right).

4. **Name the file** using the format `YYYY-MM-DD.md`, e.g. `2026-06-23.md`.
   If you're posting multiple updates on the same day, add a short label:
   `2026-06-23-midpoint-check.md`

5. **Paste the frontmatter and your update text** (see format below).

6. Scroll down, choose **"Commit directly to the `main` branch"**, and click **"Commit new file"**.

The dashboard regenerates within a minute or two.

---

## Update format

```markdown
---
type: weekly
---

Short summary of what happened this week. No rigid structure —
write what's most useful for the lab meeting.
```

That's the minimal version. Add `priority: urgent` if you need the project to show at the top of the dashboard, or change the type if something more specific applies (see below).

---

## Frontmatter fields

### `type` (optional, default: weekly)

| Value | When to use |
|---|---|
| `weekly` | Routine weekly status update |
| `adhoc` | Mid-week note, not tied to a regular meeting |
| `blocked` | Project is stuck and needs help or a decision |
| `resolved` | Clears a previous `blocked` update |

### `priority` (optional)

| Value | Effect |
|---|---|
| `urgent` | Moves the project to the top of the dashboard (🔴 Urgent tier) |

Omit `priority` entirely for routine updates.

---

## Examples

**Routine weekly update:**
```markdown
---
type: weekly
---

Finished the preprocessing pipeline for MIMIC-IV cohort. Next: run
baseline model experiments this week, aiming to have numbers by Friday.
```

**Flagging a blocker:**
```markdown
---
type: blocked
---

Waiting on IRB amendment approval before we can access the new cohort.
Need Leo to co-sign the amendment — please reach out.
```

**Clearing a blocker:**
```markdown
---
type: resolved
---

IRB amendment approved. Resuming data access this week.
```

**Urgent escalation:**
```markdown
---
priority: urgent
type: weekly
---

Submission deadline moved up to Friday. Need all co-authors to review
the draft by Wednesday EOD.
```

---

## Tips

- The body is freeform — write as much or as little as is useful.
- You don't need to repeat the project name or date in the body; the dashboard shows those automatically.
- If you're not sure which `type` to use, just omit it — the dashboard handles it gracefully.
- One update file per week is the norm, but there's no strict limit.
