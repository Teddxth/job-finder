# Job Finder: an AI agent that finds, scores and prepares job applications

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

1. Download the `skill/job-finder` folder and zip it.
2. In Claude, open *Settings → Capabilities → Skills* and upload the zip.
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

Open `swipe/index.html` in a browser (it works offline, no install). It shows a demo deck; click *Load offers_scored.json* to load your own offers. Swipe, use the arrow keys or the buttons, then *Export decisions* and run:

```bash
python skill/job-finder/scripts/apply_decisions.py job_tracker.xlsx decisions.json
```

Kept offers get the status *To apply*; discarded ones move to the *Rejected* sheet.

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
```

## Author

**Teddy Thamrong**, Arts et Métiers engineering student (robotics & AI). Looking for an AI engineering internship from September 2027.

License: MIT
