import pygame
from settings import *

class Renderer:
    def __init__(self, screen, game_state, board):
        self.screen = screen
        self.gs = game_state
        self.board = board

        self.font_xl = pygame.font.SysFont("arial", int(HEIGHT * 0.08))
        self.font_lg = pygame.font.SysFont("arial", 40)
        self.font_md = pygame.font.SysFont("arial", 20)
        self.font_sm = pygame.font.SysFont("arial", 16)
        self.font_bold = pygame.font.SysFont("arial", 16, bold=True)

        self.tool_rects = []
        self.num_rects = []
        self.pause_rects = []

        self.board_start_y = int(HEIGHT * 0.1)
        self.board_padding = int(WIDTH * 0.03)
        max_board_size = min(WIDTH - 2*self.board_padding, HEIGHT - self.board_start_y - int(HEIGHT*0.28))
        self.cell_size = max_board_size // 9
        self.board_size = self.cell_size * 9
        self.board_start_x = (WIDTH - self.board_size) // 2

    def draw(self):
        self.screen.fill(WHITE)
        self._draw_stats()
        self._draw_board()
        self._draw_toolbar()
        self._draw_numpad()
        self._draw_labels()

        if self.gs.overlay_visible:
            self._draw_overlay()

        pygame.display.flip()

    def _draw_labels(self):
        surf = self.font_sm.render("Solve (L)", True, GRAY_DARK)
        surf2 = self.font_sm.render("Menu (ESC)", True, GRAY_DARK)
        y = self.board_start_y + self.board_size + 180
        x = WIDTH - surf.get_width() - 20
        self.screen.blit(surf, (x, y))
        self.screen.blit(surf2, (20, y))

    def _draw_stats(self):
        labels = ["Date", "Mistakes", "Score", "Time"]
        values = [
            self.gs.get_date_str(),
            f"{self.gs.mistakes}/{MAX_MISTAKES}",
            str(self.board.score),
            self.gs.get_time_str()
        ]

        label_y = int(HEIGHT * 0.012)
        value_y = label_y + 20

        total_w = sum(self.font_sm.size(l)[0] for l in labels)
        remaining = WIDTH - (2 * int(WIDTH * 0.1)) - total_w
        spacing = remaining // 3

        x = int(WIDTH * 0.1)
        for i in range(4):
            l_surf = self.font_sm.render(labels[i], True, BLACK)
            v_surf = self.font_sm.render(values[i], True, BLACK)

            lx = x
            vx = x + (l_surf.get_width() - v_surf.get_width()) // 2

            self.screen.blit(l_surf, (lx, label_y))
            self.screen.blit(v_surf, (vx, value_y))

            x += l_surf.get_width() + spacing

    def _draw_board(self):
        sr, sc = self.gs.selected_cell
        sel_val = self.board.grid[sr][sc]

        for i in range(9):
            self._draw_cell_bg(sr, i, BLUE_HIGHLIGHT, 120)
            self._draw_cell_bg(i, sc, BLUE_HIGHLIGHT, 120)

        if sel_val != 0:
            for r in range(9):
                for c in range(9):
                    if self.board.grid[r][c] == sel_val and (r, c) != (sr, sc):
                        self._draw_cell_bg(r, c, BLUE_SAME_NUM, 250)

        self._draw_cell_bg(sr, sc, BLUE_SELECTED, 200)

        pygame.draw.rect(self.screen, BLACK, (self.board_start_x, self.board_start_y, self.board_size, self.board_size), 3)
        for i in range(1, 9):
            thick = 3 if i % 3 == 0 else 1
            pos = i * self.cell_size
            pygame.draw.line(self.screen, BLACK,
                             (self.board_start_x + pos, self.board_start_y),
                             (self.board_start_x + pos, self.board_start_y + self.board_size), thick)
            pygame.draw.line(self.screen, BLACK,
                             (self.board_start_x, self.board_start_y + pos),
                             (self.board_start_x + self.board_size, self.board_start_y + pos), thick)

        for r in range(9):
            for c in range(9):
                val = self.board.grid[r][c]
                cx = self.board_start_x + c * self.cell_size
                cy = self.board_start_y + r * self.cell_size

                if val != 0:
                    if self.board.is_given(r, c):
                        color = BLACK
                    elif self.gs.is_solving:
                        color = BLUE_SOLVER
                    elif val == self.board.solution[r][c]:
                        color = GREEN_SUCCESS
                    else:
                        color = RED_ERROR

                    surf = self.font_lg.render(str(val), True, color)
                    self.screen.blit(surf, (cx + (self.cell_size - surf.get_width()) // 2,
                                            cy + (self.cell_size - surf.get_height()) // 2))
                else:
                    notes = sorted(list(self.board.notes[r][c]))
                    if not notes: continue

                    inner_cell = self.cell_size // 3 -2
                    for n in notes:
                        nx = (n - 1) % 3 + 0.25
                        ny = (n - 1) // 3 + 0.25
                        font = self.font_bold if (sel_val == n) else self.font_sm
                        col = BLACK if (sel_val == n) else GRAY_TEXT

                        nsurf = font.render(str(n), True, col)
                        self.screen.blit(nsurf, (cx + nx * inner_cell + (inner_cell - nsurf.get_width()) // 2,
                                                 cy + ny * inner_cell + (inner_cell - nsurf.get_height()) // 2))

    def _draw_cell_bg(self, r, c, color, alpha):
        s = pygame.Surface((self.cell_size, self.cell_size))
        s.set_alpha(alpha)
        s.fill(color)
        self.screen.blit(s, (self.board_start_x + c * self.cell_size,
                             self.board_start_y + r * self.cell_size))

    def _draw_toolbar(self):
        self.tool_rects = []
        labels = ["Undo (U)", "Erase (E)", "Notes (N)", "Hint (H)"]

        tool_y = self.board_start_y + self.board_size + 30

        total_w = sum(self.font_md.size(l)[0] for l in labels)
        side_pad = int(WIDTH * 0.07)
        remaining = WIDTH - 2 * side_pad - total_w
        spacing = remaining // (len(labels) - 1)

        x = side_pad
        for l in labels:
            surf = self.font_md.render(l, True, GRAY_DARK)
            rect = pygame.Rect(x - 10, tool_y - 10, surf.get_width() + 20, surf.get_height() + 20)
            pygame.draw.rect(self.screen, GRAY_LIGHT, rect, border_radius=15)
            self.screen.blit(surf, (x, tool_y))

            self.tool_rects.append((rect, l))

            if l == "Hint (H)":
                left = MAX_HINTS - self.gs.hints_used
                self._draw_badge(rect, str(left))
            if l == "Notes (N)":
                self._draw_badge(rect, "ON" if self.gs.notes_mode else "OFF")

            x += surf.get_width() + spacing

    def _draw_badge(self, parent_rect, text):
        surf = self.font_sm.render(text, True, BLACK)
        w = surf.get_width() + 8
        h = surf.get_height() + 4
        bx = parent_rect.right - w + 10
        by = parent_rect.top - 10
        pygame.draw.rect(self.screen, BLUE_SAME_NUM, (bx, by, w, h), border_radius=5)
        self.screen.blit(surf, (bx + 4, by + 2))

    def _draw_numpad(self):
        self.num_rects = []
        y = self.board_start_y + self.board_size + 80
        col_w = WIDTH // 9

        for i in range(1, 10):
            count = sum(row.count(i) for row in self.board.grid)
            color = GRAY_LIGHT if count >= 9 else GRAY_DARK

            surf = self.font_xl.render(str(i), True, color)
            cx = col_w * (i - 1) + col_w // 2 - surf.get_width() // 2

            self.screen.blit(surf, (cx, y))
            rect = pygame.Rect(cx - 5, y - 5, surf.get_width() + 10, surf.get_height() + 10)
            self.num_rects.append((rect, i))

    def _draw_overlay(self):
        s = pygame.Surface((WIDTH, HEIGHT))
        s.set_alpha(240)
        s.fill(WHITE)
        self.screen.blit(s, (0, 0))

        if self.gs.paused and not self.gs.game_over:
            title = "PAUSED"
            options = ["(ESC) Resume", "(R) Restart", "(Q) Quit"]

        elif (self.gs.game_over and self.gs.mistakes >= MAX_MISTAKES) or (self.gs.game_over and self.gs.solved_by_solver):
            title = "GAME OVER"
            options = ["(R) Restart", "(Q) Quit"]

        elif self.gs.game_over and not self.gs.solved_by_solver:
            title = "YOU WON!"
            options = ["(R) Restart", "(Q) Quit"]

        else:
            return

        t_surf = self.font_xl.render(title, True, BLACK)
        self.screen.blit(t_surf, ((WIDTH - t_surf.get_width()) // 2, HEIGHT // 2 - 100))

        self.pause_rects = []
        y = HEIGHT // 2
        for opt in options:
            surf = self.font_lg.render(opt, True, BLACK)
            x = (WIDTH - surf.get_width()) // 2
            self.screen.blit(surf, (x, y))
            self.pause_rects.append((pygame.Rect(x, y, surf.get_width(), surf.get_height()), opt))
            y += 60

    def get_cell_from_pos(self, pos):
        x, y = pos
        if (self.board_start_x <= x <= self.board_start_x + self.board_size and
                self.board_start_y <= y <= self.board_start_y + self.board_size):
            row = int((y - self.board_start_y) // self.cell_size)
            col = int((x - self.board_start_x) // self.cell_size)
            return max(0, min(8, row)), max(0, min(8, col))
        return None