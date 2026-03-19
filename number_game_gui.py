# AI assistance information:
# Prompt used: Fix the imports in number_game_gui.py so that it works with the
# updated Game_State and AI_Agent modules. Ensure compatibility with the current
# project structure and avoid import errors.
# Model used: ChatGPT (GPT-5.3)

import tkinter as tk
from tkinter import simpledialog, messagebox, Menu
import Game_State as gs
import AI_Agent as AI

# updated imports to match Game_State and AI_Agent after recent changes
# ============================================================
# COLOR PALETTE & STYLE CONSTANTS
# A modern dark theme with accent colors for a polished look.
# ============================================================
COLORS = {
    'bg_dark':       '#1a1a2e',   # Main background (deep navy)
    'bg_card':       '#16213e',   # Card/panel background
    'bg_header':     '#0f3460',   # Header bar
    'accent_blue':   '#00adb5',   # Primary accent (teal)
    'accent_orange': '#e94560',   # Secondary accent (coral red)
    'accent_green':  '#00c897',   # Success green
    'accent_gold':   '#ffd700',   # Gold for highlights
    'text_primary':  '#eaeaea',   # Main text
    'text_secondary':'#a0a0b0',   # Dimmed text
    'text_dark':     '#1a1a2e',   # Text on light backgrounds
    'btn_1':         '#2d6a4f',   # Button color for number 1
    'btn_2':         '#457b9d',   # Button color for number 2
    'btn_3':         '#e07a5f',   # Button color for number 3
    'btn_4':         '#9b5de5',   # Button color for number 4
    'btn_hover':     '#f0e68c',   # Button hover highlight
    'btn_disabled':  '#3a3a5c',   # Disabled button
}

FONTS = {
    'title':    ('Segoe UI', 20, 'bold'),
    'score':    ('Segoe UI', 18, 'bold'),
    'status':   ('Segoe UI', 13, 'italic'),
    'number':   ('Consolas', 16, 'bold'),
    'button':   ('Segoe UI', 11),
    'small':    ('Segoe UI', 10),
    'header':   ('Segoe UI', 11, 'bold'),
}

# Map each number value to a distinct button color
NUM_COLORS = {
    1: COLORS['btn_1'],
    2: COLORS['btn_2'],
    3: COLORS['btn_3'],
    4: COLORS['btn_4'],
}


class NumberGameGUI:
    """
    Graphical User Interface for the Number String Game.
    Uses tkinter with a modern dark theme.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Number String Game — Human vs AI")
        self.root.geometry("900x520")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS['bg_dark'])

        # Game state references
        self.game_state = None
        self.ai_agent = None

        # Track number buttons for animation
        self.number_buttons = []

        # Build the UI
        self._build_header()
        self._build_scoreboard()
        self._build_status_bar()
        self._build_board_area()
        self._build_footer()

        # Launch the game setup dialog
        self.root.after(300, self.start_new_game)

    # -------------------------------------------------------
    # UI CONSTRUCTION
    # -------------------------------------------------------

    def _build_header(self):
        """Top banner with the game title."""
        header = tk.Frame(self.root, bg=COLORS['bg_header'], height=55)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="🎲  NUMBER STRING GAME  🎲",
            font=FONTS['title'],
            bg=COLORS['bg_header'],
            fg=COLORS['accent_gold'],
        ).pack(expand=True)

    def _build_scoreboard(self):
        """Score panel showing Human and AI scores side by side."""
        board = tk.Frame(self.root, bg=COLORS['bg_card'], pady=12)
        board.pack(fill=tk.X, padx=20, pady=(15, 5))

        # --- Human score (left) ---
        human_frame = tk.Frame(board, bg=COLORS['bg_card'])
        human_frame.pack(side=tk.LEFT, expand=True)

        tk.Label(
            human_frame, text="👤 HUMAN", font=FONTS['header'],
            bg=COLORS['bg_card'], fg=COLORS['accent_blue'],
        ).pack()

        self.lbl_human_score = tk.Label(
            human_frame, text="0", font=FONTS['score'],
            bg=COLORS['bg_card'], fg=COLORS['text_primary'],
        )
        self.lbl_human_score.pack()

        # --- Separator ---
        tk.Label(
            board, text="VS", font=('Segoe UI', 14, 'bold'),
            bg=COLORS['bg_card'], fg=COLORS['text_secondary'],
        ).pack(side=tk.LEFT, expand=True)

        # --- AI score (right) ---
        ai_frame = tk.Frame(board, bg=COLORS['bg_card'])
        ai_frame.pack(side=tk.RIGHT, expand=True)

        tk.Label(
            ai_frame, text="🤖 AI", font=FONTS['header'],
            bg=COLORS['bg_card'], fg=COLORS['accent_orange'],
        ).pack()

        self.lbl_ai_score = tk.Label(
            ai_frame, text="0", font=FONTS['score'],
            bg=COLORS['bg_card'], fg=COLORS['text_primary'],
        )
        self.lbl_ai_score.pack()

    def _build_status_bar(self):
        """Status label that shows whose turn it is."""
        self.lbl_status = tk.Label(
            self.root,
            text="Welcome! Setting up the game...",
            font=FONTS['status'],
            bg=COLORS['bg_dark'],
            fg=COLORS['accent_green'],
            pady=8,
        )
        self.lbl_status.pack()

    def _build_board_area(self):
        """Central area where number buttons are displayed."""
        # Outer container with a border effect
        outer = tk.Frame(self.root, bg=COLORS['accent_blue'], padx=2, pady=2)
        outer.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        self.board_canvas_frame = tk.Frame(outer, bg=COLORS['bg_card'])
        self.board_canvas_frame.pack(fill=tk.BOTH, expand=True)

        # Inner frame that will hold the number buttons (centered)
        self.numbers_frame = tk.Frame(self.board_canvas_frame, bg=COLORS['bg_card'])
        self.numbers_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def _build_footer(self):
        """Bottom bar with a New Game button and info text."""
        footer = tk.Frame(self.root, bg=COLORS['bg_dark'], pady=8)
        footer.pack(fill=tk.X, side=tk.BOTTOM)

        btn_new = tk.Button(
            footer, text="🔄  New Game", font=FONTS['button'],
            bg=COLORS['bg_header'], fg=COLORS['text_primary'],
            activebackground=COLORS['accent_blue'],
            activeforeground=COLORS['text_dark'],
            relief=tk.FLAT, padx=15, pady=4,
            command=self.start_new_game,
            cursor='hand2',
        )
        btn_new.pack(side=tk.LEFT, padx=20)

        tk.Label(
            footer, text="Minimax + Alpha-Beta Pruning AI",
            font=FONTS['small'], bg=COLORS['bg_dark'], fg=COLORS['text_secondary'],
        ).pack(side=tk.RIGHT, padx=20)

    # -------------------------------------------------------
    # GAME FLOW
    # -------------------------------------------------------

    def start_new_game(self):
        """Ask for string length and initialize a new game."""
        length = simpledialog.askinteger(
            "Game Setup",
            "Enter the length of the number string (15–20):",
            minvalue=15, maxvalue=20, parent=self.root,
        )
        if length is None:
            # User cancelled — if no game running, quit
            if self.game_state is None:
                self.root.destroy()
            return

        self.game_state = gs.GameState(length=length)
        self.ai_agent = AI.AI_Agent(player_id=2, depth_limit=4)
        self.refresh_ui()

    def refresh_ui(self):
        """Redraw all dynamic elements: scores, status, number buttons."""
        if self.game_state is None:
            return

        # --- Scores ---
        self.lbl_human_score.config(text=str(self.game_state.scores[1]))
        self.lbl_ai_score.config(text=str(self.game_state.scores[2]))

        # --- Game over check ---
        if self.game_state.is_game_over():
            self._show_winner()
            return

        # --- Status ---
        if self.game_state.current_player == 1:
            self.lbl_status.config(text="🟢  Your turn! Click a number to make a move.", fg=COLORS['accent_green'])
        else:
            self.lbl_status.config(text="🔴  AI is thinking...", fg=COLORS['accent_orange'])
            self.root.after(600, self._perform_ai_move)

        # --- Redraw number buttons ---
        self._draw_numbers()

    def _draw_numbers(self):
        """Create styled buttons for each number in the current string."""
        # Clear previous buttons
        for w in self.numbers_frame.winfo_children():
            w.destroy()
        self.number_buttons.clear()

        nums = self.game_state.numbers
        is_human_turn = (self.game_state.current_player == 1)

        # Use grid layout with wrapping (max ~10 per row for readability)
        cols = min(len(nums), 10)
        for idx, num in enumerate(nums):
            row = idx // cols
            col = idx % cols

            color = NUM_COLORS.get(num, COLORS['btn_disabled'])
            state = tk.NORMAL if is_human_turn else tk.DISABLED

            btn = tk.Button(
                self.numbers_frame,
                text=str(num),
                font=FONTS['number'],
                width=4, height=2,
                bg=color if is_human_turn else COLORS['btn_disabled'],
                fg='white',
                activebackground=COLORS['btn_hover'],
                activeforeground=COLORS['text_dark'],
                relief=tk.FLAT,
                state=state,
                cursor='hand2' if is_human_turn else 'arrow',
                command=lambda i=idx, n=num: self._on_number_click(i, n),
            )
            btn.grid(row=row, column=col, padx=4, pady=4)
            self.number_buttons.append(btn)

    # -------------------------------------------------------
    # PLAYER INTERACTION
    # -------------------------------------------------------

    def _on_number_click(self, index, number):
        """Show a context menu with available actions for the clicked number."""
        if self.game_state.current_player != 1:
            return

        menu = Menu(self.root, tearoff=0, font=FONTS['button'],
                    bg=COLORS['bg_card'], fg=COLORS['text_primary'],
                    activebackground=COLORS['accent_blue'],
                    activeforeground='white')

        # Always available: Take the number
        menu.add_command(
            label=f"✋  Take {number}  (+{number} pts)",
            command=lambda: self._apply_human_move(('take', index, number)),
        )

        # Split 2 → 1, 1  (strategic, no points)
        if number == 2:
            menu.add_command(
                label="✂️  Split 2 → 1, 1  (0 pts)",
                command=lambda: self._apply_human_move(('split2', index, 2)),
            )

        # Split 4 → 2, 2  (+1 point)
        if number == 4:
            menu.add_command(
                label="✂️  Split 4 → 2, 2  (+1 pt)",
                command=lambda: self._apply_human_move(('split4', index, 4)),
            )

        try:
            menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
        finally:
            menu.grab_release()

    def _apply_human_move(self, move):
        """Apply the human player's chosen move and refresh."""
        self.game_state.apply_move(move)
        self.refresh_ui()

    def _perform_ai_move(self):
        """Let the AI agent pick and apply a move."""
        if self.game_state is None or self.game_state.is_game_over():
            return
        move = self.ai_agent.get_best_move(self.game_state)
        if move:
            self.game_state.apply_move(move)
        self.refresh_ui()

    # -------------------------------------------------------
    # GAME END
    # -------------------------------------------------------

    def _show_winner(self):
        """Display the final result and offer to play again."""
        winner = self.game_state.get_winner()
        s1 = self.game_state.scores[1]
        s2 = self.game_state.scores[2]

        if winner == 1:
            msg = "🏆  You Win!"
            color = COLORS['accent_green']
        elif winner == 2:
            msg = "🤖  AI Wins!"
            color = COLORS['accent_orange']
        else:
            msg = "🤝  It's a Draw!"
            color = COLORS['accent_gold']

        self.lbl_status.config(text=f"GAME OVER — {msg}  (Human {s1} – AI {s2})", fg=color)

        # Clear the board
        for w in self.numbers_frame.winfo_children():
            w.destroy()

        if messagebox.askyesno("Game Over", f"{msg}\nHuman: {s1}  |  AI: {s2}\n\nPlay again?"):
            self.start_new_game()


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = NumberGameGUI(root)
    root.mainloop()
