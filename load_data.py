"""Load CIK section-level results for the 2026 presidential election.

Usage:
    from load_data import load_votes, load_sections, ROUND1, ROUND2
    votes = load_votes()                    # round 1 (default): rows = sections, cols = candidates
    votes2 = load_votes(election=ROUND2)    # round 2 (runoff)
    meta = load_sections(election=ROUND2)   # section metadata, same index
    df = meta.join(votes2)

    load_votes(kind="paper") / kind="machine" for paper-only or machine-only counts.
"""

from pathlib import Path

import pandas as pd

ROUND1 = "2026-10-president-01"
ROUND2 = "2026-11-president-02"
ELECTIONS = {ROUND1: "25.10.2026", ROUND2: "01.11.2026"}   # folder -> file date suffix

def data_dir(election=ROUND1):
    return Path(__file__).parent / "data" / election / "Актуализирана база данни"

# backwards compatibility (round 1)
DATA_DIR = data_dir(ROUND1)
DATE = ELECTIONS[ROUND1]

# Each candidate block in votes.txt: number; total; paper; machine; machine1; machine2
_BLOCK = 6
_KIND_OFFSET = {"total": 1, "paper": 2, "machine": 3}


def _f(name, election=ROUND1):
    return data_dir(election) / f"{name}_{ELECTIONS[election]}.txt"


def load_candidates(election=ROUND1):
    """Candidate number -> short label like '25 Илияна Йотова' (presidential candidate only)."""
    c = pd.read_csv(_f("cik_candidates", election), sep=";", header=None,
                    names=["num", "party", "pos", "names"], dtype={"num": int})
    def short(names):
        president = names.split(" и ")[0].split()
        return f"{president[0]} {president[-1]}"
    c["label"] = c["num"].astype(str).str.zfill(2) + " " + c["names"].map(short)
    return c.set_index("num")


def load_votes(kind="total", include_none=True, election=ROUND1):
    """DataFrame indexed by section code, one column per candidate with absolute votes.

    kind: 'total' | 'paper' | 'machine'
    include_none: append a 'Не подкрепям никого' column (from protocols.txt).
    """
    off = _KIND_OFFSET[kind]
    raw = pd.read_csv(_f("votes", election), sep=";", header=None, dtype=str)
    labels = load_candidates(election)["label"]
    n_cand = (raw.shape[1] - 2) // _BLOCK
    data = {}
    for i in range(n_cand):
        base = 2 + i * _BLOCK
        num = int(raw[base].iloc[0])
        assert (raw[base].astype(int) == num).all(), f"candidate order differs in block {i}"
        data[labels[num]] = raw[base + off].fillna("0").astype(int)
    votes = pd.DataFrame(data)
    votes.index = raw[0].rename("section")
    if include_none:
        votes["Не подкрепям никого"] = load_protocol_totals(election)[f"none_{kind}"].reindex(votes.index).fillna(0).astype(int)
    return votes


def load_protocol_totals(election=ROUND1):
    """Per-section aggregates from protocols.txt (sum of paper + machine protocols)."""
    p = pd.read_csv(_f("protocols", election), sep=";", header=None, dtype=str,
                    names=range(1, 29))
    num = lambda col: pd.to_numeric(p[col], errors="coerce").fillna(0).astype(int)
    form = num(1)
    paper_forms = form.isin([24, 26, 28, 30])
    machine_forms = form.isin([32, 41])
    receipt_forms = form.isin([26, 30])  # machine control receipts counted by hand (items 9.x, 11.x)
    main = form.isin([24, 25, 26, 28, 29, 30])  # exactly one main protocol per section
    out = pd.DataFrame({
        "section": p[2],
        "voters_list": num(9) * main,
        "voters_added": num(10) * main,
        "voted_signatures": num(11) * main,
        "invalid_paper": num(13) * paper_forms,
        "valid_cand_paper": num(16) * paper_forms,
        "none_paper": num(17) * paper_forms,
        "valid_cand_machine": num(27) * machine_forms + (num(19) + num(23)) * receipt_forms,
        "none_machine": num(28) * machine_forms + (num(20) + num(24)) * receipt_forms,
    })
    agg = out.groupby("section").sum()
    agg["none_total"] = agg["none_paper"] + agg["none_machine"]
    agg["valid_cand_total"] = agg["valid_cand_paper"] + agg["valid_cand_machine"]
    return agg


def load_sections(election=ROUND1):
    """Section metadata indexed by section code."""
    # addresses may contain ';' -> take 5 fields from the left, 5 from the right, rest is address
    rows = []
    for line in _f("sections", election).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        f = line.split(";")
        rows.append(f[:5] + [";".join(f[5:-5])] + f[-5:])
    s = pd.DataFrame(rows, columns=[
        "section", "admin_id", "admin_name", "ekatte", "place", "address",
        "lon", "lat", "mobile", "ship", "machines"])
    s = s.set_index("section")
    s["region"] = s.index.str[:2].astype(int)          # МИР (32 = abroad)
    s["municipality"] = s.index.str[:4]
    s["abroad"] = s["region"] == 32
    for c in ["lon", "lat"]:
        s[c] = pd.to_numeric(s[c], errors="coerce")
    for c in ["mobile", "ship", "machines"]:
        s[c] = pd.to_numeric(s[c], errors="coerce").fillna(0).astype(int)
    pt = load_protocol_totals(election)
    s = s.join(pt[["voters_list", "voters_added", "voted_signatures", "invalid_paper"]])
    return s


if __name__ == "__main__":
    for election, out_name in [(ROUND1, "votes_by_section.csv"), (ROUND2, "votes_by_section_round2.csv")]:
        v = load_votes(election=election)
        pt = load_protocol_totals(election)
        cand = v.drop(columns="Не подкрепям никого").sum(axis=1)
        mismatch = cand[cand != pt["valid_cand_total"].reindex(v.index)]
        print(f"[{election}] {v.shape[0]} sections x {v.shape[1]} columns; "
              f"sections where candidate sum != protocol valid votes: {len(mismatch)} {list(mismatch.index)}")
        print(v.sum().sort_values(ascending=False).to_string())
        out = Path(__file__).parent / out_name
        load_sections(election).join(v).to_csv(out)
        print(f"saved {out}\n")
