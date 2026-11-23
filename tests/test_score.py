import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skill" / "job-finder" / "scripts"))
from score import score_offer  # noqa: E402

PROFILE = {
    "weights": {"skills": 50, "domain": 50},
    "threshold": 50,
    "excluded_sectors": ["defense"],
}


def offer(skills, domain, sector="Industry"):
    return {"sector": sector, "subscores": {"skills": skills, "domain": domain}}


def test_weighted_average():
    score, decision, _ = score_offer(offer(1.0, 0.5), PROFILE)
    assert score == 75.0
    assert decision == "match"


def test_below_threshold_is_rejected():
    score, decision, why = score_offer(offer(0.4, 0.4), PROFILE)
    assert score == 40.0
    assert decision == "rejected"
    assert "threshold 50" in why


def test_threshold_is_inclusive():
    assert score_offer(offer(0.5, 0.5), PROFILE)[1] == "match"


def test_excluded_sector_scores_zero_with_reason():
    score, decision, why = score_offer(offer(1.0, 1.0, sector="Defense & Space"), PROFILE)
    assert (score, decision) == (0.0, "rejected")
    assert "Excluded sector" in why


def test_missing_subscore_counts_as_zero():
    score, _, _ = score_offer({"sector": "", "subscores": {"skills": 1.0}}, PROFILE)
    assert score == 50.0


def test_weights_scale_does_not_matter():
    scaled = dict(PROFILE, weights={"skills": 1, "domain": 1})
    assert score_offer(offer(0.8, 0.2), scaled)[0] == score_offer(offer(0.8, 0.2), PROFILE)[0]


def test_justification_names_weakest_criterion():
    _, _, why = score_offer(offer(0.9, 0.1), PROFILE)
    assert why.index("domain") < why.index("skills")


@pytest.mark.parametrize("skills,domain", [(0, 0), (1, 1), (0.33, 0.77)])
def test_score_in_range(skills, domain):
    assert 0 <= score_offer(offer(skills, domain), PROFILE)[0] <= 100
