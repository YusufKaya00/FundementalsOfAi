"""
Isolation (Isola) Board Game — Console Version
================================================
A two-player strategy game played on a 7x7 grid.
Players move like a chess Queen (horizontal, vertical, diagonal).
After each move the square you left is destroyed — no one can step on it again.
The player who cannot move loses.

This file runs entirely in the terminal (no GUI required).
It contains:
    1. IsolationGame  — game state and rules
    2. AIAgent        — Minimax with Alpha-Beta Pruning
    3. Console game loop (text-based input/output)
"""

import copy  # For deep-copying the game state inside AI search


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

        # Place Player 1 (human) at the top-left corner
        self.player_pos = [0, 0]

        # Place Player 2 (AI) at the bottom-right corner
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

        The Queen can slide any number of squares in 8 directions but must stop
        before hitting a wall, a destroyed square, or the other player.

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

            # Keep sliding as long as we stay on the board and the square is empty
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
            return len(self.get_legal_moves(self.player_pos)) == 0
        else:
            return len(self.get_legal_moves(self.ai_pos)) == 0

    # -------------------------------------------------------------------------
    def clone(self):
        """
        Create a deep copy of the current game state.

        Used by the AI so it can simulate future moves without modifying
        the real game.

        Returns
        -------
        IsolationGame
            An independent copy of this game.
        """
        return copy.deepcopy(self)

    # -------------------------------------------------------------------------
    def print_board(self):
        """
        Print the board to the console in a human-readable format.

        Legend:
            .  = empty square
            X  = destroyed square
            P  = human player
            AI = AI player
        """
        # Print column numbers as header
        print("    ", end="")
        for c in range(self.board_size):
            print(f" {c}  ", end="")
        print()

        # Print a horizontal separator line
        print("   +" + "---+" * self.board_size)

        # Print each row
        for r in range(self.board_size):
            # Print the row number
            print(f" {r} |", end="")

            for c in range(self.board_size):
                cell = self.board[r][c]

                if cell == 1:
                    # Human player
                    print(" P |", end="")
                elif cell == 2:
                    # AI player
                    print("AI |", end="")
                elif cell == -1:
                    # Destroyed square
                    print(" X |", end="")
                else:
                    # Empty square
                    print(" . |", end="")

            print()
            # Print a horizontal separator line after each row
            print("   +" + "---+" * self.board_size)


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
        """
        # Store the maximum search depth
        self.search_depth = search_depth

    # -------------------------------------------------------------------------
    def evaluate(self, game):
        """
        Heuristic evaluation of the board from the AI's perspective.

        Formula: score = (AI's legal moves) - (human's legal moves)

        Parameters
        ----------
        game : IsolationGame
            The game state to evaluate.

        Returns
        -------
        int
            The heuristic score.
        """
        # Count moves for each player
        ai_moves = len(game.get_legal_moves(game.ai_pos))
        player_moves = len(game.get_legal_moves(game.player_pos))

        # Positive = good for AI, negative = good for human
        return ai_moves - player_moves

    # -------------------------------------------------------------------------
    def minimax(self, game, depth, alpha, beta, is_maximizing):
        """
        Minimax search with Alpha-Beta Pruning.

        Parameters
        ----------
        game : IsolationGame
            Current game state (may be a simulated clone).
        depth : int
            Remaining search depth.
        alpha : float
            Best score the maximizer can guarantee so far.
        beta : float
            Best score the minimizer can guarantee so far.
        is_maximizing : bool
            True if it is the AI's turn (maximizer).

        Returns
        -------
        int
            The heuristic score of the best reachable position.
        """
        # BASE CASE 1: depth exhausted
        if depth == 0:
            return self.evaluate(game)

        # BASE CASE 2: game over
        if game.is_game_over():
            if game.is_player_turn:
                # Human cannot move → AI wins
                return 1000
            else:
                # AI cannot move → human wins
                return -1000

        # RECURSIVE CASE
        if is_maximizing:
            # AI's turn — maximise the score
            max_eval = float('-inf')
            moves = game.get_legal_moves(game.ai_pos)

            for move in moves:
                # Clone and simulate the move
                child = game.clone()
                child.make_move(list(child.ai_pos), move)

                # Recurse (next level is minimizer)
                eval_score = self.minimax(child, depth - 1, alpha, beta, False)

                # Keep the best score
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)

                # Prune if possible
                if beta <= alpha:
                    break

            return max_eval

        else:
            # Human's turn — minimise the score
            min_eval = float('inf')
            moves = game.get_legal_moves(game.player_pos)

            for move in moves:
                # Clone and simulate the move
                child = game.clone()
                child.make_move(list(child.player_pos), move)

                # Recurse (next level is maximizer)
                eval_score = self.minimax(child, depth - 1, alpha, beta, True)

                # Keep the lowest score
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)

                # Prune if possible
                if beta <= alpha:
                    break

            return min_eval

    # -------------------------------------------------------------------------
    def best_move(self, game):
        """
        Determine the best move for the AI.

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

        # No moves means AI lost
        if not moves:
            return None

        # Evaluate every possible move
        best_score = float('-inf')
        best = None

        for move in moves:
            child = game.clone()
            child.make_move(list(child.ai_pos), move)

            score = self.minimax(child, self.search_depth - 1,
                                 float('-inf'), float('inf'), False)

            if score > best_score:
                best_score = score
                best = move

        return best


# =============================================================================
# 3. CONSOLE GAME LOOP
# =============================================================================
def play_console():
    """
    Run the Isolation game in the terminal.

    The human enters moves as "row col" (e.g. "2 3").
    The AI responds automatically after each human move.
    """
    # Create game and AI instances
    game = IsolationGame()
    ai = AIAgent(search_depth=3)

    # Print welcome message
    print("=" * 40)
    print("  ISOLATION (ISOLA) — Console Version")
    print("=" * 40)
    print("You are P (Player). The computer is AI.")
    print("Enter your move as: row col  (e.g. 2 3)")
    print("Type 'quit' to exit.\n")

    # Main game loop — runs until someone cannot move
    while True:
        # Display the current board
        game.print_board()

        # Check if the game is over
        if game.is_game_over():
            if game.is_player_turn:
                print("\n>>> AI WINS! You have no moves left. <<<")
            else:
                print("\n>>> YOU WIN! The AI has no moves left. <<<")
            break

        if game.is_player_turn:
            # --- HUMAN'S TURN -------------------------------------------------
            # Show available moves
            legal = game.get_legal_moves(game.player_pos)
            print(f"\nYour position: {game.player_pos}")
            print(f"Legal moves: {legal}")

            # Read input from the user
            while True:
                user_input = input("Your move (row col): ").strip()

                # Allow the player to quit
                if user_input.lower() == "quit":
                    print("Thanks for playing!")
                    return

                # Parse the input
                try:
                    parts = user_input.split()
                    row, col = int(parts[0]), int(parts[1])
                except (ValueError, IndexError):
                    print("Invalid format. Please enter: row col (e.g. 2 3)")
                    continue

                # Validate the move
                if [row, col] in legal:
                    # Execute the move
                    game.make_move(game.player_pos, [row, col])
                    break
                else:
                    print(f"[{row}, {col}] is not a legal move. Try again.")

        else:
            # --- AI'S TURN ----------------------------------------------------
            print("\nAI is thinking...")

            # Get the best move from the AI agent
            move = ai.best_move(game)

            if move is not None:
                print(f"AI moves to: {move}")
                game.make_move(game.ai_pos, move)
            else:
                print("AI has no moves!")

    # Ask if the player wants to play again
    print()
    again = input("Play again? (y/n): ").strip().lower()
    if again == "y":
        play_console()


# =============================================================================
# 4. MAIN ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    # Start the console game loop
    play_console()
