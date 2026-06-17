"""
AI Decision Making Framework for Tic-Tac-Toe
Demonstrates different decision-making strategies and feedback loops
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, Optional
import random
import copy
from ttt_game import TicTacToeGame, Player, GameState

class AIPlayer(ABC):
    """
    Abstract base class for AI players
    Defines the interface for decision-making engines
    """
    
    def __init__(self, name: str, player: Player):
        self.name = name
        self.player = player
        self.move_history = []
        self.decision_log = []
    
    @abstractmethod
    def make_decision(self, game_state: Dict[str, Any]) -> int:
        """
        Make a move decision based on current game state
        This is the core decision-making method that each AI strategy implements
        
        Args:
            game_state: Complete game state from TicTacToeGame.get_game_state()
            
        Returns:
            Position (0-8) to place the mark
        """
        pass
    
    def log_decision(self, game_state: Dict[str, Any], chosen_move: int, reasoning: str):
        """Log the decision-making process for analysis"""
        decision_entry = {
            'move_number': len(self.move_history) + 1,
            'game_state': copy.deepcopy(game_state),
            'chosen_move': chosen_move,
            'reasoning': reasoning,
            'available_moves': game_state['available_moves']
        }
        self.decision_log.append(decision_entry)
        self.move_history.append(chosen_move)
    
    def get_decision_analysis(self) -> Dict[str, Any]:
        """Analyze the decision-making process"""
        return {
            'total_moves': len(self.move_history),
            'decision_log': self.decision_log,
            'move_pattern': self.move_history
        }

class RandomAI(AIPlayer):
    """Random move selection - baseline for comparison"""
    
    def make_decision(self, game_state: Dict[str, Any]) -> int:
        available_moves = game_state['available_moves']
        chosen_move = random.choice(available_moves)
        
        reasoning = f"Random selection from {len(available_moves)} available moves"
        self.log_decision(game_state, chosen_move, reasoning)
        
        return chosen_move

class StrategicAI(AIPlayer):
    """
    Strategic AI with prioritized decision making
    Demonstrates rule-based decision logic
    """
    
    def make_decision(self, game_state: Dict[str, Any]) -> int:
        board_eval = game_state['board_evaluation']
        available_moves = game_state['available_moves']
        
        # Decision priority system
        decision_chain = [
            self._check_winning_move,
            self._check_blocking_move,
            self._prefer_center,
            self._prefer_corners,
            self._prefer_edges
        ]
        
        for strategy in decision_chain:
            move = strategy(game_state, board_eval, available_moves)
            if move is not None:
                return move
        
        # Fallback to random
        return random.choice(available_moves)
    
    def _check_winning_move(self, game_state: Dict[str, Any], board_eval: Dict[str, Any], available_moves: List[int]) -> Optional[int]:
        """Check if we can win immediately"""
        threats = board_eval[f'{self.player.value.lower()}_threats']
        if threats['winning_moves']:
            move = threats['winning_moves'][0]
            reasoning = f"Winning move found at position {move}"
            self.log_decision(game_state, move, reasoning)
            return move
        return None
    
    def _check_blocking_move(self, game_state: Dict[str, Any], board_eval: Dict[str, Any], available_moves: List[int]) -> Optional[int]:
        """Check if we need to block opponent's winning move"""
        threats = board_eval[f'{self.player.value.lower()}_threats']
        if threats['blocking_needed']:
            move = threats['blocking_needed'][0]
            reasoning = f"Blocking opponent's winning move at position {move}"
            self.log_decision(game_state, move, reasoning)
            return move
        return None
    
    def _prefer_center(self, game_state: Dict[str, Any], board_eval: Dict[str, Any], available_moves: List[int]) -> Optional[int]:
        """Prefer center position if available"""
        if 4 in available_moves:
            reasoning = "Taking center position for strategic advantage"
            self.log_decision(game_state, 4, reasoning)
            return 4
        return None
    
    def _prefer_corners(self, game_state: Dict[str, Any], board_eval: Dict[str, Any], available_moves: List[int]) -> Optional[int]:
        """Prefer corner positions"""
        corners = [0, 2, 6, 8]
        available_corners = [pos for pos in corners if pos in available_moves]
        if available_corners:
            move = random.choice(available_corners)
            reasoning = f"Taking corner position {move} for strategic advantage"
            self.log_decision(game_state, move, reasoning)
            return move
        return None
    
    def _prefer_edges(self, game_state: Dict[str, Any], board_eval: Dict[str, Any], available_moves: List[int]) -> Optional[int]:
        """Take edge positions as last resort"""
        edges = [1, 3, 5, 7]
        available_edges = [pos for pos in edges if pos in available_moves]
        if available_edges:
            move = random.choice(available_edges)
            reasoning = f"Taking edge position {move}"
            self.log_decision(game_state, move, reasoning)
            return move
        return None

class MinimaxAI(AIPlayer):
    """
    Minimax algorithm implementation
    Demonstrates perfect play through game tree search
    """
    
    def __init__(self, name: str, player: Player, max_depth: int = 9):
        super().__init__(name, player)
        self.max_depth = max_depth
        self.positions_evaluated = 0
    
    def make_decision(self, game_state: Dict[str, Any]) -> int:
        self.positions_evaluated = 0
        
        # Create a game instance for simulation
        temp_game = TicTacToeGame()
        temp_game.board = [Player(cell) for cell in game_state['board']]
        temp_game.current_player = Player(game_state['current_player'])
        
        _, best_move = self.minimax(temp_game, self.max_depth, True, self.player)
        
        # Ensure we have a valid move
        if best_move is None:
            available_moves = game_state['available_moves']
            best_move = available_moves[0] if available_moves else 0
        
        reasoning = f"Minimax analysis (evaluated {self.positions_evaluated} positions) chose position {best_move}"
        self.log_decision(game_state, best_move, reasoning)
        
        return best_move
    
    def minimax(self, game: TicTacToeGame, depth: int, is_maximizing: bool, maximizing_player: Player) -> Tuple[float, Optional[int]]:
        """
        Minimax algorithm with game tree search
        Returns (score, best_move)
        """
        self.positions_evaluated += 1
        
        # Terminal conditions
        if game.game_state == GameState.X_WINS:
            return (10 if maximizing_player == Player.X else -10, None)
        elif game.game_state == GameState.O_WINS:
            return (10 if maximizing_player == Player.O else -10, None)
        elif game.game_state == GameState.DRAW or depth == 0:
            return (0, None)
        
        available_moves = game.get_available_moves()
        best_move = available_moves[0]
        
        if is_maximizing:
            max_score = float('-inf')
            for move in available_moves:
                game_copy = game.simulate_move(move)
                score, _ = self.minimax(game_copy, depth - 1, False, maximizing_player)
                if score > max_score:
                    max_score = score
                    best_move = move
            return (max_score, best_move)
        else:
            min_score = float('inf')
            for move in available_moves:
                game_copy = game.simulate_move(move)
                score, _ = self.minimax(game_copy, depth - 1, True, maximizing_player)
                if score < min_score:
                    min_score = score
                    best_move = move
            return (min_score, best_move)

class LearningAI(AIPlayer):
    """
    Simple learning AI that adapts based on game outcomes
    Demonstrates basic reinforcement learning concepts
    """
    
    def __init__(self, name: str, player: Player, learning_rate: float = 0.1):
        super().__init__(name, player)
        self.learning_rate = learning_rate
        self.position_values = [0.0] * 9  # Value for each position
        self.game_outcomes = []
    
    def make_decision(self, game_state: Dict[str, Any]) -> int:
        available_moves = game_state['available_moves']
        
        # Choose move based on learned position values
        if random.random() < 0.1:  # 10% exploration
            chosen_move = random.choice(available_moves)
            reasoning = "Exploration move (random)"
        else:
            # Exploitation: choose best known move
            move_values = [(move, self.position_values[move]) for move in available_moves]
            chosen_move = max(move_values, key=lambda x: x[1])[0]
            reasoning = f"Exploitation move (position value: {self.position_values[chosen_move]:.3f})"
        
        self.log_decision(game_state, chosen_move, reasoning)
        return chosen_move
    
    def learn_from_game(self, final_game_state: Dict[str, Any]):
        """Update position values based on game outcome"""
        if final_game_state['winner'] == self.player.value:
            reward = 1.0
        elif final_game_state['winner'] is None:  # Draw
            reward = 0.5
        else:
            reward = 0.0
        
        # Update values for positions we played
        for move in self.move_history:
            self.position_values[move] += self.learning_rate * (reward - self.position_values[move])
        
        self.game_outcomes.append({
            'reward': reward,
            'moves_played': len(self.move_history),
            'final_state': final_game_state['game_state']
        })

# Game Engine with AI Integration
class AIGameManager:
    """
    Manages games between AI players and provides detailed analytics
    This is where the complete feedback loop is demonstrated
    """
    
    def __init__(self):
        self.game_history = []
        self.current_game = None
    
    def play_game(self, player_x: AIPlayer, player_o: AIPlayer, verbose: bool = False) -> Dict[str, Any]:
        """Play a complete game between two AI players"""
        game = TicTacToeGame()
        self.current_game = game
        
        players = {Player.X: player_x, Player.O: player_o}
        move_log = []
        
        if verbose:
            print(f"\nGame: {player_x.name} (X) vs {player_o.name} (O)")
            game.print_board()
        
        while game.game_state == GameState.ONGOING:
            current_ai = players[game.current_player]
            game_state = game.get_game_state()
            
            # AI makes decision
            chosen_move = current_ai.make_decision(game_state)
            
            # Execute move
            move_result = game.make_move(chosen_move)
            move_log.append({
                'player': current_ai.name,
                'move': chosen_move,
                'reasoning': current_ai.decision_log[-1]['reasoning'] if current_ai.decision_log else "No reasoning logged"
            })
            
            if verbose:
                print(f"\n{current_ai.name} plays position {chosen_move}")
                game.print_board()
        
        # Game completed - gather results
        final_state = game.get_game_state()
        game_result = {
            'game_id': len(self.game_history) + 1,
            'player_x': player_x.name,
            'player_o': player_o.name,
            'winner': final_state['winner'],
            'game_state': final_state['game_state'],
            'total_moves': final_state['move_count'],
            'move_log': move_log,
            'final_board': final_state['board']
        }
        
        self.game_history.append(game_result)
        
        # Update learning AIs
        if isinstance(player_x, LearningAI):
            player_x.learn_from_game(final_state)
        if isinstance(player_o, LearningAI):
            player_o.learn_from_game(final_state)
        
        if verbose:
            print(f"\nGame Over! Result: {final_state['game_state']}")
            if final_state['winner']:
                print(f"Winner: {final_state['winner']}")
        
        return game_result
    
    def analyze_performance(self, ai_player: AIPlayer, games_played: int) -> Dict[str, Any]:
        """Analyze an AI player's performance across multiple games"""
        player_games = [game for game in self.game_history[-games_played:] 
                       if game['player_x'] == ai_player.name or game['player_o'] == ai_player.name]
        
        wins = sum(1 for game in player_games if game['winner'] == ai_player.player.value)
        draws = sum(1 for game in player_games if game['winner'] is None)
        losses = len(player_games) - wins - draws
        
        return {
            'player_name': ai_player.name,
            'games_played': len(player_games),
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'win_rate': wins / len(player_games) if player_games else 0,
            'decision_analysis': ai_player.get_decision_analysis()
        }

if __name__ == "__main__":
    # Demonstration of different AI strategies
    print("AI Decision-Making Framework Demonstration")
    print("=" * 50)
    
    # Create different AI players
    random_ai = RandomAI("Random AI", Player.X)
    strategic_ai = StrategicAI("Strategic AI", Player.O)
    minimax_ai = MinimaxAI("Minimax AI", Player.X)
    learning_ai = LearningAI("Learning AI", Player.O)
    
    # Game manager
    manager = AIGameManager()
    
    # Play a few demonstration games
    print("\n1. Random AI vs Strategic AI")
    result = manager.play_game(random_ai, strategic_ai, verbose=True)
    
    print("\n2. Strategic AI vs Minimax AI")
    strategic_ai2 = StrategicAI("Strategic AI 2", Player.X)
    result = manager.play_game(strategic_ai2, minimax_ai, verbose=True)
    
    print(f"\nGames played: {len(manager.game_history)}")
    print("Decision-making framework is ready for experimentation!")
