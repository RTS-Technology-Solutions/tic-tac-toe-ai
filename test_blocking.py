"""
Demonstrate the blocking heuristic in action
"""

from ttt_game import TicTacToeGame, Player
from ttt_engine import TTTEngine

def demonstrate_blocking():
    """Show the blocking heuristic working"""
    print("DEMONSTRATING BLOCKING HEURISTIC")
    print("=" * 40)
    
    # Create a game where opponent is about to win
    game = TicTacToeGame()
    
    # Set up a position where O is about to win
    # O has positions 0 and 1, needs position 2 to win
    game.board[0] = Player.O  # O in position 0
    game.board[1] = Player.O  # O in position 1
    game.current_player = Player.X  # X's turn
    game.move_history = [
        {'player': 'O', 'position': 0, 'move_number': 1},
        {'player': 'X', 'position': 4, 'move_number': 2},  # X took center
        {'player': 'O', 'position': 1, 'move_number': 3}
    ]
    game.board[4] = Player.X  # X has center
    
    print("Current board - O is about to win on top row:")
    game.print_board()
    
    # Create custom engine as X
    engine = TTTEngine("Custom Engine", Player.X)
    
    # Get game state and see what engine decides
    game_state = game.get_game_state()
    print(f"Available moves: {game_state['available_moves']}")
    print(f"Board evaluation: {game_state['board_evaluation']}")
    
    # Show what the engine evaluates
    chosen_move = engine.make_decision(game_state)
    
    print(f"\nEngine decision: Position {chosen_move}")
    if engine.decision_log:
        print(f"Reasoning: {engine.decision_log[-1]['reasoning']}")
    
    # Show the result
    game.make_move(chosen_move)
    print("\nAfter engine's move:")
    game.print_board()
    
    if chosen_move == 2:
        print("✓ SUCCESS: Engine correctly blocked the winning move!")
    else:
        print("✗ MISSED: Engine did not block the winning move.")

if __name__ == "__main__":
    demonstrate_blocking()