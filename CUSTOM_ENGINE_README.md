# Custom TTT Engine - Extensible Heuristic Framework

## Overview

The `ttt_engine.py` file provides a minimal, extensible framework for building your own tic-tac-toe AI using static evaluation heuristics. It's designed to be easily modifiable so you can experiment with different strategies and see how they perform.

## Architecture

### Core Components

```
TTTEngine (extends AIPlayer)
├── make_decision() - Main decision logic
├── evaluate_move() - Applies heuristics to score moves  
└── heuristic_*() - Individual heuristic methods
```

### How It Works

1. **Move Generation**: Gets all available moves from game state
2. **Move Evaluation**: Scores each move using heuristics
3. **Move Selection**: Chooses the highest-scoring move
4. **Decision Logging**: Records reasoning for analysis

## Current Implementation

### Starting Heuristic

The engine currently implements **one heuristic** as requested:

#### `heuristic_block_opponent_win()`
- **Purpose**: Block opponent's winning moves
- **Score**: 100.0 if the move blocks a win, 0.0 otherwise
- **Logic**: Checks if the move position is in opponent's `blocking_needed` list

### Code Structure

```python
def evaluate_move(self, move: int, game_state: Dict[str, Any]) -> float:
    """Evaluate a move by applying all heuristics"""
    total_score = 0.0
    
    # Apply each heuristic
    total_score += self.heuristic_block_opponent_win(move, game_state)
    # Add more heuristics here...
    
    return total_score
```

## Adding New Heuristics

To add your own heuristics, follow this pattern:

### 1. Create a new heuristic method:

```python
def heuristic_your_strategy(self, move: int, game_state: Dict[str, Any]) -> float:
    """
    HEURISTIC: Your strategy description
    Returns a score for how good this move is according to your strategy
    """
    # Your logic here
    if some_condition:
        return 50.0  # Good move
    elif other_condition:
        return -10.0  # Bad move
    return 0.0  # Neutral
```

### 2. Add it to the evaluation:

```python
def evaluate_move(self, move: int, game_state: Dict[str, Any]) -> float:
    total_score = 0.0
    total_score += self.heuristic_block_opponent_win(move, game_state)
    total_score += self.heuristic_your_strategy(move, game_state)  # Add this line
    return total_score
```

## Available Information

Your heuristics have access to rich game state information:

### `game_state` contains:
- `'board'`: Current board state (list of 9 positions)
- `'current_player'`: Whose turn it is
- `'available_moves'`: List of valid move positions
- `'board_evaluation'`: Strategic analysis including:
  - `'center_control'`: Whether center is occupied
  - `'corner_control'`: Number of corners occupied
  - `'x_threats'` / `'o_threats'`: Winning and blocking opportunities

### Utility methods:
- `self.player`: Your player (X or O)
- `self.opponent`: Opponent player  
- `self._create_temp_game()`: Create game copy for move simulation

## Example Heuristic Ideas

Here are some heuristics you might want to implement:

### Offensive Heuristics:
```python
def heuristic_take_winning_move(self, move, game_state):
    """Take immediate winning moves"""
    # Check if this move wins the game
    
def heuristic_create_threats(self, move, game_state):
    """Create multiple winning threats"""
    # Prefer moves that create multiple ways to win
```

### Positional Heuristics:
```python
def heuristic_control_center(self, move, game_state):
    """Prefer center position"""
    # Give bonus for taking center (position 4)
    
def heuristic_prefer_corners(self, move, game_state):
    """Prefer corner positions"""
    # Give bonus for corners (positions 0,2,6,8)
```

### Defensive Heuristics:
```python
def heuristic_avoid_opponent_forks(self, move, game_state):
    """Avoid moves that let opponent create forks"""
    # Analyze if move allows opponent multiple threats
```

## Testing Your Engine

### Quick Test:
```bash
python ttt_engine.py
```

### Comprehensive Testing:
```bash
python test_custom_engine.py
```

### Integration with Main Demo:
```python
from ttt_engine import TTTEngine
custom_engine = TTTEngine("My Engine", Player.X)
# Use with existing game manager
```

## Performance Baseline

With just the blocking heuristic, your engine should:
- Beat Random AI consistently (80%+ win rate)
- Struggle against Strategic AI (may lose frequently)
- Lose badly to Minimax AI (perfect play)

As you add more heuristics, you should see improvement against stronger opponents.

## Heuristic Scoring Guidelines

### Score Ranges:
- **100+**: Critical moves (winning, blocking wins)
- **50-99**: Strong positional advantages
- **10-49**: Minor advantages
- **0**: Neutral moves
- **Negative**: Moves to avoid

### Combining Heuristics:
- Scores are summed, so balance your ranges
- Critical heuristics should dominate minor ones
- Consider using weights/multipliers for fine-tuning

## Next Steps

1. **Start Simple**: Add one heuristic at a time
2. **Test Frequently**: Use `test_custom_engine.py` after each change
3. **Analyze Decisions**: Look at the decision logs to understand behavior
4. **Iterate**: Adjust scores based on performance

The framework is designed to make it easy to experiment. Have fun building your engine!