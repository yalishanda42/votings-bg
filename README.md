# Statistical checks of the 2026 Bulgarian presidential election

Was the election rigged? These notebooks apply the standard statistical **election-forensics** methods to the
polling-station results of the 2026 Bulgarian presidential election: round 1 on 25 October and the runoff between
Илияна Йотова and Андрей Гюров on 1 November.

Every method is checked against a **baseline of what an honest election with the same polling stations would look like**.
That matters: several textbook tests (e.g. Benford's first-digit law) "fail" on perfectly honest polling-station data.

## Notebooks

| Notebook | Question | Methods |
|---|---|---|
| **Benford & digit tests** ([round 1](benford.ipynb), [round 2](benford_round2.ipynb)) | Were numbers invented rather than counted? | Benford 1st digit, Mebane's 2nd-digit test, last-digit uniformity, round-number heaping, all compared with simulated clean elections |
| **Turnout fingerprints** ([round 1](turnout_fingerprint.ipynb), [round 2](turnout_fingerprint_round2.ipynb)) | Were ballot boxes stuffed? | Klimek's election fingerprint, Shpilkin's turnout-binned votes, Kobak's integer-percentage test, fraud injection, round 1 → round 2 comparison |
| **Ballot-level anomalies** ([round 1](ballot_anomalies.ipynb), [round 2](ballot_anomalies_round2.ipynb)) | Was the count or the voter list manipulated? | Regression discontinuity at the 300-voter paper/machine threshold, invalid-ballot and added-voter outlier tests, protocol arithmetic, combined watch-list |

## Summary of findings

| | Round 1 | Round 2 (runoff) |
|---|---|---|
| Invented numbers (Benford, digits) | none | none |
| Ballot stuffing (turnout fingerprint) | none | none; runoff turnout rose evenly (+5 pts) and new voters split like the rest |
| Counting-stage manipulation | none | none |
| Data-quality issues | 39 voter-list errors, 2 small arithmetic mismatches | 42 voter-list errors (only 12 repeat), 21 machine recording slips |
| Organised-voting patterns | ~56 low-turnout blocs, mostly Василев | mobilisation of round-1 abstainers for Гюров (Кърджали, Белица, Якоруда, Шумен, Хасково; net ≈ +4,900 votes); 9 stations with blocs in both rounds |

**Bottom line:** no statistical fingerprint of large-scale fraud in either round. What remains are localised patterns of
organised voting, involving hundreds to a few thousand votes against a 343,601-vote margin in the runoff. The stations behind them
are listed in [`watchlist.csv`](watchlist.csv) (round 1) and [`watchlist_round2.csv`](watchlist_round2.csv) (round 2).

These methods cannot detect vote buying among people who would have voted anyway, pressure on voters, or problems that affect
paper and machine stations equally. A "clean" result means *the published numbers look like honest counts*. It does not mean
*the election was clean*.

## Data

Polling-station results published by the Central Election Commission (ЦИК, [cik.bg](https://www.cik.bg)) as open data
(“Актуализирана база данни”), in `data/<election>/Актуализирана база данни/`. The machine-voting archives (`suemg/`) are not
included in the repository because of their size.

## Running locally

```bash
pip install -r requirements.txt
python load_data.py           # sanity checks + writes votes_by_section*.csv
jupyter lab                   # open any notebook
```

```python
from load_data import load_votes, load_sections, ROUND2
votes = load_votes(election=ROUND2)     # rows = polling stations, columns = candidates
meta = load_sections(ROUND2)            # station metadata (region, municipality, address, voters on list, …)
```

Build the book: `pip install "jupyter-book<2" && jupyter-book build .` (output in `_build/html`).
