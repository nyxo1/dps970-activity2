# Experiments for the Connect Four MCTS report.

# Usage (from the project root, venv active):
#     python q1_connect4/experiments.py sweeps --games 20
#     python q1_connect4/experiments.py consistency --runs 30
#     python q1_connect4/experiments.py noise --games 20
#     python q1_connect4/experiments.py depth
#     python q1_connect4/experiments.py charts
#     python q1_connect4/experiments.py all --quick        (small run to check everything works)

# Results go to q1_connect4/results/ as CSV files and PNG charts.

# Each sweep changes ONE setting of the baseline and plays the variant
#   (a) against a random player and (b) against the baseline MCTS player,
# alternating who moves first. win_rate = (wins + 0.5 * draws) / games.

import argparse
import csv
import random
import time
from collections import Counter
from dataclasses import asdict, replace
from pathlib import Path

from board import COLS, P1, P2, Board
from mcts import Config, mcts_move

HERE = Path(__file__).parent
RESULTS = HERE / "results"
TEST_DATA = HERE / "test_data"

BASELINE = Config(iterations=200, expand_width=3, max_depth=6,
                  exploration_c=1.4, objective_weight=0.3)

SWEEPS = {
    "iterations": [50, 100, 200, 500, 1000],
    "expand_width": [1, 2, 3, 5, 7],
    "max_depth": [1, 2, 4, 6, 8, 12],
    "objective_weight": [0.0, 0.1, 0.3, 0.6, 1.0],
    "exploration_c": [0.5, 1.0, 1.4, 2.0],
}

QUICK_SWEEPS = {
    "iterations": [50, 200],
    "expand_width": [1, 3],
    "max_depth": [2, 6],
    "objective_weight": [0.0, 0.3],
    "exploration_c": [1.0, 1.4],
}

# positions used to measure how consistent the chosen move is
POSITIONS = {
    "empty_board": None,
    "midgame": "midgame.txt",
    "block_in_one": "block_in_one.txt",
}


# ---------------------------------------------------------------------------
# players
# ---------------------------------------------------------------------------
def random_player(board, rng):
    return rng.choice(board.legal_moves())


def mcts_player(cfg):
    def player(board, rng):
        return mcts_move(board, replace(cfg, seed=rng.randrange(10 ** 9)))
    return player


# ---------------------------------------------------------------------------
# matches
# ---------------------------------------------------------------------------
def play_game(first, second, rng, timer=None):
    # Play one game. `timer` is a dict that collects seconds/moves for the P1 or P2 function `first`.
    board = Board()
    players = {P1: first, P2: second}
    while not board.is_terminal():
        fn = players[board.current_player]
        start = time.perf_counter()
        move = fn(board, rng)
        if timer is not None and fn is timer["player"]:
            timer["seconds"] += time.perf_counter() - start
            timer["moves"] += 1
        board.play(move)
    return board.winner()


def run_match(player_a, player_b, games, seed):
    # Player A vs player B; A moves first in even-numbered games.
    rng = random.Random(seed)
    wins = draws = losses = 0
    timer = {"player": player_a, "seconds": 0.0, "moves": 0}
    for g in range(games):
        a_first = g % 2 == 0
        first, second = (player_a, player_b) if a_first else (player_b, player_a)
        winner = play_game(first, second, rng, timer)
        a_seat = P1 if a_first else P2
        if winner is None:
            draws += 1
        elif winner == a_seat:
            wins += 1
        else:
            losses += 1
    return {
        "games": games, "wins": wins, "draws": draws, "losses": losses,
        "win_rate": round((wins + 0.5 * draws) / games, 3),
        "avg_move_sec": round(timer["seconds"] / max(timer["moves"], 1), 4),
    }


def write_csv(path, rows):
    RESULTS.mkdir(exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print("wrote", path)


# ---------------------------------------------------------------------------
# experiment 1: strength sweeps
# ---------------------------------------------------------------------------
def run_sweeps(games, quick=False, seed=2026):
    sweeps = QUICK_SWEEPS if quick else SWEEPS
    rows = []
    for param, values in sweeps.items():
        for value in values:
            cfg = replace(BASELINE, **{param: value})
            for opponent_name, opponent in (("random", random_player),
                                            ("baseline", mcts_player(BASELINE))):
                result = run_match(mcts_player(cfg), opponent, games, seed)
                row = {"parameter": param, "value": value, "opponent": opponent_name, **result}
                rows.append(row)
                print(f"{param}={value:<5} vs {opponent_name:<8} win_rate={row['win_rate']:<5} "
                      f"({row['wins']}W {row['draws']}D {row['losses']}L)  {row['avg_move_sec']}s/move")
    write_csv(RESULTS / "sweeps.csv", rows)
    return rows


# ---------------------------------------------------------------------------
# experiment 2: does it always choose the same move?
# ---------------------------------------------------------------------------
def load_position(filename):
    if filename is None:
        return Board()
    return Board.from_text((TEST_DATA / filename).read_text())


def run_consistency(runs, quick=False):
    iteration_levels = [50, 200] if quick else [50, 200, 1000]
    rows = []
    for name, filename in POSITIONS.items():
        board = load_position(filename)
        for iterations in iteration_levels:
            counts = Counter()
            for seed in range(runs):
                cfg = replace(BASELINE, iterations=iterations, seed=seed)
                counts[mcts_move(board, cfg)] += 1
            most_common, times = counts.most_common(1)[0]
            row = {"position": name, "iterations": iterations, "runs": runs}
            for col in range(COLS):
                row[f"col{col}"] = counts.get(col, 0)
            row["most_common_move"] = most_common
            row["share_of_most_common"] = round(times / runs, 2)
            row["distinct_moves"] = len(counts)
            rows.append(row)
            print(f"{name:<13} iterations={iterations:<5} counts={dict(sorted(counts.items()))}")
    write_csv(RESULTS / "consistency.csv", rows)
    return rows


# ---------------------------------------------------------------------------
# experiment 3: how noisy are the win rates? (baseline plays itself)
# ---------------------------------------------------------------------------
def run_noise_check(games, quick=False):
    # The baseline plays the baseline, so the true win rate is about 0.5.
    # Repeating with different master seeds shows how far 20-game results wander.
    seeds = [11, 12] if quick else [11, 12, 13, 14, 15, 16]
    rows = []
    for seed in seeds:
        result = run_match(mcts_player(BASELINE), mcts_player(BASELINE), games, seed)
        rows.append({"master_seed": seed, **result})
        print(f"master seed {seed}: {result['wins']}W {result['draws']}D {result['losses']}L  "
              f"win_rate={result['win_rate']}")
    total_games = sum(r["games"] for r in rows)
    points = sum(r["wins"] + 0.5 * r["draws"] for r in rows)
    print(f"pooled win rate over {total_games} games: {round(points / total_games, 3)}")
    write_csv(RESULTS / "noise.csv", rows)
    return rows


# ---------------------------------------------------------------------------
# experiment 4: how deep does the tree actually grow?
# ---------------------------------------------------------------------------
def run_depth_check(quick=False):
    # Searches with no depth cap, to see how far down the tree really grows.
    # max_depth only has an effect if the tree can reach it.
    from mcts import search
    seeds = range(2) if quick else range(5)
    rows = []
    for name, filename in (("empty_board", None), ("midgame", "midgame.txt")):
        board = load_position(filename)
        for iterations in ([50, 200] if quick else [50, 200, 1000]):
            depths = []
            for seed in seeds:
                root = search(board, replace(BASELINE, iterations=iterations, max_depth=40, seed=seed))
                stack, deepest = [root], 0
                while stack:
                    node = stack.pop()
                    deepest = max(deepest, node.depth)
                    stack.extend(node.children)
                depths.append(deepest)
            rows.append({"position": name, "iterations": iterations,
                         "min_deepest_node": min(depths), "max_deepest_node": max(depths)})
            print(f"{name:<12} iterations={iterations:<5} deepest node depth: {min(depths)}-{max(depths)}")
    write_csv(RESULTS / "depth.csv", rows)
    return rows


# ---------------------------------------------------------------------------
# charts (matplotlib is only needed here)
# ---------------------------------------------------------------------------
def make_charts():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sweeps_file = RESULTS / "sweeps.csv"
    if sweeps_file.exists():
        with open(sweeps_file) as f:
            rows = list(csv.DictReader(f))
        for param in dict.fromkeys(r["parameter"] for r in rows):
            fig, ax = plt.subplots(figsize=(6, 4))
            for opponent in ("random", "baseline"):
                pts = [(float(r["value"]), float(r["win_rate"])) for r in rows
                       if r["parameter"] == param and r["opponent"] == opponent]
                ax.plot(*zip(*pts), marker="o", label=f"vs {opponent}")
            ax.set_xlabel(param)
            ax.set_ylabel("win rate")
            ax.set_ylim(0, 1.05)
            ax.set_title(f"Effect of {param}")
            ax.legend()
            ax.grid(alpha=0.3)
            fig.tight_layout()
            out = RESULTS / f"sweep_{param}.png"
            fig.savefig(out, dpi=120)
            plt.close(fig)
            print("wrote", out)

    consistency_file = RESULTS / "consistency.csv"
    if consistency_file.exists():
        with open(consistency_file) as f:
            rows = list(csv.DictReader(f))
        for position in dict.fromkeys(r["position"] for r in rows):
            sub = [r for r in rows if r["position"] == position]
            fig, ax = plt.subplots(figsize=(6, 4))
            width = 0.8 / len(sub)
            for i, r in enumerate(sub):
                xs = [c + i * width for c in range(COLS)]
                ax.bar(xs, [int(r[f"col{c}"]) for c in range(COLS)], width,
                       label=f"{r['iterations']} iterations")
            ax.set_xticks([c + 0.4 - width / 2 for c in range(COLS)])
            ax.set_xticklabels(range(COLS))
            ax.set_xlabel("column chosen")
            ax.set_ylabel("times chosen")
            ax.set_title(f"Move consistency: {position}")
            ax.legend()
            fig.tight_layout()
            out = RESULTS / f"consistency_{position}.png"
            fig.savefig(out, dpi=120)
            plt.close(fig)
            print("wrote", out)


# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Connect Four MCTS experiments")
    parser.add_argument("what", choices=["sweeps", "consistency", "noise", "depth", "charts", "all"])
    parser.add_argument("--games", type=int, default=20, help="games per setting and opponent")
    parser.add_argument("--runs", type=int, default=30, help="searches per position and setting")
    parser.add_argument("--quick", action="store_true", help="tiny version to check the script works")
    args = parser.parse_args()

    if args.quick:
        args.games, args.runs = 4, 6
    if args.what in ("sweeps", "all"):
        run_sweeps(args.games, args.quick)
    if args.what in ("consistency", "all"):
        run_consistency(args.runs, args.quick)
    if args.what in ("noise", "all"):
        run_noise_check(args.games, args.quick)
    if args.what in ("depth", "all"):
        run_depth_check(args.quick)
    if args.what in ("charts", "all"):
        make_charts()


if __name__ == "__main__":
    main()
