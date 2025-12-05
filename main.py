import pygame
import pandas as pd
import random
from settings import WIDTH, HEIGHT
from model.board import SudokuBoard
from model.game_state import GameState
from controller.game_controller import GameController

"""
 - TODO - 
little menu 
new game sudoku 
GAME OVER stats 

DONE notes size
DONE L for backtracking label
DONE hold keyboard keys
DONE pause freeze time  
"""

def load_puzzle():
    default_given = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]

    default_sol = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9]
    ]

    try:
        df = pd.read_csv("sudoku.csv", header=None)
        idx = random.randint(0, len(df) - 1)
        given_str = str(df.iloc[idx, 0])
        sol_str = str(df.iloc[idx, 1])

        if len(given_str) < 81 or len(sol_str) < 81: raise ValueError("Data too short")

        given = [[int(given_str[i * 9 + j]) for j in range(9)] for i in range(9)]
        sol = [[int(sol_str[i * 9 + j]) for j in range(9)] for i in range(9)]
        return given, sol
    except Exception as e:
        print(f"Loaded default puzzle (Reason: {e})")
        return default_given, default_sol


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sudoku")

    given, solution = load_puzzle()

    board = SudokuBoard(given, solution)
    gs = GameState()
    controller = GameController(screen, gs, board)

    controller.run()
    pygame.quit()