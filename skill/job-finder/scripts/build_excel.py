"""Builds the job-search tracker: matches, rejected offers, spontaneous applications."""
import json
import sys

from openpyxl import Workbook
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

HEAD = PatternFill("solid", fgColor="1F3864")
COLS = ["Score %", "Title", "Company", "Location", "Remote", "Sector", "Contract", "Start",
        "Junior salary (k€)", "Salary after 3 yrs (k€)", "Justification", "Link",
        "Cover letter", "Status", "Applied on"]


def sheet(ws, rows, cols):
    ws.append(cols)
    for c in ws[1]:
        c.font, c.fill = Font(bold=True, color="FFFFFF"), HEAD
        c.alignment = Alignment(wrap_text=True, vertical="center")
    for r in rows:
        ws.append(r)
    for i, col in enumerate(cols, 1):
        ws.column_dimensions[get_column_letter(i)].width = 45 if col in ("Justification", "Link") else 16
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions


def row(o):
    return [o.get("score"), o.get("title"), o.get("company"), o.get("location"), o.get("remote"),
            o.get("sector"), o.get("contract"), o.get("start"), o.get("salary_junior"),
            o.get("salary_growth"), o.get("justification"), o.get("url"),
            o.get("letter_file", ""), "To apply" if o.get("decision") == "match" else "", ""]


def main(scored_path, out="job_tracker.xlsx", companies_path=None):
    offers = json.load(open(scored_path, encoding="utf-8"))
    wb = Workbook()
    ws = wb.active
    ws.title = "Matches"
    sheet(ws, [row(o) for o in offers if o["decision"] == "match"], COLS)
    if ws.max_row > 1:
        ws.conditional_formatting.add(f"A2:A{ws.max_row}", ColorScaleRule(
            start_type="num", start_value=50, start_color="FFEB84",
            end_type="num", end_value=100, end_color="63BE7B"))
    sheet(wb.create_sheet("Rejected"), [row(o) for o in offers if o["decision"] != "match"], COLS)
    comp = json.load(open(companies_path, encoding="utf-8")) if companies_path else []
    sheet(wb.create_sheet("Spontaneous"),
          [[c.get("company"), c.get("location"), c.get("ai_team"), c.get("contact"), c.get("url"), ""] for c in comp],
          ["Company", "Location", "AI team / activity", "Contact", "Careers page", "Status"])
    wb.save(out)
    print(f"Tracker saved -> {out}")


if __name__ == "__main__":
    main(*sys.argv[1:])
