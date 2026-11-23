"""Weighted matching score between a candidate profile and job offers.

Input : offers.json (list of offers already analysed by the agent, one sub-score per criterion in [0, 1])
        profile.yaml (weights, threshold, excluded sectors, preferred locations)
Output: offers_scored.json with total score, decision and justification.
"""
import json
import sys

import yaml

DEFAULT_WEIGHTS = {"skills": 35, "domain": 25, "location": 15, "level": 10, "remote": 5, "salary": 10}


def score_offer(offer, profile):
    weights = profile.get("weights", DEFAULT_WEIGHTS)
    excluded = [s.lower() for s in profile.get("excluded_sectors", [])]
    sector = offer.get("sector", "").lower()

    if any(x in sector for x in excluded):
        return 0.0, "rejected", f"Excluded sector ({offer.get('sector')})"

    sub = offer.get("subscores", {})
    total_w = sum(weights.values())
    total = sum(weights[k] * float(sub.get(k, 0)) for k in weights) / total_w * 100

    threshold = profile.get("threshold", 50)
    decision = "match" if total >= threshold else "rejected"
    weakest = sorted(weights, key=lambda k: float(sub.get(k, 0)))[:2]
    why = f"{total:.0f}% (threshold {threshold}%). Weakest criteria: " + ", ".join(
        f"{k}={float(sub.get(k, 0)):.0%}" for k in weakest)
    return round(total, 1), decision, why


def main(offers_path, profile_path, out_path="offers_scored.json"):
    offers = json.load(open(offers_path, encoding="utf-8"))
    profile = yaml.safe_load(open(profile_path, encoding="utf-8"))
    for o in offers:
        o["score"], o["decision"], o["justification"] = score_offer(o, profile)
    offers.sort(key=lambda o: o["score"], reverse=True)
    json.dump(offers, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    n = sum(o["decision"] == "match" for o in offers)
    print(f"{len(offers)} offers scored, {n} above threshold -> {out_path}")


if __name__ == "__main__":
    main(*sys.argv[1:])
