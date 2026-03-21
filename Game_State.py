import random
import copy

class GameState:
    def __init__(self, current_player, length=None, numbers=None):
        if numbers is not None:
            self.numbers = numbers
        else:
            if length is None:
                length = random.randint(15, 20)
            self.numbers = [random.randint(1, 4) for i in range(length)]

        self.scores = {1: 0, 2: 0}
        self.current_player = current_player
        self.history = []

    def clone(self):
        new_state = GameState(numbers=copy.deepcopy(self.numbers), current_player=copy.deepcopy(self.current_player))
        new_state.scores = copy.deepcopy(self.scores)
        new_state.current_player = self.current_player
        new_state.history = copy.deepcopy(self.history)
        return new_state

    def get_legal_moves(self):
        moves = []
        for i, num in enumerate(self.numbers):
            moves.append(('take', i, num))
            if num == 2:
                moves.append(('split2', i, 2))
            if num == 4:
                moves.append(('split4', i, 4))
        return moves

    def apply_move(self, move):
        action, index, value = move

        if action == 'take':
            removed = self.numbers.pop(index)
            self.scores[self.current_player] += removed
        elif action == 'split2':
            self.numbers.pop(index)
            self.numbers.insert(index, 1)
            self.numbers.insert(index, 1)
        elif action == 'split4':
            self.numbers.pop(index)
            self.numbers.insert(index, 2)
            self.numbers.insert(index, 2)
            self.scores[self.current_player] += 1
        self.current_player = 2 if self.current_player == 1 else 1

    def is_game_over(self):
        return len(self.numbers) == 0

    def get_winner(self):
        if not self.is_game_over():
            return None
        if self.scores[1] > self.scores[2]:
            return 1
        elif self.scores[2] > self.scores[1]:
            return 2
        else:
            return 0

    def get_game_tree(self, depth_limit):
        def build_tree(state, depth_limit):
            node = {
                'state': {
                    'numbers': state.numbers.copy(),
                    'scores': state.scores.copy(),
                    'current_player': state.current_player,
                    'depth': depth_limit
                },
                'children': []
            }

            if state.is_game_over():
                node['winner'] = state.get_winner()
                return node

            for move in state.get_legal_moves():
                next_state = state.clone()
                next_state.apply_move(move)

                if depth_limit > 0:
                    child_node = {
                        'move': move,
                        'result': build_tree(next_state, (depth_limit - 1))
                    }
                    node['children'].append(child_node)

            return node

        return build_tree(self, depth_limit)


if __name__ == "__main__":
    game = GameState(length=5, current_player=1)
    print(f"Initial Board: {game.numbers}")

    print("Testing moves generation:")
    print(game.get_legal_moves())

    print("Testing tree generation:")
    print(game.get_game_tree(depth_limit=4))
