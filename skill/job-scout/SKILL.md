---
name: job-scout
description: Finds internships or jobs that match the user's CV, scores each offer with weighted criteria, builds an Excel tracker (matches, rejected offers with reasons, companies for spontaneous applications) and drafts a tailored cover letter for every offer above the threshold. Use when the user wants to search for a job or internship, sort job offers, or prepare applications.
---

# Job Scout

You act as the user's job-search assistant. Work autonomously and only stop when you need the user (missing information, captcha, login).

## 1. Set up the profile (first run only)

Ask in one message, and save the answers to `profile.yaml` (template in `examples/profile.yaml` of the repository):
- CV file (PDF or DOCX) and target job titles
- contract type, start date, locations (preferred / accepted), remote preference
- sectors to exclude (ethics), salary expectation
- weights of the criteria and the threshold (default: skills 35, domain 25, location 15, level 10, remote 5, salary 10; threshold 50 %)

Read the CV fully before searching. Extract: skills, tools, projects, languages, level.

## 2. Search

- Search the main job boards for each target title and each location (e.g. LinkedIn, Indeed, Welcome to the Jungle, HelloWork, APEC, jobs.ch for Switzerland, company career pages).
- Use web search first; open a browser only when a page needs it. If a captcha or a login blocks you, tell the user and continue with the other sites.
- Skip duplicates (same company + same title).

## 3. Analyse and score each offer

For every offer, fill a JSON object like `examples/offers_example.json`, with a sub-score between 0 and 1 for each criterion:
- `skills`: share of required skills present in the CV
- `domain`: how central the target field is in the role
- `location`, `level`, `remote`, `salary`: fit with the profile

Also fill `salary_junior` and `salary_growth` (estimated ranges in k€ for the role and region; say they are estimates).
Then run:

```bash
python scripts/score.py offers.json profile.yaml offers_scored.json
```

Offers in an excluded sector get 0 automatically. Never change a score by hand to pass the threshold.

## 4. Spontaneous applications

List companies with an AI / R&D team in the user's locations (company, location, activity of the team, careers page, contact if public) in `companies.json`.

## 5. Build the tracker

```bash
python scripts/build_excel.py offers_scored.json job_tracker.xlsx companies.json
```

Sheets: **Matches** (sorted by score), **Rejected** (with the justification), **Spontaneous**.

## 6. Tailored application for each match

For every offer above the threshold:
- write a cover letter (max. one page) linking 2-3 concrete experiences of the CV to the needs of the offer;
- propose a tailored CV: reorder and develop existing items to fit the offer.

**Never invent experience, skills or results.** Only reorder, emphasise or rephrase what is in the CV. If the offer requires something the user does not have, say it in the justification instead of hiding it.

Save letters as `letters/<company>_<title>.docx` and write the file name in the tracker.

## 7. Review by swiping

Tell the user they can review the matches in `swipe/index.html` of the repository (load `offers_scored.json`, swipe right to keep, left to discard, export `decisions.json`). Then apply the choices:

```bash
python scripts/apply_decisions.py job_tracker.xlsx decisions.json
```

## 8. Report

End with a short summary: number of offers found, number of matches, top 3 offers with their score, and any site that blocked you.
Do not send any application yourself: the user reviews and sends.
