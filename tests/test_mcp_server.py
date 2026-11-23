"""End-to-end test: start the MCP server over stdio and drive it like Claude would."""
import json
import sys
from pathlib import Path

import anyio
import pytest
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

ROOT = Path(__file__).resolve().parent.parent
OFFERS = json.loads((ROOT / "examples" / "offers_example.json").read_text(encoding="utf-8"))


def call(tracker: Path, steps):
    """Run the server in a subprocess and execute `steps(session)`."""
    params = StdioServerParameters(
        command=sys.executable,
        args=[str(ROOT / "mcp_server" / "server.py")],
        env={"JOB_FINDER_TRACKER": str(tracker), "JOB_FINDER_PROFILE": str(ROOT / "examples" / "profile.yaml")},
    )

    async def run():
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return await steps(session)

    return anyio.run(run)


def result(res):
    assert not res.is_error, res.content
    return json.loads(res.content[0].text) if len(res.content) == 1 else [json.loads(c.text) for c in res.content]


@pytest.fixture
def tracker(tmp_path):
    return tmp_path / "tracker.json"


def test_tools_are_listed(tracker):
    async def steps(s):
        return {t.name for t in (await s.list_tools()).tools}

    names = call(tracker, steps)
    assert {"get_profile", "score_offers", "add_offers", "list_offers", "set_decision", "mark_applied", "stats"} <= names


def test_full_workflow(tracker):
    async def steps(s):
        added = result(await s.call_tool("add_offers", {"offers": OFFERS}))
        again = result(await s.call_tool("add_offers", {"offers": OFFERS[:1]}))
        await s.call_tool("set_decision", {"company": "ExampleVision",
                                           "title": "ML Engineer intern - computer vision", "decision": "keep"})
        await s.call_tool("mark_applied", {"company": "examplevision",
                                           "title": "ml engineer intern - computer vision"})
        st = result(await s.call_tool("stats", {}))
        return added, again, st

    added, again, st = call(tracker, steps)
    assert added == {"added": 3, "updated": 0, "total": 3}
    assert again == {"added": 0, "updated": 1, "total": 3}
    assert st["by_status"]["applied"] == 1

    saved = json.loads(tracker.read_text(encoding="utf-8"))
    finance = next(o for o in saved if o["company"] == "SomeBank")
    assert finance["score"] == 0 and "Excluded sector" in finance["justification"]
    assert [o["score"] for o in saved] == sorted((o["score"] for o in saved), reverse=True)


def test_invalid_input_is_reported(tracker):
    async def steps(s):
        bad = await s.call_tool("add_offers", {"offers": [{"company": "X", "title": "Y", "subscores": {"skills": 3}}]})
        unknown = await s.call_tool("set_decision", {"company": "Nope", "title": "Nope", "decision": "keep"})
        wrong = await s.call_tool("set_decision", {"company": "Nope", "title": "Nope", "decision": "maybe"})
        return bad.is_error, unknown.is_error, wrong.is_error

    assert call(tracker, steps) == (True, True, True)
    assert not tracker.exists()
