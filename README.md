# DPS970 Activity 2

Python 3.12 or newer (the timings in the report were measured on Python 3.14.2).

## Setup
    python -m venv .venv
    .venv\Scripts\activate        (Mac/Linux: source .venv/bin/activate)
    pip install -r requirements.txt

## Run tests
    pytest

## Run experiments
Run from the project root with the venv active. Results go to q1_connect4/results/.

    python q1_connect4/experiments.py sweeps --games 20
    python q1_connect4/experiments.py consistency --runs 30
    python q1_connect4/experiments.py noise --games 20
    python q1_connect4/experiments.py depth
    python q1_connect4/experiments.py charts
    python q1_connect4/check_results.py

`sweeps` takes the longest (tens of minutes). Add `--quick` to any command for a
tiny smoke test; it writes to q1_connect4/results_quick/ and leaves the real
results alone.

## Contents
- answers.md: Q2, Q3, Q4 (logic)
- report.md: Q1 report
- q1_connect4/: board, MCTS, experiments, tests, test data, results