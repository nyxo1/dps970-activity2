import re
from pathlib import Path

import pytest

from board import COLS, P1, P2, Board
from mcts import (Config, backpropagate, choose_move, expand, mcts_move, objective,
                  search, simulate)
import random

TEST_DATA = Path(__file__).parent / "test_data"


def load(name):
    """Return (board, expected column or None) from a test_data file."""
    text = (TEST_DATA / name).read_text()
    match = re.search(r"expected:\s*(\d)", text)
    return Board.from_text(text), (int(match.group(1)) if match else None)


FAST = dict(iterations=300, expand_width=3, max_depth=6)


# ---------- configuration ----------
@pytest.mark.parametrize("bad", [dict(iterations=0), dict(expand_width=0), dict(max_depth=0)])
def test_config_rejects_bad_values(bad):
    with pytest.raises(ValueError):
        Config(**bad)


# ---------- objective (rules-based part of the utility) ----------
def test_objective_is_between_minus_one_and_one():
    b, _ = load("midgame.txt")
    assert -1 < objective(b, P1) < 1


def test_objective_is_opposite_for_the_two_players():
    b, _ = load("midgame.txt")
    assert objective(b, P1) == pytest.approx(-objective(b, P2))


def test_objective_of_finished_games():
    b = Board()
    for m in [0, 1, 0, 1, 0, 1, 0]:
        b.play(m)
    assert objective(b, P1) == 1.0 and objective(b, P2) == -1.0
    d, _ = load("draw.txt")
    assert objective(d, P1) == 0.0


# ---------- the four steps ----------
def test_simulate_returns_a_valid_result():
    root = search(Board(), Config(iterations=1, seed=0))
    rng = random.Random(0)
    for _ in range(20):
        assert simulate(root.children[0], rng) in (None, P1, P2)


def test_expand_adds_at_most_expand_width_children():
    root = search(Board(), Config(iterations=1, expand_width=2, seed=0))
    assert len(root.children) == 2
    root = search(Board(), Config(iterations=1, expand_width=7, seed=0))
    assert len(root.children) == 7


def test_backpropagate_updates_the_whole_path():
    root = search(Board(), Config(iterations=1, expand_width=1, seed=0))
    child = root.children[0]
    visits_before = (root.visits, child.visits)
    backpropagate(child, child.player_just_moved)
    assert (root.visits, child.visits) == (visits_before[0] + 1, visits_before[1] + 1)


def test_tree_never_exceeds_max_depth():
    root = search(Board(), Config(iterations=300, expand_width=3, max_depth=3, seed=1))
    stack, deepest = [root], 0
    while stack:
        node = stack.pop()
        deepest = max(deepest, node.depth)
        stack.extend(node.children)
    assert deepest <= 3


def test_every_playout_goes_through_one_root_child():
    root = search(Board(), Config(**FAST, seed=2))
    assert sum(ch.visits for ch in root.children) == root.visits
    assert root.visits >= FAST["iterations"]


# ---------- choosing moves ----------
def test_move_is_legal_on_new_board():
    assert mcts_move(Board(), Config(**FAST, seed=3)) in range(COLS)


@pytest.mark.parametrize("name", ["win_in_one.txt", "block_in_one.txt", "almost_full.txt"])
def test_finds_the_expected_move(name):
    board, expected = load(name)
    for seed in range(5):
        assert mcts_move(board, Config(**FAST, seed=seed)) == expected


def test_same_seed_gives_same_move_and_statistics():
    b, _ = load("midgame.txt")
    r1 = search(b, Config(**FAST, seed=42))
    r2 = search(b, Config(**FAST, seed=42))
    assert [(c.move, c.visits) for c in r1.children] == [(c.move, c.visits) for c in r2.children]
    assert choose_move(r1) == choose_move(r2)


def test_single_legal_move_is_returned_without_search():
    board, _ = load("almost_full.txt")
    assert board.legal_moves() == [3]
    assert mcts_move(board, Config(iterations=1)) == 3


def test_finished_game_cannot_be_searched():
    d, _ = load("draw.txt")
    with pytest.raises(ValueError):
        search(d)
