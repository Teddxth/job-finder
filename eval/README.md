# Evaluation

Does the Job Finder score agree with what I actually want? To check, I rated real offers from my own internship search blind (the model score was hidden while rating), on a 1 to 5 scale mapped to 0/25/50/75/100, and said for each one whether I would apply.

Run it yourself:

```bash
python eval/analyze.py eval/evaluation.json
```

## Results (first batch, 18 offers)

| Metric | Value |
|---|---|
| Keep / discard agreement (threshold 50) | 94 % |
| Recall: offers I would apply to that the score keeps | 100 % |
| Precision: kept offers I would apply to | 100 % |
| Rank correlation (Spearman) | 0.40 |
| Mean absolute error | 20.5 pts |

## What I learned

- **As a filter, the score works.** With a threshold of 50 it never dropped an offer I wanted.
- **As a ranking, it is weak.** My favourite offers (CSEM, MDPI, Tether, Capgemini) score between 55 and 72, in the middle of the pack. The weighted criteria do not capture what makes an offer stand out for me (team, topic, company).
- **The exclusion rules were too strict.** 6 of the offers I would apply to had been discarded by the filtering rules (sector, location), not by the score. The rules need revisiting.

## Limits

18 offers is a small sample, and 17 of them are offers I would apply to, so the ability to reject bad offers is barely tested yet. Next batches will add more negative examples.

## Next steps

- Rate 30 to 50 more offers, including ones I would not apply to.
- Revisit the exclusion rules.
- Try learning the weights from my ratings instead of setting them by hand.
