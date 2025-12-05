import random


class SudokuBoard:
    def __init__(self, given, solution):
        self.given = [row[:] for row in given]
        self.solution = [row[:] for row in solution]
        self.grid = [row[:] for row in given]
        self.notes = [[set() for _ in range(9)] for _ in range(9)]
        self.player_filled = [[False for _ in range(9)] for _ in range(9)]
        self.score = 0

    def reset(self):
        self.grid = [row[:] for row in self.given]
        self.notes = [[set() for _ in range(9)] for _ in range(9)]
        self.player_filled = [[False for _ in range(9)] for _ in range(9)]
        self.score = 0

    def is_given(self, r, c):
        return self.given[r][c] != 0

    def place_number(self, r, c, num, is_player=True):
        prev_val = self.grid[r][c]
        prev_notes = set(self.notes[r][c])
        was_correct_before = (prev_val == self.solution[r][c])

        self.grid[r][c] = num
        self.notes[r][c].clear()

        if num != 0:
            self.player_filled[r][c] = is_player
        else:
            self.player_filled[r][c] = False

        is_correct = (num == self.solution[r][c])

        if is_player:
            if is_correct:
                if not was_correct_before:
                    self.score += 1
            else:
                if was_correct_before:
                    self.score = max(0, self.score - 1)

        return {
            'type': 'place', 'r': r, 'c': c,
            'prev': prev_val, 'new': num,
            'prev_notes': prev_notes,
            'correct': is_correct,
            'player_filled': True
        }

    def erase(self, r, c):
        prev_val = self.grid[r][c]
        prev_notes = set(self.notes[r][c])
        was_correct_before = (prev_val == self.solution[r][c])

        if prev_val == 0 and not prev_notes:
            return None

        self.grid[r][c] = 0
        self.notes[r][c].clear()
        self.player_filled[r][c] = False

        if was_correct_before:
            self.score = max(0, self.score - 1)

        return {'type': 'erase', 'r': r, 'c': c, 'prev': prev_val, 'prev_notes': prev_notes}

    def toggle_note(self, r, c, num):
        if num in self.notes[r][c]:
            self.notes[r][c].remove(num)
            return {'type': 'note_remove', 'r': r, 'c': c, 'num': num}
        else:
            self.notes[r][c].add(num)
            return {'type': 'note_add', 'r': r, 'c': c, 'num': num}

    def get_random_empty_cell(self):
        empties = [(r, c) for r in range(9) for c in range(9)
                   if self.grid[r][c] == 0]
        if not empties:
            return None
        return random.choice(empties)

    def is_solved(self):
        return self.grid == self.solution