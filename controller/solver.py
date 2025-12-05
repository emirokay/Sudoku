class SudokuSolver:
    def __init__(self, board_obj):
        self.board_obj = board_obj
        self.grid = board_obj.grid

    def create_solve_generator(self):
        empty = self._find_empty()
        if not empty:
            return True

        row, col = empty

        for num in range(1, 10):
            if self._is_safe(row, col, num):
                self.grid[row][col] = num
                yield (row, col, num, "testing")

                if (yield from self.create_solve_generator()):
                    return True

                self.grid[row][col] = 0
                yield (row, col, 0, "backtrack")

        return False

    def _find_empty(self):
        for r in range(9):
            for c in range(9):
                if self.grid[r][c] == 0:
                    return (r, c)
        return None

    def _is_safe(self, row, col, num):
        if num in self.grid[row]: return False
        if num in [self.grid[i][col] for i in range(9)]: return False
        box_r, box_c = row // 3 * 3, col // 3 * 3
        for i in range(3):
            for j in range(3):
                if self.grid[box_r + i][box_c + j] == num:
                    return False
        return True