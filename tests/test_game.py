import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import submarines as sub


def test_random_placement_no_overlap():
    b = sub.Board(5, 5)
    for _ in range(2):
        b.place_random(sub.submarine())
    for _ in range(2):
        b.place_random(sub.destroyer())
    b.place_random(sub.general(0))
    occupied = set()
    for piece in b.pieces:
        assert piece.positions.isdisjoint(occupied)
        occupied |= piece.positions
        for coord in piece.positions:
            assert b.grid[coord[0]][coord[1]][coord[2]] is piece


def test_general_hit_ends_game():
    pieces = {"Submarine": 0, "Destroyer": 0, "Jet": 0, "General": 1}
    game = sub.Game(3, 3, pieces)
    board = game.boards[1]
    # find general position
    general_piece = next(p for p in board.pieces if p.name == "General")
    coord = next(iter(general_piece.positions))
    result = board.fire(coord)
    assert result == "Kill"
    assert general_piece.is_destroyed


def test_fire_out_of_bounds():
    b = sub.Board(3, 3)
    result = b.fire((10, 10, 10))
    assert result == "Out of bounds"
