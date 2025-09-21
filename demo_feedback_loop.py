"""
Tic-Tac-Toe AI Demonstration
Shows the complete feedback loop between game state and AI decision making
"""

import time
from ttt_game import TicTacToeGame, Player, GameState
from ttt_ai import RandomAI, StrategicAI, MinimaxAI, LearningAI, AIGameManager

def demonstrate_single_game_analysis():
    """Demonstrate detailed analysis of a single game"""
    print("=" * 60)
    print("SINGLE GAME ANALYSIS - DETAILED FEEDBACK LOOP")
    print("=" * 60)
    
    # Create AI players with different strategies
    strategic_ai = StrategicAI("Strategic Player", Player.X)
    random_ai = RandomAI("Random Player", Player.O)
    
    # Create game manager
    manager = AIGameManager()
    
    # Play one game with detailed logging
    print(f"\nPlaying: {strategic_ai.name} (X) vs {random_ai.name} (O)")
    print("-" * 40)
    
    game = TicTacToeGame()
    players = {Player.X: strategic_ai, Player.O: random_ai}
    
    move_count = 0
    while game.game_state == GameState.ONGOING:
        move_count += 1
        current_ai = players[game.current_player]
        
        print(f"\nMove {move_count}: {current_ai.name}'s turn ({game.current_player.value})")
        game.print_board()
        
        # Get current game state (this is the feedback the AI receives)
        game_state = game.get_game_state()
        print(f"\nGame State Feedback:")
        print(f"  Available moves: {game_state['available_moves']}")
        print(f"  Board evaluation: {game_state['board_evaluation']}")
        
        # AI makes decision
        chosen_move = current_ai.make_decision(game_state)
        
        # Show decision reasoning
        if current_ai.decision_log:
            last_decision = current_ai.decision_log[-1]
            print(f"  AI Decision: Position {chosen_move}")
            print(f"  Reasoning: {last_decision['reasoning']}")
        
        # Execute move and get result feedback
        move_result = game.make_move(chosen_move)
        new_state = move_result['game_state']
        
        print(f"  Move executed successfully: {move_result['success']}")
        print(f"  New game state: {new_state['game_state']}")
        
        time.sleep(1)  # Pause for readability
    
    # Final game state
    print(f"\nFINAL RESULT:")
    game.print_board()
    final_state = game.get_game_state()
    print(f"Winner: {final_state['winner'] or 'Draw'}")
    print(f"Total moves: {final_state['move_count']}")
    
    # Show decision analysis for strategic AI
    strategic_analysis = strategic_ai.get_decision_analysis()
    print(f"\n{strategic_ai.name} Decision Analysis:")
    for i, decision in enumerate(strategic_analysis['decision_log']):
        print(f"  Move {i+1}: Position {decision['chosen_move']} - {decision['reasoning']}")

def demonstrate_learning_progression():
    """Demonstrate how a learning AI improves over time"""
    print("\n" + "=" * 60)
    print("LEARNING AI PROGRESSION ANALYSIS")
    print("=" * 60)
    
    # Create a learning AI and a consistent opponent
    learning_ai = LearningAI("Learning AI", Player.X, learning_rate=0.2)
    minimax_ai = MinimaxAI("Minimax AI", Player.O, max_depth=5)
    
    manager = AIGameManager()
    
    # Play multiple games and track performance
    game_batches = [10, 25, 50, 100]
    print(f"\nTraining {learning_ai.name} against {minimax_ai.name}")
    print("Tracking performance over time...")
    
    for batch_size in game_batches:
        # Play games
        for _ in range(batch_size - len(manager.game_history)):
            manager.play_game(learning_ai, minimax_ai, verbose=False)
        
        # Analyze performance
        performance = manager.analyze_performance(learning_ai, batch_size)
        
        print(f"\nAfter {batch_size} games:")
        print(f"  Win Rate: {performance['win_rate']:.2%}")
        print(f"  Wins: {performance['wins']}, Draws: {performance['draws']}, Losses: {performance['losses']}")
        
        # Show learned position values
        print(f"  Learned position values:")
        print(f"    {learning_ai.position_values[0]:.2f} | {learning_ai.position_values[1]:.2f} | {learning_ai.position_values[2]:.2f}")
        print(f"    {learning_ai.position_values[3]:.2f} | {learning_ai.position_values[4]:.2f} | {learning_ai.position_values[5]:.2f}")
        print(f"    {learning_ai.position_values[6]:.2f} | {learning_ai.position_values[7]:.2f} | {learning_ai.position_values[8]:.2f}")

def demonstrate_strategy_comparison():
    """Compare different AI strategies head-to-head"""
    print("\n" + "=" * 60)
    print("STRATEGY COMPARISON - AI vs AI TOURNAMENT")
    print("=" * 60)
    
    # Create different AI strategies
    random_ai = RandomAI("Random", Player.X)
    strategic_ai = StrategicAI("Strategic", Player.X)
    minimax_ai = MinimaxAI("Minimax", Player.X, max_depth=5)
    
    opponents = [
        RandomAI("Random Opponent", Player.O),
        StrategicAI("Strategic Opponent", Player.O)
    ]
    
    players = [random_ai, strategic_ai, minimax_ai]
    
    print("\nTournament Results (10 games each):")
    print("-" * 40)
    
    for player in players:
        total_wins = 0
        total_games = 0
        
        for opponent in opponents:
            manager = AIGameManager()
            
            # Play 10 games
            for _ in range(10):
                result = manager.play_game(player, opponent, verbose=False)
                if result['winner'] == player.player.value:
                    total_wins += 1
                total_games += 1
            
            performance = manager.analyze_performance(player, 10)
            print(f"{player.name} vs {opponent.name}: {performance['win_rate']:.1%} win rate")
        
        overall_win_rate = total_wins / total_games
        print(f"{player.name} overall: {overall_win_rate:.1%} win rate")
        print()

def demonstrate_decision_tree_analysis():
    """Show how different AIs approach the same game position"""
    print("\n" + "=" * 60)
    print("DECISION ANALYSIS - SAME POSITION, DIFFERENT STRATEGIES")
    print("=" * 60)
    
    # Create a specific game state
    game = TicTacToeGame()
    # Set up a specific board position
    moves = [4, 0, 1]  # X center, O corner, X top-middle
    for move in moves:
        game.make_move(move)
    
    print("Current board position:")
    game.print_board()
    
    current_state = game.get_game_state()
    print(f"Available moves: {current_state['available_moves']}")
    print(f"Current player: {current_state['current_player']}")
    
    # Create different AIs for the same position
    ais = [
        RandomAI("Random AI", Player.O),
        StrategicAI("Strategic AI", Player.O),
        MinimaxAI("Minimax AI", Player.O, max_depth=5)
    ]
    
    print(f"\nHow each AI approaches this position:")
    print("-" * 40)
    
    for ai in ais:
        chosen_move = ai.make_decision(current_state)
        if ai.decision_log:
            reasoning = ai.decision_log[-1]['reasoning']
            print(f"{ai.name}: Position {chosen_move}")
            print(f"  Reasoning: {reasoning}")
        print()

def main():
    """Main demonstration of the tic-tac-toe AI system"""
    print("TIC-TAC-TOE AI SYSTEM DEMONSTRATION")
    print("Exploring Game State -> Decision -> Action -> Feedback Loops")
    
    try:
        # 1. Detailed single game analysis
        demonstrate_single_game_analysis()
        
        # 2. Learning progression over time
        demonstrate_learning_progression()
        
        # 3. Strategy comparison
        demonstrate_strategy_comparison()
        
        # 4. Decision analysis for same position
        demonstrate_decision_tree_analysis()
        
        print("\n" + "=" * 60)
        print("DEMONSTRATION COMPLETE")
        print("=" * 60)
        print("\nKey Concepts Demonstrated:")
        print("✓ Game state feedback to AI decision makers")
        print("✓ Different decision-making strategies")
        print("✓ Action execution and result feedback")
        print("✓ Learning and adaptation over time")
        print("✓ Performance analysis and comparison")
        print("\nThe feedback loop architecture is now ready for:")
        print("• Integration with other games")
        print("• More sophisticated AI algorithms")
        print("• Real-time performance monitoring")
        print("• Advanced learning techniques")
        
    except KeyboardInterrupt:
        print("\n\nDemonstration interrupted by user.")
    except Exception as e:
        print(f"\nError during demonstration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()