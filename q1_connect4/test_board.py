from pathlib import Path

import pytest

from board import COLS, EMPTY, P1, P2, ROWS, WINDOWS, Board

TEST_DATA = Path(__file__).parent / "test_data"


def play_all(moves):
    b = Board()
    for m in moves:
        b.play(m)
    return b


def test_new_board_is_empty():
    b = Board()
    assert all(cell == EMPTY for row in b.grid for cell in row)
    assert b.legal_moves() == list(range(COLS))
    assert b.current_player == P1
    assert b.winner() is None


def test_piece_lands_in_lowest_cell_and_turn_switches():
    b = Board()
    b.play(3)
    assert b.grid[ROWS - 1][3] == P1
    assert b.current_player == P2
    b.play(3)
    assert b.grid[ROWS - 2][3] == P2
    assert b.last_move == (ROWS - 2, 3)


def test_full_column_is_illegal():
    b = Board()
    for _ in range(ROWS):
        b.play(0)
    assert 0 not in b.legal_moves()
    with pytest.raises(ValueError):
        b.play(0)


def test_out_of_range_column_is_illegal():
    with pytest.raises(ValueError):
        Board().play(7)


def test_copy_is_independent():
    b = Board()
    b.play(2)
    c = b.copy()
    c.play(2)
    assert b.grid[ROWS - 2][2] == EMPTY
    assert b.num_moves == 1 and c.num_moves == 2


def test_vertical_win():
    b = play_all([0, 1, 0, 1, 0, 1, 0])
    assert b.winner() == P1 and b.is_terminal()


def test_horizontal_win():
    b = play_all([0, 0, 1, 1, 2, 2, 3])
    assert b.winner() == P1


def test_diagonal_win_up_right():
    b = play_all([0, 1, 1, 2, 3, 2, 3, 6, 2, 3, 3])
    assert b.winner() == P1


def test_diagonal_win_up_left():
    b = play_all([6, 5, 5, 4, 3, 4, 3, 0, 4, 3, 3])
    assert b.winner() == P1


def test_three_in_a_row_is_not_a_win():
    b = play_all([0, 0, 1, 1, 2])
    assert b.winner() is None and not b.is_terminal()


def test_no_moves_after_game_over():
    b = play_all([0, 1, 0, 1, 0, 1, 0])
    assert b.legal_moves() == []
    with pytest.raises(ValueError):
        b.play(2)


def test_draw_board():
    b = Board.from_text((TEST_DATA / "draw.txt").read_text())
    assert b.is_full() and b.winner() is None and b.is_draw() and b.is_terminal()


def test_from_text_reads_position():
    b = Board.from_text((TEST_DATA / "win_in_one.txt").read_text())
    assert b.grid[ROWS - 1][0] == P1 and b.grid[ROWS - 2][0] == P2
    assert b.current_player == P1
    assert b.num_moves == 6


def test_from_text_finds_existing_win():
    text = "\n".join([".......", ".......", ".......", ".......", ".......", "XXXX..."])
    assert Board.from_text(text).winner() == P1


def test_from_text_rejects_floating_piece():
    text = "\n".join([".......", ".......", ".......", "X......", ".......", "......."])
    with pytest.raises(ValueError):
        Board.from_text(text)


def test_from_text_rejects_wrong_size():
    with pytest.raises(ValueError):
        Board.from_text("XXX\nOOO")


def test_there_are_69_windows():
    assert len(WINDOWS) == 69
