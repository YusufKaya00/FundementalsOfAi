import Game_State as gs
import AI_Agent as AI
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
    length = 0
    algo_type = 0
    player_id = 0
    print("Welcome to the Number String Game!")
    while True:
        try:
            length_str = input("Enter string length (15-20): ")
            length = int(length_str)
            algo_type_inp = input(
                "Enter what kind of algorithm you want your AI opponent to use (Minimax[0] or AlphaBeta[1]): ")
            algo_type = int(algo_type_inp)
            player_id_inp = input("Enter who starts the game: 2 - You, 1 - AI: ")
            player_id = int(player_id_inp)
            if algo_type in [0, 1] and 1 <= length <= 20 and player_id in [1, 2]:
                break
            print("Please enter valid inputs.")
        except ValueError:
            print("Invalid input.")

    game = gs.GameState(length=length)
    ai = AI.AI_Agent(player_id=player_id, algo_type=algo_type, depth_limit=4) # Depth can be adjusted

    print("Game started!")
    print("Initial string length:", length)

    while not game.is_game_over():
        print_game_state(game)
        
        if game.current_player == 1:
            move = get_human_move(game)
            game.apply_move(move)
            print(f"\nYou chose: {move}")
        else:
            print("\nAI is thinking...")
            start_time = time.time()
            move = ai.get_best_move(game)
            game.apply_move(move)
            ai_time = time.time() - start_time

            print("AI move:", move)
            print("Time:", round(ai_time, 2), "seconds")

    print("\n" + "#"*40)
    print("GAME OVER!")
    print(f"Final Scores -> You: {game.scores[1]} | AI: {game.scores[2]}")
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
