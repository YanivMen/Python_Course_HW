# Submarines Game

This project implements a simple two-player "Submarines" game (a 3D variant of Battleship) in a single Python module (`submarines.py`).

## Usage

```
from submarines import Game

pieces = {
    "Submarine": 2,
    "Destroyer": 1,
    "Jet": 1,
    "General": 1,
}

game = Game(rows=6, cols=6, pieces=pieces)
# Start interactive game (two players at same keyboard)
# Commands during the game:
#  - "l r c" to fire at layer l, row r, column c
#  - "show" to reveal the opponent board
#  - "quit" to stop playing

game.start()
```
