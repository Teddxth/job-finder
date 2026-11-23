# Job Finder MCP server

The tracker as an MCP server: Claude analyses the offers, the server scores them deterministically (same code as the skill), stores them and keeps track of decisions.

| Tool | What it does |
|---|---|
| `get_profile` | Returns weights, threshold, excluded sectors, locations |
| `score_offers` | Scores offers without storing them |
| `add_offers` | Scores and stores offers, updates duplicates (same company + title) |
| `list_offers` | Lists offers best first, filtered by status or minimum score |
| `set_decision` | Records a review: `keep` (to apply) or `discard` |
| `mark_applied` | Marks an offer as applied today |
| `stats` | Offers per status and decision, average score |

Inputs are validated (sub-scores in [0, 1], known decisions), and the tracker is written atomically.

## Install

```bash
pip install -r requirements.txt
```

**Claude Code**

```bash
claude mcp add job-finder \
  -e JOB_FINDER_PROFILE=/path/to/profile.yaml \
  -e JOB_FINDER_TRACKER=/path/to/job_tracker.json \
  -- python /path/to/job-finder/mcp_server/server.py
```

**Claude Desktop** (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "job-finder": {
      "command": "python",
      "args": ["/path/to/job-finder/mcp_server/server.py"],
      "env": {
        "JOB_FINDER_PROFILE": "/path/to/profile.yaml",
        "JOB_FINDER_TRACKER": "/path/to/job_tracker.json"
      }
    }
  }
}
```

Then ask Claude: *"Find AI internships in Lille, score them and add them to my tracker"*, or *"Show me the offers above 70 I haven't reviewed yet"*.

## Tests

`tests/test_mcp_server.py` starts the server over stdio and drives it with the official MCP client: add offers, update a duplicate, record a decision, mark as applied, check the stats and the error handling.

```bash
pip install -r requirements-dev.txt
pytest -q
```
