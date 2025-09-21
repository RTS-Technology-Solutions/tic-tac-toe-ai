"""
Tic-Tac-Toe Game Engine
Core game logic separated from UI and AI for clean automation integration
"""

from typing import List, Tuple, Optional, Dict, Any
from enum import Enum
import copy

class Player(Enum):
    X = "X"
    O = "O"
    EMPTY = " "

class GameState(Enum):
    ONGOING = "ongoing"
    X_WINS = "x_wins"
    O_WINS = "o_wins"
    DRAW = "draw"

class TicTacToeGame:
    """
    Core game engine for Tic-Tac-Toe with clean state management
    Provides clear feedback loop for AI decision making
    """
    
    def __init__(self):
        self.reset_game()
        
    def reset_game(self):
        """Reset the game to initial state"""
        self.board = [Player.EMPTY] * 9  # 0-8 positions
        self.current_player = Player.X
        self.game_state = GameState.ONGOING
        self.move_history = []
        self.winner = None
        self.winning_line = None
        
    def get_game_state(self) -> Dict[str, Any]:
        """
        Get comprehensive game state for AI decision making
        This is the core of the feedback loop
        """
        return {
            'board': [p.value for p in self.board],
            'current_player': self.current_player.value,
            'game_state': self.game_state.value,
            'available_moves': self.get_available_moves(),
            'move_count': len(self.move_history),
            'winner': self.winner.value if self.winner else None,
            'winning_line': self.winning_line,
            'board_evaluation': self._evaluate_board_state()
        }
    
    def get_available_moves(self) -> List[int]:
        """Get list of available positions (0-8)"""
        return [i for i, cell in enumerate(self.board) if cell == Player.EMPTY]
    
    def make_move(self, position: int) -> Dict[str, Any]:
        """
        Make a move and return the resulting game state
        This is where actions create feedback
        
        Args:
            position: Board position (0-8)
            
        Returns:
            Dictionary containing move result and new game state
        """
        if not self.is_valid_move(position):
            return {
                'success': False,
                'error': f"Invalid move: position {position}",
                'game_state': self.get_game_state()
            }
        
        # Make the move
        self.board[position] = self.current_player
        move_info = {
            'player': self.current_player.value,
            'position': position,
            'move_number': len(self.move_history) + 1
        }
        self.move_history.append(move_info)
        
        # Check for game end conditions
        self._check_game_end()
        
        # Switch players if game continues
        if self.game_state == GameState.ONGOING:
            self.current_player = Player.O if self.current_player == Player.X else Player.X
        
        return {
            'success': True,
            'move_info': move_info,
            'game_state': self.get_game_state()
        }
    
    def is_valid_move(self, position: int) -> bool:
        """Check if a move is valid"""
        return (0 <= position <= 8 and 
                self.board[position] == Player.EMPTY and 
                self.game_state == GameState.ONGOING)
    
    def _check_game_end(self):
        """Check if the game has ended and update state accordingly"""
        # Check for winner
        winner_info = self._check_winner()
        if winner_info:
            self.winner = winner_info['player']
            self.winning_line = winner_info['line']
            self.game_state = GameState.X_WINS if self.winner == Player.X else GameState.O_WINS
            return
        
        # Check for draw
        if len(self.get_available_moves()) == 0:
            self.game_state = GameState.DRAW
    
    def _check_winner(self) -> Optional[Dict]:
        """Check for a winning condition"""
        # All possible winning lines
        winning_lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
            [0, 4, 8], [2, 4, 6]              # diagonals
        ]
        
        for line in winning_lines:
            if (self.board[line[0]] == self.board[line[1]] == self.board[line[2]] != Player.EMPTY):
                return {
                    'player': self.board[line[0]],
                    'line': line
                }
        return None
    
    def _evaluate_board_state(self) -> Dict[str, Any]:
        """
        Evaluate current board state for AI decision making
        This provides rich feedback about the current position
        """
        evaluation = {
            'center_control': self.board[4] != Player.EMPTY,
            'corner_control': sum(1 for i in [0, 2, 6, 8] if self.board[i] != Player.EMPTY),
            'edge_control': sum(1 for i in [1, 3, 5, 7] if self.board[i] != Player.EMPTY),
            'x_threats': self._count_threats(Player.X),
            'o_threats': self._count_threats(Player.O),
            'x_positions': [i for i, p in enumerate(self.board) if p == Player.X],
            'o_positions': [i for i, p in enumerate(self.board) if p == Player.O]
        }
        return evaluation
    
    def _count_threats(self, player: Player) -> Dict[str, List[int]]:
        """Count immediate threats (2 in a row) for a player"""
        winning_lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
            [0, 4, 8], [2, 4, 6]              # diagonals
        ]
        
        threats = {'winning_moves': [], 'blocking_needed': []}
        
        for line in winning_lines:
            player_count = sum(1 for i in line if self.board[i] == player)
            empty_count = sum(1 for i in line if self.board[i] == Player.EMPTY)
            
            if player_count == 2 and empty_count == 1:
                empty_pos = [i for i in line if self.board[i] == Player.EMPTY][0]
                threats['winning_moves'].append(empty_pos)
        
        # Check opponent threats (for blocking)
        opponent = Player.O if player == Player.X else Player.X
        for line in winning_lines:
            opponent_count = sum(1 for i in line if self.board[i] == opponent)
            empty_count = sum(1 for i in line if self.board[i] == Player.EMPTY)
            
            if opponent_count == 2 and empty_count == 1:
                empty_pos = [i for i in line if self.board[i] == Player.EMPTY][0]
                threats['blocking_needed'].append(empty_pos)
        
        return threats
    
    def get_board_copy(self) -> List[Player]:
        """Get a copy of the current board state"""
        return copy.deepcopy(self.board)
    
    def simulate_move(self, position: int) -> 'TicTacToeGame':
        """
        Create a copy of the game with a simulated move
        Useful for AI lookahead without affecting the actual game
        """
        game_copy = TicTacToeGame()
        game_copy.board = copy.deepcopy(self.board)
        game_copy.current_player = self.current_player
        game_copy.game_state = self.game_state
        game_copy.move_history = copy.deepcopy(self.move_history)
        game_copy.winner = self.winner
        game_copy.winning_line = self.winning_line
        
        game_copy.make_move(position)
        return game_copy
    
    def print_board(self):
        """Print a visual representation of the board"""
        print("\n   |   |   ")
        print(f" {self.board[0].value} | {self.board[1].value} | {self.board[2].value} ")
        print("___|___|___")
        print("   |   |   ")
        print(f" {self.board[3].value} | {self.board[4].value} | {self.board[5].value} ")
        print("___|___|___")
        print("   |   |   ")
        print(f" {self.board[6].value} | {self.board[7].value} | {self.board[8].value} ")
        print("   |   |   ")
        print("\nPositions:")
        print(" 0 | 1 | 2 ")
        print(" 3 | 4 | 5 ")
        print(" 6 | 7 | 8 ")

if __name__ == "__main__":
    # Quick test of the game engine
    game = TicTacToeGame()
    print("Tic-Tac-Toe Game Engine Test")
    game.print_board()
    
    # Test some moves
    moves = [4, 0, 1, 3, 7]  # X should win
    for move in moves:
        result = game.make_move(move)
        print(f"\nMove {move} by {result['move_info']['player']}:")
        game.print_board()
        print(f"Game state: {result['game_state']['game_state']}")
        
        if result['game_state']['game_state'] != 'ongoing':
            print(f"Game over! Winner: {result['game_state']['winner']}")
            break
