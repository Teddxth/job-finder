"""Compare human ratings with the Job Finder score.

Usage: python eval/analyze.py [eval/evaluation.json]
"""
import json
import sys
from statistics import mean

THRESHOLD = 50


def ranks(values):
    order = sorted(range(len(values)), key=lambda i: values[i])
    r = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j < len(order) and values[order[j]] == values[order[i]]:
            j += 1
        for k in range(i, j):
            r[order[k]] = (i + j - 1) / 2
        i = j
    return r


def spearman(a, b):
    a, b = ranks(a), ranks(b)
    ma, mb = mean(a), mean(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    den = (sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b)) ** 0.5
    return num / den if den else float("nan")


def main(path):
    items = json.load(open(path, encoding="utf-8"))["items"]
    h = [x["human"] for x in items]
    m = [x["model"] for x in items]
    wanted = [x for x in items if x["would_apply"]]
    kept = [x for x in items if x["model"] >= THRESHOLD]
    print(f"rated offers            : {len(items)}")
    print(f"keep/discard agreement  : {mean((a >= THRESHOLD) == (b >= THRESHOLD) for a, b in zip(h, m)):.0%}")
    print(f"spearman (rank)         : {spearman(h, m):.2f}")
    print(f"mean absolute error     : {mean(abs(a - b) for a, b in zip(h, m)):.1f} pts")
    if wanted:
        print(f"recall (would apply)    : {mean(x['model'] >= THRESHOLD for x in wanted):.0%}")
    if kept:
        print(f"precision (kept)        : {mean(x['would_apply'] for x in kept):.0%}")
    filt = [x for x in wanted if not x["kept_by_filters"]]
    print(f"wanted but excluded by filters: {len(filt)}")
    print("\nlargest disagreements:")
    for x in sorted(items, key=lambda x: -abs(x["human"] - x["model"]))[:5]:
        print(f"  {x['company'][:40]:40} human {x['human']:>3}  model {x['model']:>5.1f}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "eval/evaluation.json")
