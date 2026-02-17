"""
Isolation (Isola) Board Game
=============================
A two-player strategy game played on a 7x7 grid.
Players move like a chess Queen (horizontal, vertical, diagonal).
After each move the square you left is destroyed — no one can step on it again.
The player who cannot move loses.

This file contains:
    1. IsolationGame  — game state and rules
    2. AIAgent        — Minimax with Alpha-Beta Pruning
    3. IsolationGUI   — Tkinter graphical interface
"""

import tkinter as tk          # Standard Python GUI library
from tkinter import messagebox  # For showing game-over pop-ups
import copy                    # For deep-copying the game state inside AI search


# =============================================================================
# 1. GAME LOGIC CLASS
# =============================================================================
class IsolationGame:
    """
    Holds the board state and enforces the rules of Isolation.

    Board encoding:
        0  = empty (available square)
       -1  = destroyed (no one can go here)
        1  = Player 1 (human)
        2  = Player 2 (AI)
    """

    def __init__(self, board_size=7):
        """
        Initialise a new game.

        Parameters
        ----------
        board_size : int
            Width and height of the square board (default 7).
        """
        # Store the board dimensions
        self.board_size = board_size

        # Create a 2-D list filled with zeros (all squares empty)
        self.board = [[0] * board_size for _ in range(board_size)]

        # Place Player 1 (human) at the top-left area
        self.player_pos = [0, 0]

        # Place Player 2 (AI) at the bottom-right area
        self.ai_pos = [board_size - 1, board_size - 1]

        # Mark starting positions on the board
        self.board[self.player_pos[0]][self.player_pos[1]] = 1  # Human
        self.board[self.ai_pos[0]][self.ai_pos[1]] = 2          # AI

        # Track whose turn it is: True = human's turn, False = AI's turn
        self.is_player_turn = True

    # -------------------------------------------------------------------------
    def get_legal_moves(self, position):
        """
        Return every square reachable from *position* using Queen-style movement.

        The Queen can slide any number of squares in 8 directions (up, down,
        left, right, and four diagonals) but must stop before hitting a wall,
        a destroyed square, or the other player.

        Parameters
        ----------
        position : list[int, int]
            [row, col] of the piece to move.

        Returns
        -------
        list[list[int, int]]
            A list of [row, col] pairs the piece can legally move to.
        """
        # All eight directions: (row_delta, col_delta)
        directions = [
            (-1,  0),  # Up
            ( 1,  0),  # Down
            ( 0, -1),  # Left
            ( 0,  1),  # Right
            (-1, -1),  # Up-Left   (diagonal)
            (-1,  1),  # Up-Right  (diagonal)
            ( 1, -1),  # Down-Left (diagonal)
            ( 1,  1),  # Down-Right(diagonal)
        ]

        # Collect all legal destination squares here
        moves = []

        # Try every direction
        for dr, dc in directions:
            # Start one step away from the current position
            r, c = position[0] + dr, position[1] + dc

            # Keep sliding in this direction as long as we stay on the board
            # and the square is empty (value == 0)
            while 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == 0:
                # This square is reachable — add it
                moves.append([r, c])
                # Slide one more step in the same direction
                r += dr
                c += dc

        # Return the complete list of reachable squares
        return moves

    # -------------------------------------------------------------------------
    def make_move(self, position, new_position):
        """
        Move a piece from *position* to *new_position*.

        Steps:
            1. Destroy the old square (set to -1).
            2. Place the piece on the new square.
            3. Update the stored position for that player.
            4. Switch the turn.

        Parameters
        ----------
        position : list[int, int]
            Current [row, col] of the piece.
        new_position : list[int, int]
            Target [row, col] to move to.
        """
        # Get the piece value at the old position (1 or 2)
        piece = self.board[position[0]][position[1]]

        # Destroy the old square so nobody can use it again
        self.board[position[0]][position[1]] = -1

        # Place the piece on the new square
        self.board[new_position[0]][new_position[1]] = piece

        # Update the internal position tracker for the correct player
        if piece == 1:
            # Human moved
            self.player_pos = list(new_position)
        else:
            # AI moved
            self.ai_pos = list(new_position)

        # Switch the turn flag
        self.is_player_turn = not self.is_player_turn

    # -------------------------------------------------------------------------
    def is_game_over(self):
        """
        Check whether the game has ended.

        The game is over when the player whose turn it is has zero legal moves.

        Returns
        -------
        bool
            True if the current player cannot move, False otherwise.
        """
        # Determine whose turn it is right now
        if self.is_player_turn:
            # It is the human's turn — check their available moves
            return len(self.get_legal_moves(self.player_pos)) == 0
        else:
            # It is the AI's turn — check AI's available moves
            return len(self.get_legal_moves(self.ai_pos)) == 0

    # -------------------------------------------------------------------------
    def clone(self):
        """
        Create a deep copy of the current game state.

        This is used by the AI so it can simulate future moves without
        modifying the real game.

        Returns
        -------
        IsolationGame
            An independent copy of this game.
        """
        return copy.deepcopy(self)


# =============================================================================
# 2. AI AGENT CLASS
# =============================================================================
class AIAgent:
    """
    Computer opponent that picks its move using the Minimax algorithm
    with Alpha-Beta Pruning.
    """

    def __init__(self, search_depth=3):
        """
        Parameters
        ----------
        search_depth : int
            How many moves ahead the AI looks (default 3).
            Higher = smarter but slower.
        """
        # Store the maximum search depth
        self.search_depth = search_depth

    # -------------------------------------------------------------------------
    def evaluate(self, game):
        """
        Heuristic evaluation of the board from the AI's perspective.

        Formula:
            score = (number of AI's legal moves) − (number of human's legal moves)

        A positive score means the AI has more room to move (good for AI).
        A negative score means the human has more room (bad for AI).

        Parameters
        ----------
        game : IsolationGame
            The game state to evaluate.

        Returns
        -------
        int
            The heuristic score.
        """
        # Count how many moves the AI can make
        ai_moves = len(game.get_legal_moves(game.ai_pos))

        # Count how many moves the human can make
        player_moves = len(game.get_legal_moves(game.player_pos))

        # Return the difference (positive is good for AI)
        return ai_moves - player_moves

    # -------------------------------------------------------------------------
    def minimax(self, game, depth, alpha, beta, is_maximizing):
        """
        Minimax search with Alpha-Beta Pruning.

        The AI (maximizing player) tries to pick the move with the highest
        score, while the human (minimizing player) is assumed to pick the
        move with the lowest score.

        Alpha-Beta Pruning skips branches that cannot influence the final
        decision, making the search much faster.

        Parameters
        ----------
        game : IsolationGame
            Current game state (may be a simulated clone).
        depth : int
            Remaining search depth (stops when this reaches 0).
        alpha : float
            Best score the maximizer can guarantee so far (starts at -∞).
        beta : float
            Best score the minimizer can guarantee so far (starts at +∞).
        is_maximizing : bool
            True if it is the AI's turn (maximizer), False for human.

        Returns
        -------
        int
            The heuristic score of the best reachable position.
        """
        # --- BASE CASE 1: depth exhausted ---------------------------------
        if depth == 0:
            return self.evaluate(game)

        # --- BASE CASE 2: game over ----------------------------------------
        if game.is_game_over():
            if game.is_player_turn:
                # Human cannot move → AI wins → very high score
                return 1000
            else:
                # AI cannot move → human wins → very low score
                return -1000

        # --- RECURSIVE CASE ------------------------------------------------
        if is_maximizing:
            # AI's turn — try to MAXIMISE the score
            max_eval = float('-inf')  # Start with the worst possible score

            # Get all moves available to the AI
            moves = game.get_legal_moves(game.ai_pos)

            for move in moves:
                # Create a copy so the real game is untouched
                child = game.clone()

                # Apply the AI's move on the copy
                child.make_move(list(child.ai_pos), move)

                # Recurse — next level is the minimizer (human)
                eval_score = self.minimax(child, depth - 1, alpha, beta, False)

                # Keep the highest score found so far
                max_eval = max(max_eval, eval_score)

                # Update alpha (best guaranteed score for maximizer)
                alpha = max(alpha, eval_score)

                # Pruning: if alpha >= beta, the minimizer will never allow
                # this branch, so we can stop searching here
                if beta <= alpha:
                    break

            return max_eval

        else:
            # Human's turn — try to MINIMISE the score
            min_eval = float('inf')  # Start with the best possible score

            # Get all moves available to the human
            moves = game.get_legal_moves(game.player_pos)

            for move in moves:
                # Create a copy so the real game is untouched
                child = game.clone()

                # Apply the human's move on the copy
                child.make_move(list(child.player_pos), move)

                # Recurse — next level is the maximizer (AI)
                eval_score = self.minimax(child, depth - 1, alpha, beta, True)

                # Keep the lowest score found so far
                min_eval = min(min_eval, eval_score)

                # Update beta (best guaranteed score for minimizer)
                beta = min(beta, eval_score)

                # Pruning: if alpha >= beta, the maximizer already has a
                # better option, so we can stop here
                if beta <= alpha:
                    break

            return min_eval

    # -------------------------------------------------------------------------
    def best_move(self, game):
        """
        Determine the best move for the AI by running minimax on every
        possible move and choosing the one with the highest score.

        Parameters
        ----------
        game : IsolationGame
            The current (real) game state.

        Returns
        -------
        list[int, int] or None
            [row, col] of the best move, or None if no move exists.
        """
        # Get all legal moves for the AI
        moves = game.get_legal_moves(game.ai_pos)

        # If there are no moves the AI has lost
        if not moves:
            return None

        # Track the best score and corresponding move
        best_score = float('-inf')  # Start with worst possible
        best = None                  # No best move yet

        # Evaluate every possible move
        for move in moves:
            # Clone the game to simulate this move
            child = game.clone()

            # Apply the move on the clone
            child.make_move(list(child.ai_pos), move)

            # Run minimax from the resulting position
            # Next turn belongs to the human (minimizer), hence False
            score = self.minimax(child, self.search_depth - 1,
                                 float('-inf'), float('inf'), False)

            # If this move leads to a better score, remember it
            if score > best_score:
                best_score = score
                best = move

        # Return the move with the highest minimax score
        return best


# =============================================================================
# 3. GUI CLASS (Tkinter)
# =============================================================================
class IsolationGUI:
    """
    Graphical interface for the Isolation game.

    Each cell is drawn on a Tkinter Canvas.
    The human clicks a highlighted (green) cell to move.
    After the human moves, the AI responds automatically.
    """

    # Size in pixels of each cell on the grid
    CELL_SIZE = 70

    # Colour palette for the different cell states
    COLOR_EMPTY     = "#F0E6D3"   # Light beige — empty square
    COLOR_DESTROYED = "#3B3B3B"   # Dark grey  — destroyed square
    COLOR_PLAYER    = "#2196F3"   # Blue       — human player
    COLOR_AI        = "#F44336"   # Red        — AI player
    COLOR_LEGAL     = "#81C784"   # Green      — legal move highlight
    COLOR_GRID      = "#5D4037"   # Brown      — grid lines

    def __init__(self, root):
        """
        Build the GUI and start the game.

        Parameters
        ----------
        root : tk.Tk
            The top-level Tkinter window.
        """
        # Store a reference to the root window
        self.root = root

        # Set the window title
        self.root.title("Isolation (Isola) Game")

        # Create game logic and AI instances
        self.game = IsolationGame()           # 7x7 board by default
        self.ai = AIAgent(search_depth=3)     # Looks 3 moves ahead

        # Calculate canvas dimensions based on board size and cell size
        canvas_width = self.game.board_size * self.CELL_SIZE
        canvas_height = self.game.board_size * self.CELL_SIZE

        # --- INFO LABEL -------------------------------------------------------
        # Shows whose turn it is
        self.info_label = tk.Label(
            root,
            text="Your turn! Click a green square to move.",
            font=("Arial", 14, "bold"),
            bg="#4E342E",        # Dark brown background
            fg="white",         # White text
            pady=8              # Vertical padding
        )
        # Place the label at the top, stretching the full width
        self.info_label.pack(fill=tk.X)

        # --- CANVAS (the game board) ------------------------------------------
        self.canvas = tk.Canvas(
            root,
            width=canvas_width,
            height=canvas_height,
            bg=self.COLOR_GRID,     # Grid line colour shows through gaps
            highlightthickness=0    # No border highlight
        )
        self.canvas.pack(padx=10, pady=10)

        # Bind mouse clicks on the canvas to our handler
        self.canvas.bind("<Button-1>", self.on_click)

        # --- RESTART BUTTON ---------------------------------------------------
        self.restart_btn = tk.Button(
            root,
            text="Restart Game",
            font=("Arial", 12),
            command=self.restart_game,  # Calls restart_game() on click
            bg="#FF9800",               # Orange background
            fg="white",                 # White text
            relief=tk.FLAT,             # Flat button style
            padx=16, pady=6             # Inner padding
        )
        self.restart_btn.pack(pady=(0, 10))

        # Prevent resizing so the layout stays neat
        self.root.resizable(False, False)

        # Set window background colour
        self.root.configure(bg="#4E342E")

        # Draw the initial board
        self.draw_board()

    # -------------------------------------------------------------------------
    def draw_board(self):
        """
        Redraw every cell on the canvas to reflect the current game state.

        Also highlights legal moves for the human player in green.
        """
        # Wipe everything currently on the canvas
        self.canvas.delete("all")

        # Get the list of legal moves so we can highlight them
        if self.game.is_player_turn:
            legal = self.game.get_legal_moves(self.game.player_pos)
        else:
            legal = []  # Don't show highlights during AI's turn

        # Iterate through every cell
        for row in range(self.game.board_size):
            for col in range(self.game.board_size):
                # Calculate pixel coordinates for this cell
                x1 = col * self.CELL_SIZE      # Left edge
                y1 = row * self.CELL_SIZE      # Top edge
                x2 = x1 + self.CELL_SIZE       # Right edge
                y2 = y1 + self.CELL_SIZE       # Bottom edge

                # Determine the fill colour based on cell value
                cell = self.game.board[row][col]

                if cell == -1:
                    # Destroyed square
                    color = self.COLOR_DESTROYED
                elif cell == 1:
                    # Human player
                    color = self.COLOR_PLAYER
                elif cell == 2:
                    # AI player
                    color = self.COLOR_AI
                elif [row, col] in legal:
                    # Empty but reachable — highlight green
                    color = self.COLOR_LEGAL
                else:
                    # Normal empty square
                    color = self.COLOR_EMPTY

                # Draw the cell rectangle with a small gap for grid lines
                self.canvas.create_rectangle(
                    x1 + 2, y1 + 2, x2 - 2, y2 - 2,
                    fill=color,
                    outline=""      # No outline (grid colour shows through)
                )

                # Draw labels on the player cells
                if cell == 1:
                    # "P" for Player
                    self.canvas.create_text(
                        (x1 + x2) // 2, (y1 + y2) // 2,
                        text="P", font=("Arial", 22, "bold"), fill="white"
                    )
                elif cell == 2:
                    # "AI" for Artificial Intelligence
                    self.canvas.create_text(
                        (x1 + x2) // 2, (y1 + y2) // 2,
                        text="AI", font=("Arial", 18, "bold"), fill="white"
                    )
                elif cell == -1:
                    # "X" for destroyed
                    self.canvas.create_text(
                        (x1 + x2) // 2, (y1 + y2) // 2,
                        text="✕", font=("Arial", 20), fill="#666666"
                    )

    # -------------------------------------------------------------------------
    def on_click(self, event):
        """
        Handle a mouse click on the canvas.

        If it is the human's turn and the clicked square is a legal move,
        perform the move and then schedule the AI's turn.

        Parameters
        ----------
        event : tk.Event
            Contains the x and y pixel coordinates of the click.
        """
        # Ignore clicks when it is not the human's turn
        if not self.game.is_player_turn:
            return

        # Convert pixel coordinates to board row and column
        col = event.x // self.CELL_SIZE
        row = event.y // self.CELL_SIZE

        # Check that the click is within the board boundaries
        if row < 0 or row >= self.game.board_size or col < 0 or col >= self.game.board_size:
            return  # Click was outside the board — do nothing

        # Get the list of legal moves for the human
        legal = self.game.get_legal_moves(self.game.player_pos)

        # Only proceed if the clicked square is actually a legal move
        if [row, col] in legal:
            # Execute the human's move
            self.game.make_move(self.game.player_pos, [row, col])

            # Redraw the board to show the updated state
            self.draw_board()

            # Update the info label
            self.info_label.config(text="AI is thinking...")

            # Check if the game is over after the human's move
            if self.game.is_game_over():
                self.show_game_over("You win! The AI has no moves left.")
                return

            # Schedule the AI to make its move after 500 ms
            # This gives the user a moment to see the board update
            self.root.after(500, self.ai_turn)

    # -------------------------------------------------------------------------
    def ai_turn(self):
        """
        Let the AI pick and execute its best move.
        Called automatically after the human moves.
        """
        # Ask the AI agent for the best move
        move = self.ai.best_move(self.game)

        # If the AI has a valid move, execute it
        if move is not None:
            self.game.make_move(self.game.ai_pos, move)

        # Redraw the board to show the AI's move
        self.draw_board()

        # Check if the game is over after the AI's move
        if self.game.is_game_over():
            self.show_game_over("AI wins! You have no moves left.")
            return

        # It is now the human's turn again
        self.info_label.config(text="Your turn! Click a green square to move.")

    # -------------------------------------------------------------------------
    def show_game_over(self, message):
        """
        Display a game-over message box and update the info label.

        Parameters
        ----------
        message : str
            The text to display (e.g. "You win!" or "AI wins!").
        """
        # Update the label at the top of the window
        self.info_label.config(text="Game Over!")

        # Show a pop-up dialog with the result
        messagebox.showinfo("Game Over", message)

    # -------------------------------------------------------------------------
    def restart_game(self):
        """
        Reset the game to its initial state and redraw the board.
        """
        # Create a brand-new game (7x7, default positions)
        self.game = IsolationGame()

        # Reset the info label
        self.info_label.config(text="Your turn! Click a green square to move.")

        # Redraw the board from scratch
        self.draw_board()


# =============================================================================
# 4. MAIN ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    # Create the main Tkinter window
    root = tk.Tk()

    # Instantiate the GUI — this also creates the game and AI objects
    app = IsolationGUI(root)

    # Start the Tkinter event loop (keeps the window open and responsive)
    root.mainloop()
