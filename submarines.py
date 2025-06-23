# Single-file Submarines game module
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

Coordinate = Tuple[int, int, int]  # layer, row, column

@dataclass
class Piece:
    """Represents a game piece on a specific layer."""

    name: str
    level: int
    orientations: List[Set[Tuple[int, int]]]  # row, col offsets
    kill_on_first_hit: bool = False
    positions: Set[Coordinate] = field(default_factory=set)
    hits: Set[Coordinate] = field(default_factory=set)

    def place(self, origin: Coordinate, orientation: int) -> Set[Coordinate]:
        layer, row, col = origin
        offsets = self.orientations[orientation]
        return {(layer, row + r, col + c) for r, c in offsets}

    def record_hit(self, coord: Coordinate) -> bool:
        self.hits.add(coord)
        if self.kill_on_first_hit:
            return True
        return self.is_destroyed

    @property
    def is_destroyed(self) -> bool:
        return self.positions == self.hits


def submarine() -> Piece:
    offsets = [
        {(0, 1), (1, 0), (1, 1), (1, 2), (2, 1)},
        {(0, 0), (1, 0), (2, 0), (1, -1), (1, 1)},
    ]
    return Piece("Submarine", 0, offsets, kill_on_first_hit=True)


def destroyer() -> Piece:
    offsets = [
        {(0, 1), (1, 0), (1, 1), (1, 2), (2, 1)},
        {(0, 0), (1, 0), (2, 0), (1, -1), (1, 1)},
    ]
    return Piece("Destroyer", 1, offsets)


def jet() -> Piece:
    offsets = [
        {(0, 1), (1, 0), (1, 1), (1, 2), (2, 1), (3, 1)},
        {(0, 2), (1, 0), (1, 1), (1, 2), (1, 3), (2, 2)},
    ]
    return Piece("Jet", 2, offsets, kill_on_first_hit=True)


def general(level: int) -> Piece:
    offsets = [{(0, 0)}]
    return Piece("General", level, offsets, kill_on_first_hit=True)


class Board:
    """3D board that holds pieces."""

    def __init__(self, rows: int, cols: int, levels: int = 3):
        self.rows = rows
        self.cols = cols
        self.levels = levels
        self.grid: List[List[List[Optional[Piece]]]] = [
            [[None for _ in range(cols)] for _ in range(rows)] for _ in range(levels)
        ]
        self.pieces: List[Piece] = []

    def in_bounds(self, coord: Coordinate) -> bool:
        l, r, c = coord
        return 0 <= l < self.levels and 0 <= r < self.rows and 0 <= c < self.cols

    def empty(self, coord: Coordinate) -> bool:
        l, r, c = coord
        return self.grid[l][r][c] is None

    def place_random(self, piece: Piece) -> None:
        """Place a piece randomly on its designated level without overlap."""
        orientations = list(range(len(piece.orientations)))
        random.shuffle(orientations)
        for orientation in orientations:
            offsets = piece.orientations[orientation]
            possible: List[Coordinate] = []
            l = piece.level
            for r in range(self.rows):
                for c in range(self.cols):
                    cells = {(l, r + ro, c + co) for ro, co in offsets}
                    if all(self.in_bounds(cell) and self.empty(cell) for cell in cells):
                        possible.append((l, r, c))
            if possible:
                origin = random.choice(possible)
                cells = piece.place(origin, orientation)
                for cell in cells:
                    self.grid[cell[0]][cell[1]][cell[2]] = piece
                piece.positions = cells
                self.pieces.append(piece)
                return
        raise ValueError("No space to place piece")

    def fire(self, coord: Coordinate) -> str:
        if not self.in_bounds(coord):
            return "Out of bounds"
        l, r, c = coord
        target = self.grid[l][r][c]
        if target is None:
            return "Miss"
        if coord in target.hits:
            return "Already hit"
        destroyed = target.record_hit(coord)
        if destroyed:
            if target.name == "General":
                return "Kill"
            return f"Sunk {target.name}"
        return "Hit"

    def remaining_pieces(self, include_general: bool = False) -> List[Piece]:
        return [p for p in self.pieces if not p.is_destroyed and (include_general or p.name != "General")]

    def show(self, reveal: bool = False) -> None:
        for l in range(self.levels):
            print(f"Layer {l}")
            for r in range(self.rows):
                row = []
                for c in range(self.cols):
                    piece = self.grid[l][r][c]
                    if piece is None:
                        row.append(".")
                    elif reveal or (l, r, c) in piece.hits:
                        row.append("X")
                    else:
                        row.append("?")
                print(" ".join(row))
            print()


class Game:
    """High level game logic for two human players."""

    def __init__(self, rows: int, cols: int, pieces: Dict[str, int]):
        if pieces.get("General", 0) != 1:
            raise ValueError("Exactly one General required")
        self.boards = [Board(rows, cols), Board(rows, cols)]
        factories = {
            "Submarine": submarine,
            "Destroyer": destroyer,
            "Jet": jet,
        }
        for idx in range(2):
            for name, count in pieces.items():
                if name == "General":
                    continue
                for _ in range(count):
                    piece = factories[name]()
                    self.boards[idx].place_random(piece)
            level = random.randint(0, 2)
            g = general(level)
            self.boards[idx].place_random(g)
        self.turn = 0
        self.game_over = False

    def start(self) -> None:
        while not self.game_over:
            board = self.boards[1 - self.turn]
            player = self.turn + 1
            cmd = input(f"Player {player} target (l r c) or 'show' or 'quit': ")
            if cmd.strip().lower() == "quit":
                print("Game quit.")
                return
            if cmd.strip().lower() == "show":
                board.show(reveal=True)
                continue
            try:
                l, r, c = map(int, cmd.split())
            except ValueError:
                print("Invalid input")
                continue
            result = board.fire((l, r, c))
            print(result)
            if result == "Kill" or not board.remaining_pieces():
                print(f"Player {player} wins!")
                self.game_over = True
            else:
                self.turn = 1 - self.turn

__all__ = [
    "Piece",
    "Board",
    "Game",
    "submarine",
    "destroyer",
    "jet",
    "general",
]
