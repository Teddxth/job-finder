"""Job Finder MCP server.

Exposes the job-search tracker as MCP tools, so Claude (Desktop, Code, or any MCP client)
can score offers, store them, list them and record decisions without touching files by hand.

The tracker is a JSON file (default: ./job_tracker.json, override with JOB_FINDER_TRACKER).
Scoring reuses skill/job-finder/scripts/score.py, so the skill and the server always agree.

Run:  python mcp_server/server.py
"""
import json
import os
import sys
from datetime import date
from pathlib import Path

import yaml
from mcp.server.mcpserver import MCPServer

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skill" / "job-finder" / "scripts"))
from score import score_offer  # noqa: E402

DECISIONS = {"keep", "discard"}


def tracker_path() -> Path:
    return Path(os.environ.get("JOB_FINDER_TRACKER", "job_tracker.json"))


def profile_path() -> Path:
    return Path(os.environ.get("JOB_FINDER_PROFILE", ROOT / "examples" / "profile.yaml"))


def load_tracker() -> list[dict]:
    p = tracker_path()
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def save_tracker(offers: list[dict]) -> None:
    p = tracker_path()
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(offers, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p)


def key(o: dict) -> tuple[str, str]:
    return (str(o.get("company", "")).strip().lower(), str(o.get("title", "")).strip().lower())


def load_profile() -> dict:
    return yaml.safe_load(profile_path().read_text(encoding="utf-8"))


def validate(offer: dict) -> None:
    if not offer.get("company") or not offer.get("title"):
        raise ValueError("each offer needs at least 'company' and 'title'")
    for k, v in offer.get("subscores", {}).items():
        if not 0 <= float(v) <= 1:
            raise ValueError(f"subscore '{k}' must be between 0 and 1, got {v}")


mcp = MCPServer(
    "job-finder",
    instructions=(
        "Tracker for a job search. Analyse each offer yourself (sub-scores in [0, 1] per criterion "
        "of the profile), then call add_offers. The score itself is computed here, deterministically."
    ),
)


@mcp.tool()
def get_profile() -> dict:
    """Return the candidate profile: weights, threshold, excluded sectors, locations."""
    return load_profile()


@mcp.tool()
def score_offers(offers: list[dict]) -> list[dict]:
    """Score offers without storing them. Each offer: company, title, sector, subscores {criterion: 0-1}."""
    profile = load_profile()
    out = []
    for o in offers:
        validate(o)
        s, d, why = score_offer(o, profile)
        out.append({"company": o["company"], "title": o["title"], "score": s, "decision": d, "justification": why})
    return sorted(out, key=lambda x: -x["score"])


@mcp.tool()
def add_offers(offers: list[dict]) -> dict:
    """Score offers and add them to the tracker. Offers already present (same company and title) are updated."""
    profile = load_profile()
    tracker = {key(o): o for o in load_tracker()}
    added = updated = 0
    for o in offers:
        validate(o)
        o = dict(o)
        o["score"], o["decision"], o["justification"] = score_offer(o, profile)
        k = key(o)
        if k in tracker:
            o["status"] = tracker[k].get("status", "new")
            updated += 1
        else:
            o["status"] = "new"
            o["added_on"] = date.today().isoformat()
            added += 1
        tracker[k] = o
    save_tracker(sorted(tracker.values(), key=lambda x: -x["score"]))
    return {"added": added, "updated": updated, "total": len(tracker)}


@mcp.tool()
def list_offers(status: str | None = None, min_score: float = 0, limit: int = 20) -> list[dict]:
    """List tracked offers, best first. Filter by status (new, to_apply, discarded, applied) and minimum score."""
    rows = [o for o in load_tracker() if o["score"] >= min_score and (status is None or o.get("status") == status)]
    return [{k: o.get(k) for k in ("company", "title", "score", "decision", "status", "justification", "url")}
            for o in rows[:limit]]


@mcp.tool()
def set_decision(company: str, title: str, decision: str) -> dict:
    """Record the user's review of an offer: decision is 'keep' (to apply) or 'discard'."""
    if decision not in DECISIONS:
        raise ValueError(f"decision must be one of {sorted(DECISIONS)}")
    tracker = load_tracker()
    for o in tracker:
        if key(o) == key({"company": company, "title": title}):
            o["status"] = "to_apply" if decision == "keep" else "discarded"
            save_tracker(tracker)
            return {"company": o["company"], "title": o["title"], "status": o["status"]}
    raise ValueError(f"offer not found: {company} / {title}")


@mcp.tool()
def mark_applied(company: str, title: str) -> dict:
    """Mark an offer as applied today."""
    tracker = load_tracker()
    for o in tracker:
        if key(o) == key({"company": company, "title": title}):
            o["status"], o["applied_on"] = "applied", date.today().isoformat()
            save_tracker(tracker)
            return {"company": o["company"], "title": o["title"], "status": "applied", "applied_on": o["applied_on"]}
    raise ValueError(f"offer not found: {company} / {title}")


@mcp.tool()
def stats() -> dict:
    """Summary of the search: offers per status and per decision, average score."""
    t = load_tracker()
    by = lambda f: {v: sum(o.get(f) == v for o in t) for v in sorted({o.get(f) for o in t})}  # noqa: E731
    return {"total": len(t), "by_status": by("status"), "by_decision": by("decision"),
            "average_score": round(sum(o["score"] for o in t) / len(t), 1) if t else None}


if __name__ == "__main__":
    mcp.run()
