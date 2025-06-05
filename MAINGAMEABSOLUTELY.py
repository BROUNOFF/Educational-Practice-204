import tkinter as tk
import random
import string
from tkinter import messagebox

class MemoryTrainer:
    def __init__(self, root):
        self.root = root
        self.root.title("Memory Trainer")
        self.sequence = []
        self.user_input = []
        self.score = 0
        self.difficulty = 700
        self.grid_buttons = []
        self.grid_size = 3
        self.sound_on = True
        self.input_enabled = False
        self.is_paused = False
        self.sequence_task_ids = []
        self.pause_overlay = None
        self.pause_cooldown = False
        self.timer_seconds = 0
        self.timer_task_id = None

        self.bg_color = "#f0f4f8"
        self.btn_color = "#4a90e2"
        self.btn_hover = "#357ab7"
        self.text_color = "#ffffff"

        self.root.configure(bg=self.bg_color)

        self.main_menu_frame = None
        self.game_frame = None
        self.button_width = 20

        self.create_main_menu()

    def make_styled_button(self, parent, text, command, small=False):
        font_size = 10 if small else 14
        btn = tk.Button(parent, text=text, command=command,
                        bg=self.btn_color, fg=self.text_color,
                        activebackground=self.btn_hover, activeforeground=self.text_color,
                        font=("Arial", font_size, "bold"),
                        relief="flat", padx=10, pady=5,
                        width=self.button_width)
        btn.pack(pady=5)
        return btn

    def create_main_menu(self):
        self.clear_window()
        self.main_menu_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_menu_frame.pack(padx=20, pady=20)

        tk.Label(self.main_menu_frame, text="Memory Trainer", font=("Arial", 26, "bold"),
                 bg=self.bg_color, fg="#2c3e50").pack(pady=10)

        self.make_styled_button(self.main_menu_frame, "Начать тренировку", self.select_grid_size)
        self.make_styled_button(self.main_menu_frame, "Настройки", self.open_settings)
        self.make_styled_button(self.main_menu_frame, "Выход", self.root.quit)

    def select_grid_size(self):
        self.clear_window()
        frame = tk.Frame(self.root, bg=self.bg_color)
        frame.pack(padx=20, pady=20)

        tk.Label(frame, text="Выберите размер сетки", font=("Arial", 20, "bold"),
                 bg=self.bg_color, fg="#2c3e50").pack(pady=10)

        for size in [3, 4, 5]:
            self.make_styled_button(frame, f"{size} x {size}", lambda s=size: self.start_game_ui(s))

        self.make_styled_button(frame, "Назад", self.create_main_menu)

    def start_game_ui(self, size):
        self.grid_size = size
        self.clear_window()
        self.score = 0
        self.sequence = []
        self.user_input = []
        self.is_paused = False
        self.sequence_task_ids.clear()
        self.pause_cooldown = False
        self.timer_seconds = 0

        self.game_frame = tk.Frame(self.root, bg=self.bg_color)
        self.game_frame.pack()

        difficulty_frame = tk.Frame(self.game_frame, bg=self.bg_color)
        difficulty_frame.pack(pady=10)

        tk.Button(difficulty_frame, text="Легко", command=lambda: self.set_difficulty(800, "Легко"),
                  font=("Arial", 10, "bold"), bg=self.btn_color, fg=self.text_color,
                  activebackground=self.btn_hover, relief="flat", padx=10, pady=5,
                  width=12).pack(side="left", padx=5)

        tk.Button(difficulty_frame, text="Нормально", command=lambda: self.set_difficulty(400, "Нормально"),
                  font=("Arial", 10, "bold"), bg=self.btn_color, fg=self.text_color,
                  activebackground=self.btn_hover, relief="flat", padx=10, pady=5,
                  width=12).pack(side="left", padx=5)

        tk.Button(difficulty_frame, text="Сложно", command=lambda: self.set_difficulty(200, "Сложно"),
                  font=("Arial", 10, "bold"), bg=self.btn_color, fg=self.text_color,
                  activebackground=self.btn_hover, relief="flat", padx=10, pady=5,
                  width=12).pack(side="left", padx=5)

        self.difficulty_label = tk.Label(self.game_frame, text="", bg=self.bg_color,
                                         fg="#2c3e50", font=("Arial", 12, "bold"))
        self.difficulty_label.pack(pady=(0, 10))

        self.timer_label = tk.Label(self.game_frame, text="Время: 00:00", font=("Arial", 14),
                                    bg=self.bg_color, fg="#2c3e50")
        self.timer_label.pack(pady=5)

        self.update_timer_label()

        self.hint_label = tk.Label(self.game_frame, text="", font=("Arial", 12),
                                   bg=self.bg_color, fg="#27ae60")
        self.hint_label.pack(pady=2)

        self.set_difficulty(self.difficulty, "Средне")

        self.grid_buttons = []
        grid_frame = tk.Frame(self.game_frame, bg=self.bg_color)
        grid_frame.pack(pady=10)
        for i in range(size * size):
            btn = tk.Button(grid_frame, text=random.choice(string.ascii_uppercase), font=("Arial", 18),
                            width=4, height=2, command=lambda i=i: self.handle_input(i),
                            bg="#ffffff", fg="#2c3e50", activebackground="#e1ecf4")
            btn.grid(row=i // size, column=i % size, padx=5, pady=5)
            self.grid_buttons.append(btn)

        self.score_label = tk.Label(self.game_frame, text=f"Очки: {self.score}",
                                    font=("Arial", 14), bg=self.bg_color, fg="#2c3e50")
        self.score_label.pack(pady=10)

        self.start_btn = self.make_styled_button(self.game_frame, "Старт", self.start_round)
        self.pause_btn = self.make_styled_button(self.game_frame, "Пауза", self.toggle_pause)
        self.pause_btn.config(state="disabled")
        self.make_styled_button(self.game_frame, "В меню", self.create_main_menu)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def set_difficulty(self, speed, label):
        self.difficulty = speed
        if hasattr(self, "difficulty_label"):
            self.difficulty_label.config(text=f"Текущая сложность: {label}")

    def start_round(self):
        if self.is_paused:
            return
        self.start_btn.config(state="disabled")
        self.pause_btn.config(state="disabled")
        self.user_input = []
        self.input_enabled = False
        self.sequence_task_ids.clear()
        self.sequence.append(random.randint(0, len(self.grid_buttons) - 1))
        self.show_sequence()

    def show_sequence(self):
        for btn in self.grid_buttons:
            btn.config(state="disabled")
        self.pause_btn.config(state="disabled")
        self.hint_label.config(text="")

        def flash(index):
            if self.is_paused:
                return
            btn = self.grid_buttons[index]
            original = btn.cget("background")
            btn.config(bg="#f7dc6f")
            if self.sound_on:
                self.root.bell()
            task_id = self.root.after(self.difficulty, lambda: btn.config(bg=original))
            self.sequence_task_ids.append(task_id)

        for i, index in enumerate(self.sequence):
            task_id = self.root.after(i * self.difficulty * 2, lambda idx=index: flash(idx))
            self.sequence_task_ids.append(task_id)

        total_time = len(self.sequence) * self.difficulty * 2
        final_task = self.root.after(total_time, self.enable_input)
        self.sequence_task_ids.append(final_task)

    def enable_input(self):
        if not self.is_paused:
            self.input_enabled = True
            for btn in self.grid_buttons:
                btn.config(state="normal")
            self.pause_btn.config(state="normal")
            self.hint_label.config(text="Можно нажимать")
            self.start_timer()

    def handle_input(self, index):
        if not self.input_enabled or self.is_paused:
            return
        if len(self.user_input) >= len(self.sequence):
            return

        self.user_input.append(index)
        if self.sequence[len(self.user_input) - 1] != index:
            self.stop_timer()
            minutes = self.timer_seconds // 60
            seconds = self.timer_seconds % 60
            messagebox.showinfo("Ошибка", f"Неправильно!\nОчки: {self.score}\nВремя: {minutes:02d}:{seconds:02d}")
            self.sequence.clear()
            self.user_input.clear()
            self.score = 0
            self.timer_seconds = 0
            self.update_timer_label()
            self.score_label.config(text=f"Очки: {self.score}")
            self.input_enabled = False
            self.start_btn.config(state="normal")
            self.pause_btn.config(state="disabled")
            self.is_paused = False
            self.clear_pause_overlay()
            self.pause_cooldown = False
        elif len(self.user_input) == len(self.sequence):
            self.score += 1
            self.score_label.config(text=f"Очки: {self.score}")
            self.input_enabled = False
            self.pause_btn.config(state="disabled")
            self.hint_label.config(text="")
            self.root.after(1000, self.start_round)

    def toggle_pause(self):
        if self.pause_cooldown:
            return
        if not self.is_paused:
            self.is_paused = True
            self.pause_btn.config(text="Продолжить")
            self.input_enabled = False
            for task_id in self.sequence_task_ids:
                self.root.after_cancel(task_id)
            self.sequence_task_ids.clear()
            self.stop_timer()
            self.pause_overlay = tk.Frame(self.root, bg="black")
            self.pause_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

            self.resume_button = tk.Button(self.pause_overlay, text="Продолжить", command=self.resume_from_pause,
                                           bg="#4CAF50", fg="white", font=("Arial", 20, "bold"),
                                           padx=20, pady=10)
            self.resume_button.place(relx=0.5, rely=0.5, anchor="center")
            for btn in self.grid_buttons:
                btn.config(state="disabled")
            self.hint_label.config(text="")
        else:
            self.resume_from_pause()
        self.pause_cooldown = True
        self.root.after(1500, lambda: setattr(self, 'pause_cooldown', False))

    def resume_from_pause(self):
        if not self.is_paused:
            return
        self.is_paused = False
        self.pause_btn.config(text="Пауза")
        self.enable_input()
        self.clear_pause_overlay()

    def clear_pause_overlay(self):
        if self.pause_overlay:
            self.pause_overlay.destroy()
            self.pause_overlay = None

    def update_timer(self):
        if self.is_paused or not self.input_enabled:
            return
        self.timer_seconds += 1
        self.update_timer_label()
        self.timer_task_id = self.root.after(1000, self.update_timer)

    def update_timer_label(self):
        minutes = self.timer_seconds // 60
        seconds = self.timer_seconds % 60
        self.timer_label.config(text=f"Время: {minutes:02d}:{seconds:02d}")

    def start_timer(self):
        if not self.is_paused and self.input_enabled:
            self.update_timer()

    def stop_timer(self):
        if self.timer_task_id is not None:
            self.root.after_cancel(self.timer_task_id)
            self.timer_task_id = None

    def open_settings(self):
        self.clear_window()
        settings_frame = tk.Frame(self.root, bg=self.bg_color)
        settings_frame.pack(padx=20, pady=20)

        tk.Label(settings_frame, text="Настройки", font=("Arial", 24, "bold"),
                 bg=self.bg_color, fg="#2c3e50").pack(pady=10)

        sound_text = "Включить звук" if not self.sound_on else "Выключить звук"
        self.sound_btn = self.make_styled_button(settings_frame, sound_text, self.toggle_sound, small=True)

        self.make_styled_button(settings_frame, "Назад", self.create_main_menu, small=True)

    def toggle_sound(self):
        self.sound_on = not self.sound_on
        text = "Включить звук" if not self.sound_on else "Выключить звук"
        self.sound_btn.config(text=text)

if __name__ == "__main__":
    root = tk.Tk()
    app = MemoryTrainer(root)
    root.mainloop()
