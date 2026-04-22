#!/usr/bin/env python3
"""
Collect PMHNP-relevant skills/tools from GitHub and publish a plain-language CHECK IN.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "pmhnp_focus.json"
MARKDOWN_PATH = ROOT / "PMHNP_SKILLS_TOOLS_CHECKIN.md"
JSON_PATH = ROOT / "latest_collection.json"


def _http_json(url: str, headers: Dict[str, str]) -> Dict[str, Any]:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def search_github_repos(query: str, token: str | None, per_page: int = 5) -> List[Dict[str, Any]]:
    encoded_query = urllib.parse.quote(query)
    url = (
        "https://api.github.com/search/repositories"
        f"?q={encoded_query}&sort=updated&order=desc&per_page={per_page}"
    )
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "agent-s-pmhnp-collector"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    payload = _http_json(url, headers=headers)
    items = payload.get("items", [])
    cleaned = []
    for item in items:
        cleaned.append(
            {
                "full_name": item.get("full_name", ""),
                "html_url": item.get("html_url", ""),
                "description": (item.get("description") or "").strip(),
                "updated_at": item.get("updated_at", ""),
                "stargazers_count": item.get("stargazers_count", 0),
                "language": item.get("language") or "Unknown",
            }
        )
    return cleaned


def load_config() -> Dict[str, Any]:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_collection(config: Dict[str, Any], token: str | None) -> Dict[str, Any]:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    queries = config.get("github_queries", [])

    buckets = []
    for query_cfg in queries:
        label = query_cfg["label"]
        query = query_cfg["query"]
        repos = search_github_repos(query, token=token, per_page=5)
        buckets.append({"label": label, "query": query, "repos": repos})

    return {
        "generated_at_utc": now,
        "practice_profile": config.get("practice_profile", ""),
        "collection_goal": config.get("collection_goal", ""),
        "buckets": buckets,
        "agent_skill_backlog": config.get("agent_skill_backlog", []),
        "watchlist_next_actions": config.get("watchlist_next_actions", []),
    }


def to_markdown(data: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# CHECK IN (PMHNP Skills + Tools Collector)")
    lines.append("")
    lines.append(f"- Generated: {data['generated_at_utc']}")
    lines.append(f"- Practice Profile: {data['practice_profile']}")
    lines.append("")
    lines.append("## 1) Mission")
    lines.append(data["collection_goal"])
    lines.append("")
    lines.append("## 2) Capability Status")
    lines.append("- Cloud PMHNP skills/tool collection in GitHub: READY")
    lines.append("- Desktop EHR/CoverMyMeds interaction from this cloud workflow: BLOCKED")
    lines.append("- Prior-auth execution readiness on local desktop agent: PARTIAL")
    lines.append("")
    lines.append("## 3) Collected Tools (GitHub Signals)")
    for bucket in data["buckets"]:
        lines.append(f"### {bucket['label']}")
        lines.append(f"- Query: `{bucket['query']}`")
        if not bucket["repos"]:
            lines.append("- No repositories returned this run.")
            continue
        for repo in bucket["repos"]:
            description = repo["description"] if repo["description"] else "No description provided."
            lines.append(
                f"- [{repo['full_name']}]({repo['html_url']}) | "
                f"stars={repo['stargazers_count']} | lang={repo['language']} | "
                f"updated={repo['updated_at']} | {description}"
            )
        lines.append("")

    lines.append("## 4) Agent-S Skill Backlog for Solo PMHNP")
    for item in data["agent_skill_backlog"]:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## 5) Next Curation Actions")
    for item in data["watchlist_next_actions"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## 6) Guardrails")
    lines.append("- Do not submit clinical or payer data from cloud automation without explicit human approval.")
    lines.append("- Use local authenticated sessions for final healthcare portal actions.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    config = load_config()
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

    try:
        data = build_collection(config, token)
    except Exception as exc:
        print(f"Collection failed: {exc}", file=sys.stderr)
        return 1

    markdown = to_markdown(data)

    MARKDOWN_PATH.write_text(markdown, encoding="utf-8")
    JSON_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")

    print(f"Wrote {MARKDOWN_PATH}")
    print(f"Wrote {JSON_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
