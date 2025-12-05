import time
from settings import MAX_MISTAKES

class GameState:
    def __init__(self):
        self.running = True
        self.paused = False
        self.game_over = False
        self.is_solving = False
        self.solved_by_solver = False

        self.overlay_visible = False  # NEW

        self.notes_mode = False
        self.selected_cell = (0, 0)

        self.mistakes = 0
        self.hints_used = 0
        self.undo_stack = []

        self.start_time = time.time()
        self.pause_start = None
        self.total_pause_time = 0
        self.time_frozen_at = None  # NEW

    def toggle_pause(self):
        if self.paused:
            self.pause_start = time.time()
        else:
            if self.pause_start:
                self.total_pause_time += time.time() - self.pause_start
                self.pause_start = None

    def freeze_time(self):
        if self.time_frozen_at is None:
            self.time_frozen_at = time.time() - self.start_time - self.total_pause_time

    def get_time_str(self):
        if self.game_over and self.time_frozen_at is not None:
            elapsed = int(self.time_frozen_at)
        elif self.paused and self.pause_start:
            elapsed = int(self.pause_start - self.start_time - self.total_pause_time)
        else:
            elapsed = int(time.time() - self.start_time - self.total_pause_time)

        elapsed = max(0, elapsed)
        mins = elapsed // 60
        secs = elapsed % 60
        return f"{mins:02d}:{secs:02d}"

    def get_date_str(self):
        return time.strftime("%Y-%m-%d", time.localtime())

    def add_mistake(self):
        self.mistakes += 1
        if self.mistakes >= MAX_MISTAKES:
            self.game_over = True
            self.paused = False
            self.freeze_time()
            self.overlay_visible = True

    def reset(self):
        self.__init__()
