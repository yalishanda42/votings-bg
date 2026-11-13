# Statistical checks of the 2026 Bulgarian elections

Were the elections rigged? These notebooks apply the standard statistical **election-forensics** methods to the
polling-station results of two 2026 Bulgarian elections:
* the **parliamentary election of 19 April**, in which Прогресивна България won an absolute majority (131 of 240 seats) with 44.6% of the party vote;
* the **presidential election**: round 1 on 25 October and the runoff between Илияна Йотова and Андрей Гюров on 1 November.

Every method is checked against a **baseline of what an honest election with the same polling stations would look like**.
That matters: several textbook tests (e.g. Benford's first-digit law) "fail" on perfectly honest polling-station data.

## Notebooks

| Notebook | Question | Methods |
|---|---|---|
| **Benford & digit tests** ([round 1](benford.ipynb), [round 2](benford_round2.ipynb)) | Were numbers invented rather than counted? | Benford 1st digit, Mebane's 2nd-digit test, last-digit uniformity, round-number heaping, all compared with simulated clean elections |
| **Turnout fingerprints** ([round 1](turnout_fingerprint.ipynb), [round 2](turnout_fingerprint_round2.ipynb)) | Were ballot boxes stuffed? | Klimek's election fingerprint, Shpilkin's turnout-binned votes, Kobak's integer-percentage test, fraud injection, round 1 → round 2 comparison |
| **Ballot-level anomalies** ([round 1](ballot_anomalies.ipynb), [round 2](ballot_anomalies_round2.ipynb)) | Was the count or the voter list manipulated? | Regression discontinuity at the 300-voter paper/machine threshold, invalid-ballot and added-voter outlier tests, protocol arithmetic, combined watch-list |

**Parliamentary election (19 Apr 2026):**

| Notebook | Question | Methods |
|---|---|---|
| [**Benford & digit tests**](benford_parliament.ipynb) | Were numbers invented? | As above, plus hand-counted paper votes vs machine votes in the same stations |
| [**Turnout fingerprints**](turnout_fingerprint_parliament.ipynb) | Ballot stuffing or controlled voting? | As above, plus each station compared with itself in the presidential election six months later ("parliament-only" voters) |
| [**Ballot-level anomalies**](ballot_anomalies_parliament.ipynb) | Count or voter-list manipulation? | As above, plus the **machines' signed electronic records (`suemg`) vs the hand count of machine receipts**, and the seat arithmetic (how many votes would change the majority) |
| [**Double voting**](double_voting_parliament.ipynb) | Did students vote twice (e.g. Sofia in the morning, Plovdiv in the afternoon)? | Added-voter counts vs the same stations in the presidential election, student-area stations, worst-case bounds against the majority margin |

## Summary of findings

### Parliamentary election (19 Apr 2026)

| | Finding |
|---|---|
| Invented numbers (Benford, digits) | none; paper counts look like machine counts |
| Ballot stuffing for the winner | none: its share doesn't rise with turnout, and voters who turn out only for parliament split for it at its normal share (0.97×) |
| Machine records vs hand count | agree to within 0.75%; missing receipts hit every party in proportion. The largest single losses cost Прогресивна България 101 votes (Русе) and ПП–ДБ 90 (Sofia) |
| Organised-voting patterns | "parliament-only" neighbourhood mobilisation strongly favours **ДПС** (3.0× its share; wins 84 of 204 surge stations vs 33 expected) and ГЕРБ–СДС (1.5×); 32 low-turnout bloc stations for Прогресивна България (~1,400 votes) |
| Structural irregularity | 243 stations with an unused machine voted entirely on paper, 133 of them in Кърджали (50% ДПС) |
| Student double voting | no trace: fewer added voters per voter than in either presidential round, **~1,800 fewer than expected in Plovdiv**, and student areas voted ПП–ДБ first. Even counting every domestic added voter (107k) as a double vote for the winner leaves it a majority (126 seats) |
| Data-quality issues | 13 voter-list errors, 10 stations with more "added" voters than voters, a few dozen protocols with recording slips |

**Bottom line:** no statistical fingerprint of fraud that produced the majority. The majority is robust to the removal of ~221,500 of
the winner's votes. It is more sensitive to the 4% threshold: had МЕЧ and Величие each got ~30,000 more votes, the winner would have
119 seats. Nothing found takes votes from those two parties. The flagged stations are in
[`watchlist_parliament.csv`](watchlist_parliament.csv).

### Presidential election (Oct–Nov 2026)

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
included in the repository because of their size. For the parliamentary election, the per-party machine totals parsed from them are
cached in `data/2026-04-parliament/machine_totals_19.04.2026.csv`, so the notebooks run without the archives.

## Running locally

```bash
pip install -r requirements.txt
python load_data.py           # sanity checks + writes votes_by_section*.csv
jupyter lab                   # open any notebook
```

```python
from load_data import load_votes, load_sections, load_machine_counts, ROUND2, PARLIAMENT
votes = load_votes(election=ROUND2)     # rows = polling stations, columns = candidates
meta = load_sections(ROUND2)            # station metadata (region, municipality, address, voters on list, …)
parl = load_votes(election=PARLIAMENT)  # columns = parties, e.g. '21 Прогресивна България'
machines = load_machine_counts()        # parliament: electronic per-party totals from each voting machine
```

Build the book: `pip install "jupyter-book<2" && jupyter-book build .` (output in `_build/html`).
