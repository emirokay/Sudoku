from view.renderer import Renderer
from controller.solver import SudokuSolver
from settings import *

class GameController:
    def __init__(self, screen, game_state, board):
        self.screen = screen
        self.gs = game_state
        self.board = board
        self.renderer = Renderer(screen, game_state, board)
        self.solver_generator = None
        self.solver_timer = pygame.time.get_ticks()

    def run(self):
        clock = pygame.time.Clock()
        while self.gs.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gs.running = False
                self._handle_input(event)

            if self.gs.is_solving and self.solver_generator:
                current_time = pygame.time.get_ticks()
                if current_time - self.solver_timer > SOLVER_DELAY_MS:
                    try:
                        next(self.solver_generator)
                        self.solver_timer = current_time
                    except StopIteration:
                        self.gs.is_solving = False
                        self._check_win_condition()

            self.renderer.draw()
            clock.tick(FPS)

    def _check_win_condition(self):
        if self.board.is_solved():
            self.gs.game_over = True
            self.gs.freeze_time()

            if self.gs.solved_by_solver:
                self.gs.overlay_visible = False
            else:
                self.gs.overlay_visible = True

    def _handle_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.gs.game_over:
                self.gs.overlay_visible = not self.gs.overlay_visible
                return

            self.gs.overlay_visible = not self.gs.overlay_visible
            self.gs.paused = self.gs.overlay_visible
            self.gs.toggle_pause()
            return

        if self.gs.overlay_visible:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                for rect, action in self.renderer.pause_rects:
                    if rect.collidepoint(mx, my):
                        if action == "(ESC) Resume":
                            self.gs.overlay_visible = False
                            self.gs.paused = False
                        elif action == "(R) Restart":
                            self._restart()
                        elif action == "(Q) Quit":
                            self.gs.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: self._restart()
                if event.key == pygame.K_q: self.gs.running = False
            return

        if self.gs.game_over or self.gs.is_solving:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            for rect, action in self.renderer.tool_rects:
                if rect.collidepoint(mx, my):
                    if action == "Undo (U)":
                        self._undo()
                    elif action == "Erase (E)":
                        self._erase_cell()
                    elif action == "Notes (N)":
                        self.gs.notes_mode = not self.gs.notes_mode
                    elif action == "Hint (H)":
                        self._hint()
                    return

            for rect, num in self.renderer.num_rects:
                if rect.collidepoint(mx, my):
                    self._place_number(num)
                    return

            cell = self.renderer.get_cell_from_pos(event.pos)
            if cell:
                self.gs.selected_cell = cell

        pygame.key.set_repeat(300, 100)
        if event.type == pygame.KEYDOWN:
            r, c = self.gs.selected_cell

            if event.key == pygame.K_UP:
                r = max(0, r - 1)
            elif event.key == pygame.K_DOWN:
                r = min(8, r + 1)
            elif event.key == pygame.K_LEFT:
                c = max(0, c - 1)
            elif event.key == pygame.K_RIGHT:
                c = min(8, c + 1)
            self.gs.selected_cell = (r, c)

            if event.key == pygame.K_n:
                self.gs.notes_mode = not self.gs.notes_mode
            if event.key in (pygame.K_e, pygame.K_BACKSPACE, pygame.K_DELETE, pygame.K_0):
                self._erase_cell()
            if event.key == pygame.K_u:
                self._undo()
            if event.key == pygame.K_h:
                self._hint()
            if event.key == pygame.K_l:
                self._start_solver()

            if event.unicode.isdigit() and event.unicode != '0':
                self._place_number(int(event.unicode))

    def _place_number(self, num):
        r, c = self.gs.selected_cell
        if self.board.is_given(r, c): return

        if self.gs.notes_mode:
            action = self.board.toggle_note(r, c, num)
            self.gs.undo_stack.append(action)
        else:
            action = self.board.place_number(r, c, num)
            self.gs.undo_stack.append(action)
            if not action['correct']:
                self.gs.add_mistake()

            self._check_win_condition()

    def _erase_cell(self):
        r, c = self.gs.selected_cell
        if self.board.is_given(r, c): return
        action = self.board.erase(r, c)
        if action:
            self.gs.undo_stack.append(action)

    def _undo(self):
        if not self.gs.undo_stack: return
        action = self.gs.undo_stack.pop()
        r, c = action['r'], action['c']

        if action['type'] == 'place':
            self.board.grid[r][c] = action['prev']
            self.board.notes[r][c] = action['prev_notes']
            self.board.player_filled[r][c] = (action['prev'] != 0)

            if action['prev'] == self.board.solution[r][c] and action['new'] != action['prev']:
                self.board.score += 1
            if action['correct'] and action['new'] == self.board.solution[r][c]:
                self.board.score = max(0, self.board.score - 1)

        elif action['type'] == 'erase':
            self.board.grid[r][c] = action['prev']
            self.board.notes[r][c] = action['prev_notes']
            self.board.player_filled[r][c] = True

            if action['prev'] == self.board.solution[r][c]:
                self.board.score += 1

        elif action['type'] == 'note_add':
            self.board.notes[r][c].remove(action['num'])
        elif action['type'] == 'note_remove':
            self.board.notes[r][c].add(action['num'])

        self._check_win_condition()

    def _hint(self):
        if self.gs.hints_used >= MAX_HINTS: return

        cell = self.board.get_random_empty_cell()
        if not cell: return

        r, c = cell
        correct_val = self.board.solution[r][c]

        self.board.place_number(r, c, correct_val, is_player=False)
        self.gs.hints_used += 1

        self._check_win_condition()

    def _start_solver(self):
        self._restart()
        self.gs.is_solving = True
        self.gs.solved_by_solver = True
        self.solver_timer = pygame.time.get_ticks()
        solver = SudokuSolver(self.board)
        self.solver_generator = solver.create_solve_generator()

    def _restart(self):
        self.board.reset()
        self.gs.reset()