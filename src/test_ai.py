import os 
import pygame 
import numpy as np 
import pandas as pd

from constants import ( SCREEN_WIDTH, SCREEN_HEIGHT, DEFAULT_BET, STRAT_DEALER_MIMIC, STRAT_NEVER_BUST, STRAT_BASIC_HARD, STRAT_CAUTIOUS, STRAT_AGGRESSIVE ) 
from blackjack_env import BlackjackEnv 
from utils import load_card_images

def simulate_ai(strategy, rounds, bet_amount): # Override the global AI strategy. import constants constants.AI_STRATEGY = strategy
    # Create a hidden screen (required by some game functions)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags=pygame.HIDDEN)

    # Load game assets.
    deck_image, card_images = load_card_images()
    if deck_image is None or not card_images:
        print("Failed to load assets.")
        return []

    # Create a new Blackjack environment.
    env = BlackjackEnv(deck_image, card_images, num_decks=3)
    results = []

    for r in range(1, rounds + 1):
        if env.balance < bet_amount:
            print(f"Insufficient funds for strategy {strategy} at round {r}. Ending simulation for this AI.")
            break
        
        old_balance = env.balance

        # Place bet, which sets the game_state to "DEALING"
        if not env.place_bet(bet_amount):
            print(f"Failed to place bet on round {r} for strategy {strategy}.")
            break

        # Deal the initial cards.
        env.deal_initial_cards()

        # Let the AI play until the round is resolved.
        while env.game_state == "PLAYER_TURN":
            env.player_ai_action()

        if env.game_state == "DEALER_TURN":
            env.dealer_play(screen)

        # Round is now over. Calculate result.
        new_balance = env.balance
        net_change = new_balance - old_balance
        outcome = "win" if net_change > 0 else "loss" if net_change < 0 else "push"

        # Record round details.
        results.append({
            "round": r,
            "ai_strategy": strategy,
            "bet": bet_amount,
            "old_balance": old_balance,
            "new_balance": new_balance,
            "result": outcome
        })

        # Reset environment for next round.
        env.reset_round()

    return results
def main(): # Initialize pygame. pygame.init() pygame.font.init() # Optionally disable delays to speed up simulation. pygame.time.wait = lambda x: None
    rounds_per_strategy = 100
    bet_amount = DEFAULT_BET

    strategies = [
        STRAT_DEALER_MIMIC,
        STRAT_NEVER_BUST,
        STRAT_BASIC_HARD,
        STRAT_CAUTIOUS,
        STRAT_AGGRESSIVE
    ]

    all_results = []
    for strat in strategies:
        print(f"Simulating strategy: {strat}")
        results = simulate_ai(strat, rounds_per_strategy, bet_amount)
        all_results.extend(results)

    # Convert results to a pandas DataFrame.
    df = pd.DataFrame(all_results)

    # Optionally use numpy to ensure numerical types, if needed.
    numeric_cols = ["round", "bet", "old_balance", "new_balance"]
    df[numeric_cols] = df[numeric_cols].apply(np.int64)

    # Write the DataFrame to a CSV file.
    output_folder = 'tests'
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, "ai_simulation_results.csv")
    
    df.to_csv(output_file, index=False)

    print(f"Simulation complete. Results saved to {output_file}.")
    pygame.quit()
    
if __name__ == "__main__": main()