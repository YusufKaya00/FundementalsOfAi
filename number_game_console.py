from game_logic import GameState, AI_Agent
import time

def print_game_state(game_state):
    print("\n" + "="*40)
    print(f"Board: {game_state.numbers}")
    print(f"Scores -> Human: {game_state.scores[1]} | AI: {game_state.scores[2]}")
    print("="*40)

def get_human_move(game_state):
    legal_moves = game_state.get_legal_moves()
    print("\nYour Turn!")
    print("Options:")
    for idx, move in enumerate(legal_moves):
        action, i, val = move
        desc = ""
        if action == 'take':
            desc = f"Take {val} at index {i}"
        elif action == 'split2':
            desc = f"Split 2 at index {i} -> (1, 1)"
        elif action == 'split4':
            desc = f"Split 4 at index {i} -> (2, 2) (+1 point)"
        print(f"{idx}: {desc}")

    while True:
        try:
            choice = int(input("Enter move number: "))
            if 0 <= choice < len(legal_moves):
                return legal_moves[choice]
            else:
                print("Invalid choice number.")
        except ValueError:
            print("Please enter a valid number.")

def play_console_game():
    print("Welcome to the Number String Game!")
    while True:
        try:
            length_str = input("Enter string length (15-20): ")
            length = int(length_str)
            if 15 <= length <= 20:
                break
            print("Please enter a number between 15 and 20.")
        except ValueError:
            print("Invalid input.")

    game = GameState(length=length)
    ai = AI_Agent(player_id=2, depth_limit=4) # Depth can be adjusted

    print(f"Game Started! Initial String Length: {length}")

    while not game.is_game_over():
        print_game_state(game)
        
        if game.current_player == 1:
            move = get_human_move(game)
            game.apply_move(move)
            print(f"\nHuman chose: {move}")
        else:
            print("\nAI is thinking...")
            start_time = time.time()
            move = ai.get_best_move(game)
            elapsed = time.time() - start_time
            game.apply_move(move)
            print(f"AI chose: {move} (took {elapsed:.2f}s)")

    print("\n" + "#"*40)
    print("GAME OVER!")
    print(f"Final Scores -> Human: {game.scores[1]} | AI: {game.scores[2]}")
    winner = game.get_winner()
    if winner == 1:
        print("YOU WON!")
    elif winner == 2:
        print("AI WON!")
    else:
        print("IT'S A DRAW!")
    print("#"*40)

if __name__ == "__main__":
    play_console_game()
