# PMHNP Practice Ops (GitHub Collector)

This folder keeps Agent-S focused on your solo PMHNP practice while it lives in GitHub.

## What it does

- Collects PMHNP-relevant skills and tools from GitHub queries.
- Produces a plain-language check-in report:
  - `practice_ops/PMHNP_SKILLS_TOOLS_CHECKIN.md`
- Produces a machine-readable snapshot:
  - `practice_ops/latest_collection.json`

## Automation

Workflow:
- `.github/workflows/pmhnp_skill_collection.yml`

Schedule:
- Every 6 hours and on manual trigger.

## Focus configuration

Edit:
- `practice_ops/pmhnp_focus.json`

to adjust:
- practice goals
- query buckets
- Agent-S skill backlog
- next-action watchlist
