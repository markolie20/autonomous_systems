import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, DEFAULT_BET
from blackjack_env import BlackjackEnv
from utils import load_card_images

def game_loop():
    """Main game loop for the Pygame Blackjack game."""
    pygame.init()
    # It's crucial to initialize font module if using fonts anywhere
    pygame.font.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Blackjack AI Simulation")
    clock = pygame.time.Clock()

    # --- Load Assets AFTER display mode is set ---
    try:
        deck_image, card_images = load_card_images()
        if deck_image is None or not card_images:
             raise ValueError("Asset loading failed.") # Raise error if loading returns None/empty
    except Exception as e: # Catch Pygame errors or other issues during load
        print(f"\nFATAL ERROR: Failed to load essential game assets: {e}")
        print("Please ensure Pygame is installed correctly and asset paths are correct.")
        print("Check 'constants.py' for BASE_DIR, DATA_FOLDER, CARDS_FOLDER.")
        pygame.quit() # Clean up pygame
        return # Exit if assets are missing

    # --- Create Game Environment ---
    # Pass the loaded assets to the constructor
    game = BlackjackEnv(deck_image=deck_image, card_images=card_images, num_decks=3)
    running = True
    player_is_ai = False # Set to False for manual play

    # Initial state setup
    game.reset_round()
    # Set initial message for betting state
    if game.game_state == "BETTING":
         game.message = f"Click BET or press B to start round (Bet: €{DEFAULT_BET})"


    while running:
        # --- Event Handling ---
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                 if game.game_state == "BETTING":
                     if event.key == pygame.K_b: # Place bet
                         if game.place_bet(DEFAULT_BET):
                              # Bet placed, schedule dealing (using timer is smoother than direct call)
                              pygame.time.set_timer(pygame.USEREVENT + 1, 200, 1) # Deal timer (short delay)
                 elif game.game_state == "PLAYER_TURN" and not player_is_ai:
                     if event.key == pygame.K_h: # Hit
                         game.player_hit()
                     elif event.key == pygame.K_s: # Stand
                         game.player_stand()
                 elif game.game_state == "ROUND_OVER" and game.balance <= 0:
                     if event.key == pygame.K_q: # Quit on game over
                          running = False
                 elif game.game_state == "ROUND_OVER":
                      # Allow pressing 'B' to start next round early
                      if event.key == pygame.K_b:
                           if game.balance > 0:
                                game.reset_round()
                                game.message = f"Click BET or press B (Bet: €{DEFAULT_BET})"


            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Left click
                 mouse_pos = event.pos
                 # Define button rects here or get from constants/env if preferred
                 hit_rect = pygame.Rect(SCREEN_WIDTH - 160, SCREEN_HEIGHT - 110, 150, 40)
                 stand_rect = pygame.Rect(SCREEN_WIDTH - 160, SCREEN_HEIGHT - 60, 150, 40)
                 bet_rect = pygame.Rect(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 - 20, 150, 40)

                 if game.game_state == "BETTING" and bet_rect.collidepoint(mouse_pos):
                      if game.place_bet(DEFAULT_BET):
                           pygame.time.set_timer(pygame.USEREVENT + 1, 200, 1) # Deal timer
                 elif game.game_state == "PLAYER_TURN" and not player_is_ai:
                      if hit_rect.collidepoint(mouse_pos):
                           game.player_hit()
                      elif stand_rect.collidepoint(mouse_pos):
                           game.player_stand()
                 elif game.game_state == "ROUND_OVER" and bet_rect.collidepoint(mouse_pos): # Allow clicking bet button again
                      if game.balance > 0:
                           game.reset_round()
                           game.message = f"Click BET or press B (Bet: €{DEFAULT_BET})"


            if event.type == pygame.USEREVENT + 1: # Timer for dealing
                 game.deal_initial_cards()
                 pygame.time.set_timer(pygame.USEREVENT + 1, 0) # Stop timer

        # --- Game Logic / State Updates ---
        # Check if all cards finished animating before processing next turn logic
        all_cards_stopped = not any(c.is_moving for c in game.player_cards + game.dealer_cards)
        # print(f"DEBUG: Loop Start - State: {game.game_state}, AI: {player_is_ai}, Cards Moving: {not all_cards_stopped}")
        if all_cards_stopped:
             if game.game_state == "PLAYER_TURN" and player_is_ai:
                 pygame.time.wait(400) # AI thinking pause
                 game.player_ai_action()

             elif game.game_state == "DEALER_TURN":
                 # Dealer logic might involve pauses, so pass screen for updates
                 game.dealer_play(screen) # dealer_play now handles resolve_round

             elif game.game_state == "ROUND_OVER":
                 current_time = pygame.time.get_ticks()
                 # Automatically reset after a delay IF balance is positive
                 if game.balance > 0 and current_time - game.round_over_timer > 2500: # Wait 2.5 seconds
                      game.reset_round()
                      game.message = f"Click BET or press B (Bet: €{DEFAULT_BET})"
                 elif game.balance <= 0:
                      game.message = "Game Over - Out of Balance! (Press Q to quit)"


        # --- Drawing ---
        game.render(screen) # Render the current state
        pygame.display.flip() # Update the full display

        # --- Frame Rate Control ---
        clock.tick(60) # Limit FPS

    pygame.quit()
    print("Game exited.")

if __name__ == "__main__":
    game_loop()