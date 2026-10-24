# Sanity check: are the files in results/ the full runs the report describes?
import csv
from pathlib import Path

R = Path(__file__).parent / "results"
EXPECTED_ROWS = {"sweeps.csv": 50, "consistency.csv": 9, "noise.csv": 6, "depth.csv": 6}

ok = True
for name, want in EXPECTED_ROWS.items():
    path = R / name
    if not path.exists():
        print(f"MISSING  {name}")
        ok = False
        continue
    got = len(list(csv.DictReader(open(path))))
    status = "ok" if got == want else f"WRONG (expected {want})"
    ok = ok and got == want
    print(f"{name:<16} {got:>3} rows  {status}")

sweeps = R / "sweeps.csv"
if sweeps.exists():
    rows = list(csv.DictReader(open(sweeps)))
    games = {r["games"] for r in rows}
    print("games per match:", games, "ok" if games == {"20"} else "WRONG (expected {'20'})")
    ok = ok and games == {"20"}
    print("\nparameter, value, vs-baseline W-D-L, win rate  (compare with report.md tables)")
    for r in rows:
        if r["opponent"] == "baseline":
            print(f"{r['parameter']:<17}{r['value']:<6}{r['wins']}-{r['draws']}-{r['losses']}   {r['win_rate']}")
print("\nALL GOOD" if ok else "\nSOMETHING IS OFF - rerun the experiments without --quick")