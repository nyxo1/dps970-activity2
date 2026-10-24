# Connect Four rules (6 rows x 7 columns).

# Design choices:
#   - grid[row][col]; row 0 is the TOP row and row 5 is the bottom row.
#   - A cell holds EMPTY (0), P1 (1) or P2 (2). P1 always moves first.
#   - current_player says whose turn it is; last_move is (row, col) of the
#     most recent piece (None on a new board).
#   - The winner is worked out when a piece is dropped, so asking
#     "is the game over?" is cheap during playouts.

ROWS, COLS = 6, 7
EMPTY, P1, P2 = 0, 1, 2

# (row step, column step): horizontal, vertical, diagonal down-right, diagonal down-left
DIRECTIONS = ((0, 1), (1, 0), (1, 1), (1, -1))


def other(player):
    """The opponent of `player`."""
    return P2 if player == P1 else P1


def _build_windows():
    # Every group of 4 cells in a line on the board (69 of them).
    windows = []
    for r in range(ROWS):
        for c in range(COLS):
            for dr, dc in DIRECTIONS:
                end_r, end_c = r + 3 * dr, c + 3 * dc
                if 0 <= end_r < ROWS and 0 <= end_c < COLS:
                    windows.append([(r + i * dr, c + i * dc) for i in range(4)])
    return windows


WINDOWS = _build_windows()


class Board:
    def __init__(self):
        self.grid = [[EMPTY] * COLS for _ in range(ROWS)]
        self.current_player = P1
        self.last_move = None
        self.num_moves = 0
        self._winner = None

    # ---------- copying ----------
    def copy(self):
        # An independent copy (the rows are copied too, not shared).
        b = Board.__new__(Board)
        b.grid = [row[:] for row in self.grid]
        b.current_player = self.current_player
        b.last_move = self.last_move
        b.num_moves = self.num_moves
        b._winner = self._winner
        return b

    # ---------- moves ----------
    def legal_moves(self):
        # Columns whose top cell is still empty.
        if self._winner is not None:
            return []
        return [c for c in range(COLS) if self.grid[0][c] == EMPTY]

    def play(self, col):
        # Drop the current player's piece into column `col`.
        if self._winner is not None:
            raise ValueError("the game is already over")
        if not 0 <= col < COLS or self.grid[0][col] != EMPTY:
            raise ValueError(f"column {col} is not a legal move")
        row = ROWS - 1
        while self.grid[row][col] != EMPTY:
            row -= 1
        self.grid[row][col] = self.current_player
        self.last_move = (row, col)
        self.num_moves += 1
        if self._is_win_at(row, col):
            self._winner = self.current_player
        self.current_player = other(self.current_player)

    # ---------- game state ----------
    def winner(self):
        # P1, P2, or None (no winner yet / draw).
        return self._winner

    def is_full(self):
        return self.num_moves == ROWS * COLS

    def is_draw(self):
        return self._winner is None and self.is_full()

    def is_terminal(self):
        return self._winner is not None or self.is_full()

    def _count(self, r, c, dr, dc, player):
        # How many `player` pieces in a row, starting next to (r, c) going (dr, dc).
        n = 0
        r += dr
        c += dc
        while 0 <= r < ROWS and 0 <= c < COLS and self.grid[r][c] == player:
            n += 1
            r += dr
            c += dc
        return n

    def _is_win_at(self, r, c):
        # Does the piece at (r, c) belong to a line of 4 or more?
        player = self.grid[r][c]
        for dr, dc in DIRECTIONS:
            total = 1 + self._count(r, c, dr, dc, player) + self._count(r, c, -dr, -dc, player)
            if total >= 4:
                return True
        return False

    # ---------- text in / out ----------
    @classmethod
    def from_text(cls, text, to_move=None):
        # Build a board from a text grid.

        # '.' = empty, 'X' = player 1, 'O' = player 2, six lines of seven
        # characters, top row first. Optional lines like 'to_move: O' are read;
        # any other 'key: value' line (e.g. 'expected: 3') is ignored.
        # If to_move is not given, X moves when both players have the same
        # number of pieces, otherwise O moves.
        rows = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            if ":" in line:
                key, value = (s.strip() for s in line.split(":", 1))
                if key == "to_move":
                    to_move = value
                continue
            rows.append(line)
        if len(rows) != ROWS or any(len(r) != COLS for r in rows):
            raise ValueError("board text must be 6 lines of 7 characters")

        symbols = {".": EMPTY, "X": P1, "O": P2}
        b = cls()
        try:
            b.grid = [[symbols[ch] for ch in r] for r in rows]
        except KeyError as err:
            raise ValueError(f"unknown character {err} in board text") from None

        for c in range(COLS):  # no floating pieces
            seen_piece = False
            for r in range(ROWS):
                if b.grid[r][c] != EMPTY:
                    seen_piece = True
                elif seen_piece:
                    raise ValueError(f"floating piece in column {c}")

        xs = sum(row.count(P1) for row in b.grid)
        os_ = sum(row.count(P2) for row in b.grid)
        b.num_moves = xs + os_
        if to_move is None:
            b.current_player = P1 if xs == os_ else P2
        else:
            b.current_player = {"X": P1, "O": P2}[to_move.upper()]

        for r in range(ROWS):
            for c in range(COLS):
                if b.grid[r][c] != EMPTY and b._is_win_at(r, c):
                    b._winner = b.grid[r][c]
        return b

    def __str__(self):
        symbols = {EMPTY: ".", P1: "X", P2: "O"}
        lines = ["".join(symbols[v] for v in row) for row in self.grid]
        lines.append("0123456")
        return "\n".join(lines)
