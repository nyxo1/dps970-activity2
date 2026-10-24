# Monte Carlo tree search move generator for Connect Four (AIMA Figure 5.11).

#     function MONTE-CARLO-TREE-SEARCH(state) returns an action
#         tree <- NODE(state)
#         while IS-TIME-REMAINING() do          (here: a fixed number of iterations)
#             leaf  <- SELECT(tree)
#             child <- EXPAND(leaf)             (here: up to expand_width children)
#             result <- SIMULATE(child)
#             BACK-PROPAGATE(result, child, tree)
#         return the move in ACTIONS(state) whose node has highest number of playouts

# Customisations from the assignment:
#   - SELECT picks children by a utility with a playout part (win rate +
#     exploration bonus) and an objective part (a score from the game rules).
#   - EXPAND adds up to `expand_width` children to a node.
#   - The tree is limited to `max_depth`; at that level we SIMULATE with a
#     random playout instead of growing the tree.
#   - The number of iterations is configurable.

# Perspective rule: node.wins always counts results for the player who JUST
# MOVED into that node, so a parent choosing among its children picks the child
# that is best for the player making that move.

import math
import random
from dataclasses import dataclass

from board import COLS, ROWS, WINDOWS, other


@dataclass
class Config:
    iterations: int = 1000       # loop repeats
    expand_width: int = 3        # children added each time a node is expanded
    max_depth: int = 6           # tree height; simulate with a playout at this level
    exploration_c: float = 1.4   # weight of the exploration bonus
    objective_weight: float = 0.3  # weight of the rules-based part of the utility
    seed: int = None             # None = different every run

    def __post_init__(self):
        if self.iterations < 1 or self.expand_width < 1 or self.max_depth < 1:
            raise ValueError("iterations, expand_width and max_depth must be at least 1")


# ---------------------------------------------------------------------------
# Objective part of the utility (comes from the rules of the game only)
# ---------------------------------------------------------------------------
def objective(board, player):
    winner = board.winner()
    if winner == player:
        return 1.0
    if winner is not None:
        return -1.0
    if board.is_full():
        return 0.0

    opp = other(player)
    score = 0
    for window in WINDOWS:
        mine = theirs = 0
        for r, c in window:
            v = board.grid[r][c]
            if v == player:
                mine += 1
            elif v == opp:
                theirs += 1
        if theirs == 0:
            if mine == 3:
                score += 5
            elif mine == 2:
                score += 2
        elif mine == 0:
            if theirs == 3:
                score -= 5
            elif theirs == 2:
                score -= 2

    centre = COLS // 2
    for r in range(ROWS):
        v = board.grid[r][centre]
        if v == player:
            score += 3
        elif v == opp:
            score -= 3
    return math.tanh(score / 20)


# ---------------------------------------------------------------------------
# Tree node
# ---------------------------------------------------------------------------
class Node:
    def __init__(self, board, parent=None, move=None):
        self.board = board
        self.parent = parent
        self.move = move                       # column played to reach this node
        self.depth = 0 if parent is None else parent.depth + 1
        self.children = []
        self.visits = 0                        # N: playouts through this node
        self.wins = 0.0                        # U: wins (draw = 0.5) for player_just_moved
        self.player_just_moved = other(board.current_player)
        self.is_terminal = board.is_terminal()
        self.untried = [] if self.is_terminal else board.legal_moves()
        self.objective = objective(board, self.player_just_moved)


# ---------------------------------------------------------------------------
# The four steps
# ---------------------------------------------------------------------------
def utility(child, parent, cfg):
    exploit = child.wins / child.visits
    explore = cfg.exploration_c * math.sqrt(math.log(parent.visits) / child.visits)
    return exploit + explore + cfg.objective_weight * child.objective


def select(root, cfg, rng):
    node = root
    while True:
        if node.is_terminal or node.depth >= cfg.max_depth or node.untried:
            return node
        node = max(node.children, key=lambda ch: (utility(ch, node, cfg), rng.random()))


def expand(node, cfg, rng):
    if node.is_terminal or node.depth >= cfg.max_depth:
        return [node]
    candidates = []
    for move in node.untried:
        b = node.board.copy()
        b.play(move)
        candidates.append(Node(b, node, move))
    candidates.sort(key=lambda ch: (ch.objective, rng.random()), reverse=True)
    new_children = candidates[:cfg.expand_width]
    for child in new_children:
        node.untried.remove(child.move)
        node.children.append(child)
    return new_children


def simulate(node, rng):
    b = node.board
    if node.is_terminal:
        return b.winner()
    b = b.copy()
    while b.winner() is None:
        moves = b.legal_moves()
        if not moves:
            break
        b.play(rng.choice(moves))
    return b.winner()


def backpropagate(node, winner):
    while node is not None:
        node.visits += 1
        if winner is None:
            node.wins += 0.5
        elif winner == node.player_just_moved:
            node.wins += 1
        node = node.parent


# ---------------------------------------------------------------------------
# Top level
# ---------------------------------------------------------------------------
def search(board, cfg=None):
    cfg = cfg or Config()
    if board.is_terminal():
        raise ValueError("the game is already over")
    rng = random.Random(cfg.seed)
    root = Node(board.copy())
    for _ in range(cfg.iterations):
        leaf = select(root, cfg, rng)
        for child in expand(leaf, cfg, rng):
            backpropagate(child, simulate(child, rng))
    return root


def choose_move(root):
    best = max(root.children, key=lambda ch: (ch.visits, ch.wins / ch.visits, -ch.move))
    return best.move


def mcts_move(board, cfg=None):
    moves = board.legal_moves()
    if not moves:
        raise ValueError("no legal moves")
    if len(moves) == 1:
        return moves[0]
    return choose_move(search(board, cfg))
