"""
Test Custom TTT Engine against existing AI strategies
"""

from ttt_game import Player
from ttt_ai import RandomAI, StrategicAI, MinimaxAI, AIGameManager
from ttt_engine import TTTEngine

def test_engine_performance():
    """Test the custom engine against different AI strategies"""
    print("CUSTOM TTT ENGINE PERFORMANCE TEST")
    print("=" * 50)
    
    # Create custom engine
    custom_engine = TTTEngine("Custom Engine", Player.X)
    
    # Create different opponents
    opponents = [
        RandomAI("Random AI", Player.O),
        StrategicAI("Strategic AI", Player.O),
        MinimaxAI("Minimax AI", Player.O, max_depth=5)
    ]
    
    # Test against each opponent
    for opponent in opponents:
        print(f"\nTesting vs {opponent.name}")
        print("-" * 30)
        
        manager = AIGameManager()
        wins = 0
        draws = 0
        
        # Play 10 games
        for game_num in range(10):
            result = manager.play_game(custom_engine, opponent, verbose=False)
            
            if result['winner'] == custom_engine.player.value:
                wins += 1
            elif result['winner'] is None:
                draws += 1
                
        losses = 10 - wins - draws
        win_rate = wins / 10
        
        print(f"Results: {wins} wins, {draws} draws, {losses} losses")
        print(f"Win rate: {win_rate:.1%}")
        
        # Show some decision examples
        if custom_engine.decision_log:
            print("Sample decisions:")
            for i, decision in enumerate(custom_engine.decision_log[-3:], 1):
                print(f"  {i}. {decision['reasoning']}")
        
        # Reset decision log for next opponent
        custom_engine.decision_log = []
        custom_engine.move_history = []

def demo_single_game():
    """Demonstrate a single game with detailed output"""
    print("\n" + "=" * 50)
    print("DETAILED SINGLE GAME DEMONSTRATION")
    print("=" * 50)
    
    custom_engine = TTTEngine("Custom Engine", Player.X)
    strategic_ai = StrategicAI("Strategic AI", Player.O)
    
    manager = AIGameManager()
    
    print(f"\nPlaying: {custom_engine.name} (X) vs {strategic_ai.name} (O)")
    result = manager.play_game(custom_engine, strategic_ai, verbose=True)
    
    print(f"\nCustom Engine decision analysis:")
    for i, decision in enumerate(custom_engine.decision_log, 1):
        print(f"  Move {i}: {decision['reasoning']}")

if __name__ == "__main__":
    test_engine_performance()
    demo_single_game()