import time
from Game_State import GameState


# algo_type: 0 for minimax, 1 for alpha-beta pruning
# I'm passing 4 as the default value for depth limit but we could always change it later
class AI_Agent:
    def __init__(self, player_id, algo_type=0, depth_limit=4):
        self.player_id = player_id
        self.depth_limit = depth_limit
        self.algo_type = algo_type
        self.nodes_visited = 0
        self.move_times = []

    def get_best_move(self, game_state):

        moves = game_state.get_legal_moves()
        if not moves:
            return None

        start = time.time()

        if self.algo_type == 0:
            best_move = self.get_best_move_minimax_tree(game_state)
        elif self.algo_type == 1:
            best_move = self.get_best_move_alphabeta_tree(game_state)
        else:
            return None

        self.move_times.append(time.time() - start)
        return best_move

    def get_experiment_stats(self):
        avg_time = sum(self.move_times) / len(self.move_times) if self.move_times else 0
        return {
            "nodes_visited": self.nodes_visited,
            "total_moves": len(self.move_times),
            "avg_move_time": round(avg_time, 4),
        }

    def reset_stats(self):
        self.nodes_visited = 0
        self.move_times = []

    def get_best_move_minimax_tree(self, game_state):

        tree = game_state.get_game_tree(self.depth_limit)

        best_value = -float("inf")
        best_move = None

        for child in tree["children"]:
            value = self.minimax_tree(
                node=child["result"], depth=self.depth_limit - 1, is_maximizing=False
            )

            if value > best_value:
                best_value = value
                best_move = child["move"]

        return best_move

    def minimax_tree(self, node, depth, is_maximizing):

        self.nodes_visited += 1

        children = node["children"]

        if not children or depth == 0:
            return self.heuristic_evaluation(node["state"])

        if is_maximizing:
            best_val = -float("inf")
            for child in children:
                value = self.minimax_tree(child["result"], depth - 1, False)
                best_val = max(best_val, value)

            return best_val

        else:
            best_val = float("inf")
            for child in children:
                value = self.minimax_tree(child["result"], depth - 1, True)
                best_val = min(best_val, value)

            return best_val

    def get_best_move_alphabeta_tree(self, game_state):

        tree = game_state.get_game_tree(self.depth_limit)

        best_value = -float("inf")
        best_move = None

        alpha = -float("inf")
        beta = float("inf")

        for child in tree["children"]:
            value = self.alphabeta_tree(
                node=child["result"],
                depth=self.depth_limit - 1,
                alpha=alpha,
                beta=beta,
                is_maximizing=False,
            )

            if value > best_value:
                best_value = value
                best_move = child["move"]

            alpha = max(alpha, best_value)

        return best_move

    def alphabeta_tree(self, node, depth, alpha, beta, is_maximizing):

        self.nodes_visited += 1

        children = node["children"]

        if not children or depth == 0:
            return self.heuristic_evaluation(node["state"])

        if is_maximizing:
            value = -float("inf")
            for child in children:
                value = max(
                    value,
                    self.alphabeta_tree(child["result"], depth - 1, alpha, beta, False),
                )

                alpha = max(alpha, value)
                if beta <= alpha:
                    break  # beta cutoff

            return value

        else:
            value = float("inf")
            for child in children:
                value = min(
                    value,
                    self.alphabeta_tree(child["result"], depth - 1, alpha, beta, True),
                )

                beta = min(beta, value)
                if beta <= alpha:
                    break  # alpha cutoff

            return value

    def heuristic_evaluation(self, state):
        ai_score = state["scores"][self.player_id]
        human_score = state["scores"][3 - self.player_id]  # assuming IDs are 1 and 2

        score_diff = ai_score - human_score

        potential_value = 0
        for num in state["numbers"]:
            if num == 4:
                potential_value += 0.5
            elif num == 2:
                potential_value += 0.2

        final_score = (score_diff * 10.0) + potential_value

        return final_score


# Keeping the test block for debugging without GUI just in case to confirm logic works as expected.
# In the final version, we can comment it out
if __name__ == "__main__":
    game = GameState(length=5)
    print(f"Initial Board: {game.numbers}")
    ai = AI_Agent(player_id=2, depth_limit=3, algo_type=1)

    print("Testing Moves generation:")
    print(game.get_legal_moves())

    print("\nSimulating one AI move:")
    best_move = ai.get_best_move(game)
    print(f"Best Move: {best_move}")

    game.apply_move(best_move)
    print(f"Board after move: {game.numbers}")
    print(f"Scores: {game.scores}")

    print("\nExperiment Stats:")
    print(ai.get_experiment_stats())
