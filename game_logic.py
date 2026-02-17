import random
import copy

class GameState:
    """
    Represents the state of the Number String Game.
    Manages the board (list of numbers), scores, and turn management.
    """

    def __init__(self, length=None, numbers=None):
        """
        Initialize the game state.
        :param length: Length of the number string (15-20). If None, chosen randomly.
        :param numbers: Optional list of numbers to force a specific state (useful for testing/cloning).
        """
        if numbers is not None:
            self.numbers = numbers
        else:
            if length is None:
                length = random.randint(15, 20)
            # Generate random string with numbers 1, 2, 3, 4
            self.numbers = [random.randint(1, 4) for _ in range(length)]
        
        # Scores for Player 1 (Human) and Player 2 (AI)
        self.scores = {1: 0, 2: 0}
        self.current_player = 1 # Player 1 starts
        self.history = [] # To track moves

    def clone(self):
        """
        Creates a deep copy of the current game state.
        Crucial for Minimax simulation so we don't mess up the actual game board.
        """
        new_state = GameState(numbers=copy.deepcopy(self.numbers))
        new_state.scores = copy.deepcopy(self.scores)
        new_state.current_player = self.current_player
        new_state.history = copy.deepcopy(self.history)
        return new_state

    def get_legal_moves(self):
        """
        Generates all possible legal moves for the current state.
        A move is represented as a tuple: (action_type, index, value)
        """
        moves = []
        for i, num in enumerate(self.numbers):
            # 1. Take any number
            moves.append(('take', i, num))
            
            # 2. Split '2' into '1', '1' (No points gained immediately)
            if num == 2:
                moves.append(('split2', i, 2))
            
            # 3. Split '4' into '2', '2' (+1 point immediately)
            if num == 4:
                moves.append(('split4', i, 4))
        return moves

    def apply_move(self, move):
        """
        Applies a chosen move to the game state.
        :param move: A tuple (action_type, index, value)
        """
        action, index, value = move
        
        if action == 'take':
            # Remove the number and add it to current player's score
            removed = self.numbers.pop(index)
            self.scores[self.current_player] += removed
            
        elif action == 'split2':
            # Remove '2', insert '1', '1' at the same position
            # No points added, but it changes the turn parity
            self.numbers.pop(index)
            self.numbers.insert(index, 1)
            self.numbers.insert(index, 1)
            
        elif action == 'split4':
            # Remove '4', insert '2', '2' at the same position
            # Add 1 point to current player's score
            self.numbers.pop(index)
            self.numbers.insert(index, 2)
            self.numbers.insert(index, 2)
            self.scores[self.current_player] += 1
            
        # Switch turn
        self.current_player = 2 if self.current_player == 1 else 1

    def is_game_over(self):
        """Returns True if the list of numbers is empty."""
        return len(self.numbers) == 0

    def get_winner(self):
        """
        Returns the winner ID (1 or 2) or 0 for Draw.
        Returns None if game is not over.
        """
        if not self.is_game_over():
            return None
        
        if self.scores[1] > self.scores[2]:
            return 1
        elif self.scores[2] > self.scores[1]:
            return 2
        else:
            return 0


class AI_Agent:
    """
    AI Agent that uses Minimax with Alpha-Beta Pruning.
    """
    def __init__(self, player_id, depth_limit=4):
        self.player_id = player_id
        self.depth_limit = depth_limit

    def get_best_move(self, game_state):
        """
        Determines the best move for the AI using Minimax.
        This is the entry point called by the GUI.
        """
        # Collect legal moves
        moves = game_state.get_legal_moves()
        if not moves:
            return None
        
        best_val = -float('inf')
        best_move = None
        
        # Iterate through all moves to find the best one (Root Level)
        for move in moves:
            # Simulate the move
            next_state = game_state.clone()
            next_state.apply_move(move)
            
            # Call Minimax for the next level (minimizing step)
            # We pass False because after AI moves, it's Human's turn (Minimizer)
            val = self.minimax(next_state, self.depth_limit - 1, -float('inf'), float('inf'), False)
            
            if val > best_val:
                best_val = val
                best_move = move
                
        return best_move

    def minimax(self, state, depth, alpha, beta, is_maximizing):
        """
        Recursive Minimax function with Alpha-Beta Pruning.
        """
        
        # Base case: Game over or depth limit reached
        if state.is_game_over() or depth == 0:
            return self.heuristic_evaluation(state)
        
        if is_maximizing:
            max_eval = -float('inf')
            for move in state.get_legal_moves():
                next_state = state.clone()
                next_state.apply_move(move)
                score = self.minimax(next_state, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, score)
                alpha = max(alpha, score)
                if beta <= alpha:
                    break # Beta cutoff
            return max_eval
        else:
            min_eval = float('inf')
            for move in state.get_legal_moves():
                next_state = state.clone()
                next_state.apply_move(move)
                score = self.minimax(next_state, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, score)
                beta = min(beta, score)
                if beta <= alpha:
                    break # Alpha cutoff
            return min_eval

    def heuristic_evaluation(self, state):
        """
        HEURISTIC FUNCTION (CRITICAL FOR ASSIGNMENT)
        
        Logic for Defense:
        1. Score Difference: Primary metric. AI wants to have more points than Human.
        2. Potential Value: 
           - '4' on board is valuable (0.5 bonus) because it can be split for points.
           - '2' on board is slightly valuable (0.2 bonus) for defensive splitting.
        """
        
        ai_score = state.scores[self.player_id]
        human_score = state.scores[3 - self.player_id] # Assuming IDs are 1 and 2
        
        # 1. Base Score Difference
        score_diff = ai_score - human_score
        
        # 2. Evaluate remaining board potential
        potential_value = 0
        for num in state.numbers:
            if num == 4:
                potential_value += 0.5 
            elif num == 2:
                potential_value += 0.2
        
        # Final Score Formula
        # We multiply score_diff by 10 to prioritize "Real Points" over "Potential Points"
        final_score = (score_diff * 10.0) + potential_value
        
        return final_score

# Simple test block for debugging without GUI
if __name__ == "__main__":
    game = GameState(length=5)
    print(f"Initial Board: {game.numbers}")
    ai = AI_Agent(player_id=2, depth_limit=3)
    
    print("Testing Moves generation:")
    print(game.get_legal_moves())
    
    print("\nSimulating one AI move:")
    best_move = ai.get_best_move(game)
    print(f"Best Move: {best_move}")
    
    game.apply_move(best_move)
    print(f"Board after move: {game.numbers}")
    print(f"Scores: {game.scores}")