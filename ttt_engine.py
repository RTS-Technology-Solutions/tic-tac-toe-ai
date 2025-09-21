"""
Custom Tic-Tac-Toe Static Evaluation Engine
A minimal, extensible framework for building custom heuristics
"""

from typing import Dict, Any, List, Optional
import random
from ttt_game import TicTacToeGame, Player, GameState
from ttt_ai import AIPlayer

class TTTEngine(AIPlayer):
    """
    Custom static evaluation engine with extensible heuristic system.
    Designed for easy modification and heuristic experimentation.
    """
    
    def __init__(self, name: str, player: Player):
        super().__init__(name, player)
        self.opponent = Player.O if player == Player.X else Player.X
    
    def make_decision(self, game_state: Dict[str, Any]) -> int:
        """
        Main decision-making method.
        Evaluates all available moves and selects the best one.
        """
        available_moves = game_state['available_moves']
        
        if not available_moves:
            return 0  # Should never happen in valid game state
        
        # Evaluate each possible move
        move_evaluations = []
        for move in available_moves:
            score = self.evaluate_move(move, game_state)
            move_evaluations.append((move, score))
            
        # Select the move with the highest score
        best_moves = [move for move, score in move_evaluations if score == max(move_evaluations, key=lambda x: x[1])[1]]
        chosen_move = random.choice(best_moves)  # Random tie-breaking
        
        # Log the decision with evaluation details
        evaluation_details = {move: score for move, score in move_evaluations}
        reasoning = f"Move evaluations: {evaluation_details}. Chose: {chosen_move}"
        self.log_decision(game_state, chosen_move, reasoning)
        
        return chosen_move
    
    def evaluate_move(self, move: int, game_state: Dict[str, Any]) -> float:
        """
        Evaluate a single move and return a score.
        Higher scores indicate better moves.
        
        This is where heuristics are applied.
        """
        # Create a temporary game to simulate the move
        temp_game = self._create_temp_game(game_state)
        
        # Simulate our move
        temp_game.make_move(move)
        simulated_state = temp_game.get_game_state()
        
        # Apply all heuristics and sum the scores
        total_score = 0.0
        
        # HEURISTIC 1: Block opponent wins
        total_score += self.heuristic_block_opponent_win(move, game_state)
        
        return total_score
    
    # ========================================================================
    # HEURISTIC METHODS - Add new heuristics here
    # ========================================================================
    
    def heuristic_block_opponent_win(self, move: int, game_state: Dict[str, Any]) -> float:
        """
        HEURISTIC: Block opponent's winning moves
        Returns high score if this move blocks the opponent from winning
        """
        # Get opponent's threats from the board evaluation
        board_eval = game_state['board_evaluation']
        opponent_key = f'{self.opponent.value.lower()}_threats'
        opponent_threats = board_eval[opponent_key]
        
        # If this move blocks an opponent's winning move, give it high priority
        if move in opponent_threats['winning_moves']:
            return 100.0  # High priority for blocking wins
        
        return 0.0  # No blocking value
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def _create_temp_game(self, game_state: Dict[str, Any]) -> TicTacToeGame:
        """Create a temporary game instance from current game state"""
        temp_game = TicTacToeGame()
        temp_game.board = [Player(cell) for cell in game_state['board']]
        temp_game.current_player = Player(game_state['current_player'])
        temp_game.game_state = GameState(game_state['game_state']) if game_state['game_state'] != 'ongoing' else GameState.ONGOING
        return temp_game

if __name__ == "__main__":
    # Quick test of the engine
    from ttt_ai import AIGameManager, RandomAI
    
    print("Testing Custom TTT Engine")
    print("=" * 40)
    
    # Create engine and opponent
    custom_engine = TTTEngine("Custom Engine", Player.X)
    random_opponent = RandomAI("Random AI", Player.O)
    
    # Test against random AI
    manager = AIGameManager()
    
    print("Playing 5 games against Random AI...")
    wins = 0
    for i in range(5):
        result = manager.play_game(custom_engine, random_opponent, verbose=False)
        if result['winner'] == custom_engine.player.value:
            wins += 1
        print(f"Game {i+1}: {result['game_state']} (Winner: {result['winner'] or 'Draw'})")
    
    print(f"\nCustom Engine won {wins}/5 games against Random AI")
    
    # Show decision analysis for last game
    if custom_engine.decision_log:
        print(f"\nLast game decision analysis:")
        for i, decision in enumerate(custom_engine.decision_log[-4:], 1):  # Show last 4 decisions
            print(f"  Decision {i}: {decision['reasoning']}")
