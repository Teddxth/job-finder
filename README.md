# Job Finder: an AI agent that finds, scores and prepares job applications

[![Try the demo](https://img.shields.io/badge/Try%20the%20demo-swipe%20interface-4f46e5?style=for-the-badge)](https://teddxth.github.io/job-finder/swipe/) [![Download the skill](https://img.shields.io/badge/Download-Claude%20skill%20(.zip)-059669?style=for-the-badge)](https://github.com/Teddxth/job-finder/releases/latest/download/job-finder-skill.zip)
[![tests](https://github.com/Teddxth/job-finder/actions/workflows/tests.yml/badge.svg)](https://github.com/Teddxth/job-finder/actions/workflows/tests.yml)

I built this agent for my own end-of-studies internship search (AI engineer, 2027). Instead of scrolling job boards every day, the agent does the repetitive part and I only review the best offers.

**What it does**

1. Reads your CV and your preferences (titles, locations, sectors to avoid, salary).
2. Searches the job boards and company career pages.
3. Scores every offer with **weighted, explainable criteria** (skills, domain, location, level, remote, salary).
4. Builds an **Excel tracker**: matches above the threshold, rejected offers *with the reason*, and a list of companies for spontaneous applications.
5. Drafts a **tailored cover letter** for each match, without ever inventing experience.
6. Lets you review the matches **like a dating app**: swipe right to keep, left to discard. Your choices update the Excel tracker.

The scoring and the Excel generation are plain Python scripts, so the decision is reproducible: the LLM only fills the sub-scores, it cannot "push" an offer over the threshold.

## Use it in 2 minutes (Claude skill)

This repository contains a ready-to-use **skill** for Claude.

1. [Download `job-finder-skill.zip`](https://github.com/Teddxth/job-finder/releases/latest/download/job-finder-skill.zip) (no need to unzip it).
2. In Claude, open *Plug-ins → Add → Import a plug-in* and upload the zip. Skills require a Claude plan with code execution enabled.
3. Start a chat: *"Use job-finder to find AI internships in Lille starting in September 2027"* and attach your CV.

Claude asks for the missing preferences on the first run, then does the rest.

## Use the scripts alone

```bash
pip install openpyxl pyyaml
cp examples/profile.yaml my_profile.yaml        # edit it
python skill/job-finder/scripts/score.py examples/offers_example.json my_profile.yaml scored.json
python skill/job-finder/scripts/build_excel.py scored.json job_tracker.xlsx
```

Example output with the demo offers:

```
88.2  match     88% (threshold 50%). Weakest criteria: remote=60%, salary=80%
41.0  rejected  41% (threshold 50%). Weakest criteria: domain=20%, location=20%
 0.0  rejected  Excluded sector (Finance)
```

## Review the offers by swiping

**[Open the live demo](https://teddxth.github.io/job-finder/swipe/)**, or open `swipe/index.html` locally (it works offline, no install). It shows a demo deck; click *Load offers_scored.json* to load your own offers. Swipe, use the arrow keys or the buttons, then *Export decisions* and run:

```bash
python skill/job-finder/scripts/apply_decisions.py job_tracker.xlsx decisions.json
```

Kept offers get the status *To apply*; discarded ones move to the *Rejected* sheet.

## Use it from any MCP client (v2)

The tracker is also exposed as an **MCP server** ([`mcp_server/`](mcp_server/)), so Claude Code, Claude Desktop or any MCP client can drive it with tools instead of scripts: `add_offers`, `list_offers`, `set_decision`, `mark_applied`, `stats`. Claude does the reading and the judgment, the server does the deterministic part (scoring with the same code as the skill, storage, status).

```bash
pip install -r requirements.txt
claude mcp add job-finder -e JOB_FINDER_PROFILE=$PWD/my_profile.yaml -- python $PWD/mcp_server/server.py
```

Then: *"Find AI internships in Lille, score them and add them to my tracker."*

Tested end to end: `pytest` starts the server over stdio and drives it with the official MCP client, on every push (GitHub Actions).

## Evaluation (v2)

Version 1 scores offers with hand-set weights. Version 2 checks whether that score matches my own judgment: I rated 18 real offers from my internship search blind (model score hidden), then compared.

| Metric | Value |
|---|---|
| Keep / discard agreement (threshold 50) | 94 % |
| Recall on offers I would apply to | 100 % |
| Rank correlation (Spearman) | 0.40 |
| Mean absolute error | 20.5 pts |

The score is a reliable filter but a weak ranking, and the exclusion rules dropped 6 offers I wanted. Details, data and script in [`eval/`](eval/).

## Design choices

- **Explainable score**: every rejected offer gets a reason, so I can check the agent's judgement.
- **Ethics filter**: excluded sectors are removed before scoring.
- **Human in the loop**: the agent never sends an application. It stops and asks me when a captcha or a login blocks it.
- **Honesty rule**: letters and CV variants only reorder and develop real experience.
- **Daily routine**: in my own setup, a scheduled task runs the search every morning and fills a Google Sheet, so I find new offers ready to review.

## Repository

```
skill/job-finder/SKILL.md        instructions followed by the agent
skill/job-finder/scripts/        scoring + Excel tracker
swipe/index.html                card review interface (swipe)
examples/                       profile template and demo offers
eval/                           blind human ratings vs score (v2)
mcp_server/                     MCP server: the tracker as tools (v2)
tests/                          pytest: score + MCP server end to end
```

## Author

**Teddy Thamrong**, élève-ingénieur à l'École nationale supérieure d'Arts et Métiers (ENSAM), expertise IRIS (machine learning et robotique) · recherche un stage de fin d'études en IA à partir de février ou de septembre 2027.

License: MIT
