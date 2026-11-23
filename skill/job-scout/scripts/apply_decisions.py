"""Applies the swipe decisions (decisions.json) to the Excel tracker.

Kept offers get the status "To apply"; discarded ones are moved to the "Rejected" sheet
with the justification "Discarded by the user".
"""
import json
import sys

from openpyxl import load_workbook


def main(tracker="job_tracker.xlsx", decisions_path="decisions.json"):
    dec = {(d["company"].lower(), d["title"].lower()): d["decision"]
           for d in json.load(open(decisions_path, encoding="utf-8"))}
    wb = load_workbook(tracker)
    ws, rej = wb["Matches"], wb["Rejected"]
    head = [c.value for c in ws[1]]
    ci, ti, si, ji = (head.index(k) for k in ("Company", "Title", "Status", "Justification"))
    kept = moved = 0
    for r in range(ws.max_row, 1, -1):
        row = [c.value for c in ws[r]]
        d = dec.get((str(row[ci]).lower(), str(row[ti]).lower()))
        if d == "keep":
            ws.cell(r, si + 1, "To apply"); kept += 1
        elif d == "discard":
            row[si], row[ji] = "Discarded by the user", f"{row[ji]} | discarded after review"
            rej.append(row); ws.delete_rows(r); moved += 1
    wb.save(tracker)
    print(f"{kept} kept, {moved} moved to 'Rejected' -> {tracker}")


if __name__ == "__main__":
    main(*sys.argv[1:])
