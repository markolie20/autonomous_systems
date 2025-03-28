import pygame
from constants import (
    GREEN, WHITE, BLACK, FONT, SMALL_FONT, SCREEN_WIDTH, SCREEN_HEIGHT,
    PLAYER_CARD_START_POS, DEALER_CARD_START_POS, CARD_SPACING, CARD_WIDTH, CARD_HEIGHT,
    MAX_CARDS_DISPLAY, DECK_POS, DEFAULT_NUM_DECKS,
    DEALER_STAND_THRESHOLD, PLAYER_AI_STAND_THRESHOLD,
    STARTING_BALANCE, DEFAULT_BET,  AI_STRATEGY, STRAT_DEALER_MIMIC, STRAT_NEVER_BUST, STRAT_BASIC_HARD,
    STRAT_CAUTIOUS, STRAT_AGGRESSIVE, PLAYER_AI_STAND_THRESHOLD
)
from utils import calculate_hand_value, create_deck
from card import Card

class BlackjackEnv:
    """Represents the Blackjack game environment with Pygame visualization."""
    # Add deck_image and card_images arguments to __init__
    def __init__(self, deck_image, card_images, num_decks=DEFAULT_NUM_DECKS):
        self.num_decks = num_decks
        self.deck = create_deck(self.num_decks)
        self.player_hand = []
        self.dealer_hand = []
        self.player_cards = []
        self.dealer_cards = []

        # Store the loaded images
        self.deck_image = deck_image
        self.card_images = card_images 

        self.player_positions = [
            (PLAYER_CARD_START_POS[0] + i * CARD_SPACING, PLAYER_CARD_START_POS[1])
            for i in range(MAX_CARDS_DISPLAY * 2)
        ]
        self.dealer_positions = [
            (DEALER_CARD_START_POS[0] + i * CARD_SPACING, DEALER_CARD_START_POS[1])
            for i in range(MAX_CARDS_DISPLAY * 2)
        ]

        self.balance = STARTING_BALANCE
        self.current_bet = 0
        self.game_state = "BETTING"
        self.message = ""
        self.round_over_timer = 0

    def check_deck(self):
        """Checks if the deck is low and reshuffles if necessary."""
        reshuffle_threshold = (52 * self.num_decks) // 4
        if len(self.deck) < reshuffle_threshold:
            print(f"Deck low ({len(self.deck)} cards). Reshuffling...")
            self.deck = create_deck(self.num_decks)

    def reset_round(self):
        """Resets hands and prepares for a new round."""
        self.player_hand = []
        self.dealer_hand = []
        self.player_cards = []
        self.dealer_cards = []
        self.message = ""
        self.current_bet = 0
        self.game_state = "BETTING"
        self.check_deck()

    def place_bet(self, amount=DEFAULT_BET):
        """Places the player's bet for the round."""
        if self.game_state != "BETTING": return False
        #if amount > self.balance:
        #    self.message = f"Not enough funds! (Need €{amount})"
        #    return False
        if amount <= 0:
            self.message = "Bet must be positive!"
            return False
        self.current_bet = amount
        self.message = f"Bet placed: €{self.current_bet}"
        self.game_state = "DEALING"
        return True

    def spawn_card(self, card_value, suit, start_pos, end_pos):
        """Creates a Card object for animation."""
        # Pass the stored card_images dictionary to the Card constructor
        return Card(card_value, suit, start_pos, end_pos, self.card_images)

    def deal_card(self, to_player=True):
        """Deals one card from the deck to player or dealer."""
        if not self.deck:
            self.check_deck()
            if not self.deck: return

        card_value, suit = self.deck.pop()
        start_pos = DECK_POS

        hand = self.player_hand if to_player else self.dealer_hand
        card_objects = self.player_cards if to_player else self.dealer_cards
        positions = self.player_positions if to_player else self.dealer_positions

        if len(hand) < len(positions):
            end_pos = positions[len(hand)]
            card_obj = self.spawn_card(card_value, suit, start_pos, end_pos)
            card_objects.append(card_obj)
            hand.append((card_value, suit))
        else:
             print(f"Warning: {'Player' if to_player else 'Dealer'} hand limit reached for display positions.")
             hand.append((card_value, suit))

        # print(f"Dealt {'Player' if to_player else 'Dealer'}: {card_value} of {suit}. Deck: {len(self.deck)}")

    def deal_initial_cards(self):
        """Deals the starting hands for a round."""
        if self.game_state != "DEALING": return

        deals = [(True, 100), (False, 100), (True, 100), (False, 0)]
        for to_player, delay in deals:
             self.deal_card(to_player=to_player)
             if delay > 0:
                  pygame.time.wait(delay)

        for card_obj in self.player_cards:
             card_obj.position = list(card_obj.end_pos) 
             card_obj.is_moving = False
        for card_obj in self.dealer_cards:
             card_obj.position = list(card_obj.end_pos) 
             card_obj.is_moving = False

        player_score = calculate_hand_value(self.player_hand)
        dealer_score = calculate_hand_value(self.dealer_hand)
        player_has_blackjack = (player_score == 21 and len(self.player_hand) == 2)
        dealer_has_blackjack = (dealer_score == 21 and len(self.dealer_hand) == 2)

        if player_has_blackjack or dealer_has_blackjack:
             self.resolve_round()
        else:
             self.game_state = "PLAYER_TURN"
             self.message = "Player's Turn (Hit or Stand)"

    def player_hit(self):
        """Player chooses to take another card."""
        if self.game_state != "PLAYER_TURN": return
        self.deal_card(to_player=True)
        player_score = calculate_hand_value(self.player_hand)
        self.message = f"Player Hits. Score: {player_score}"
        if player_score > 21:
            self.message = f"Player Busts! Score: {player_score}"
            self.resolve_round()
        elif player_score == 21:
             self.message = f"Player has 21! Dealer's turn."
             self.game_state = "DEALER_TURN"

    def player_stand(self):
        """Player chooses to stand."""
        if self.game_state != "PLAYER_TURN": return
        player_score = calculate_hand_value(self.player_hand)
        self.message = f"Player Stands. Score: {player_score}. Dealer's Turn."
        self.game_state = "DEALER_TURN"

    def dealer_play(self, screen): 
        """Dealer plays according to house rules. Returns True if play occurred."""
        if self.game_state != "DEALER_TURN": return False

        dealer_score = calculate_hand_value(self.dealer_hand)
        played_turn = False

        while dealer_score < DEALER_STAND_THRESHOLD:
            played_turn = True
            print(f"Dealer has {dealer_score}, Dealer Hits.")
            self.message = f"Dealer Hits..."

            # Render BEFORE dealing the card
            self.render(screen)
            pygame.display.flip()
            pygame.time.wait(700) 

            self.deal_card(to_player=False)
            dealer_score = calculate_hand_value(self.dealer_hand)
            self.message = f"Dealer has {dealer_score}" 

            # Render AFTER dealing the card
            self.render(screen)
            pygame.display.flip()
            pygame.time.wait(700) 

            if dealer_score > 21:
                print(f"Dealer Busts! Score: {dealer_score}")
                self.message = f"Dealer Busts! Score: {dealer_score}"
                break

        if not played_turn and dealer_score <= 21:
            print(f"Dealer Stands. Score: {dealer_score}")
            self.message = f"Dealer Stands. Score: {dealer_score}"
            self.render(screen) 
            pygame.display.flip()
            pygame.time.wait(1000)

        self.resolve_round()
        return True

    def resolve_round(self):
        """Determines the winner and updates balance."""
        if self.game_state == "ROUND_OVER": return  # Avoid double resolving

        self.game_state = "ROUND_OVER"
        player_score = calculate_hand_value(self.player_hand)
        dealer_score = calculate_hand_value(self.dealer_hand)

        player_bj = (player_score == 21 and len(self.player_hand) == 2)
        dealer_bj = (dealer_score == 21 and len(self.dealer_hand) == 2)

        result_message = ""
        payout = 0  # Standaard geen verandering in balans

        print("\n--- Round Result ---")
        print(f"Player Hand: {self.player_hand} (Score: {player_score})")
        print(f"Dealer Hand: {self.dealer_hand} (Score: {dealer_score})")

        if player_bj and dealer_bj:
            result_message = "Push! Both have Blackjack!"
            payout = 0  # Bet returned
        elif player_bj:
            result_message = "Player Blackjack! 🎉"
            payout = int(self.current_bet * 1.5)  # BJ betaalt 3:2
        elif dealer_bj:
            result_message = "Dealer Blackjack! 😢"
            payout = -self.current_bet  # Inzet kwijt
        elif player_score > 21:
            result_message = "Player Busts! Dealer wins."
            payout = -self.current_bet  # Inzet kwijt
        elif dealer_score > 21:
            result_message = "Dealer Busts! Player wins!"
            payout = self.current_bet  # Even money
        elif player_score > dealer_score:
            result_message = "Player wins!"
            payout = self.current_bet  # Even money
        elif dealer_score > player_score:
            result_message = "Dealer wins."
            payout = -self.current_bet  # Inzet kwijt
        else:  # player_score == dealer_score
            result_message = "Push! (Tie)"
            payout = 0  # Bet terug

        
        self.balance += payout  # Payout verwerken
        if payout == 0:  # Als er niet verloren is, zet terug
            self.balance += self.current_bet

        print(result_message)
        print(f"Bet: €{self.current_bet}, Payout: €{payout}, New Balance: €{self.balance}")
        print("--------------------\n")

        self.message = result_message + f" | Balance: €{self.balance}"
        self.round_over_timer = pygame.time.get_ticks()


    def get_dealer_upcard_value(self):
        """Gets the numeric value of the dealer's visible card."""
        if not self.dealer_hand: return 0
        upcard_val, _ = self.dealer_hand[0]
        if upcard_val in ['jack', 'queen', 'king', '10']: return 10
        if upcard_val == 'ace': return 11 # Treat Ace as 11 for strategy lookup
        try: return int(upcard_val)
        except ValueError: return 0

    def player_ai_action(self):
        """AI decides action for the player based on the selected strategy."""
        if self.game_state != "PLAYER_TURN":
            print("DEBUG: AI Action - Called but not player's turn.")
            return

        player_score = calculate_hand_value(self.player_hand)
        dealer_upcard = self.get_dealer_upcard_value()


        print(f"DEBUG: AI Turn - Strategy: {AI_STRATEGY}, Score: {player_score}, Dealer Up: {dealer_upcard}")

        # --- Strategy Implementation ---

        # 1. Dealer Mimic
        if AI_STRATEGY == STRAT_DEALER_MIMIC:
            if player_score < PLAYER_AI_STAND_THRESHOLD: # Typically 17
                 print(f"AI ({STRAT_DEALER_MIMIC}): HIT (<{PLAYER_AI_STAND_THRESHOLD})")
                 self.player_hit()
            else:
                 print(f"AI ({STRAT_DEALER_MIMIC}): STAND (>={PLAYER_AI_STAND_THRESHOLD})")
                 self.player_stand()

        # 2. Never Bust
        elif AI_STRATEGY == STRAT_NEVER_BUST:
            NEVER_BUST_THRESHOLD = 12 # Stand on 12 or higher
            if player_score < NEVER_BUST_THRESHOLD:
                 print(f"AI ({STRAT_NEVER_BUST}): HIT (<{NEVER_BUST_THRESHOLD})")
                 self.player_hit()
            else:
                 print(f"AI ({STRAT_NEVER_BUST}): STAND (>={NEVER_BUST_THRESHOLD})")
                 self.player_stand()

        # 3. Basic Hard Hands (Simplified)
        elif AI_STRATEGY == STRAT_BASIC_HARD:
            if player_score >= 17:
                 print(f"AI ({STRAT_BASIC_HARD}): STAND (Hard 17+)")
                 self.player_stand()
            elif 13 <= player_score <= 16 and 2 <= dealer_upcard <= 6:
                 print(f"AI ({STRAT_BASIC_HARD}): STAND (Hard 13-16 vs Dealer 2-6)")
                 self.player_stand()
            elif player_score == 12 and 4 <= dealer_upcard <= 6:
                 print(f"AI ({STRAT_BASIC_HARD}): STAND (Hard 12 vs Dealer 4-6)")
                 self.player_stand()
            else: # Hit 11 or less, 12 vs 2,3,7+, 13-16 vs 7+
                 print(f"AI ({STRAT_BASIC_HARD}): HIT (Default Hard)")
                 self.player_hit()

        # 4. Cautious (Stands earlier vs low dealer card)
        elif AI_STRATEGY == STRAT_CAUTIOUS:
            stand_threshold = 15 
            if 2 <= dealer_upcard <= 6
                 stand_threshold = 12 
            elif dealer_upcard >= 7: 
                 stand_threshold = 17

            if player_score < stand_threshold:
                 print(f"AI ({STRAT_CAUTIOUS}): HIT (<{stand_threshold} vs Dealer {dealer_upcard})")
                 self.player_hit()
            else:
                 print(f"AI ({STRAT_CAUTIOUS}): STAND (>={stand_threshold} vs Dealer {dealer_upcard})")
                 self.player_stand()

        # 5. Aggressive (Hits more, less fear of busting)
        elif AI_STRATEGY == STRAT_AGGRESSIVE:
            AGGRESSIVE_THRESHOLD = 19
            if player_score < AGGRESSIVE_THRESHOLD:
                 print(f"AI ({STRAT_AGGRESSIVE}): HIT (<{AGGRESSIVE_THRESHOLD})")
                 self.player_hit()
            else:
                 print(f"AI ({STRAT_AGGRESSIVE}): STAND (>={AGGRESSIVE_THRESHOLD})")
                 self.player_stand()

        else:
            print(f"AI (Unknown Strategy '{AI_STRATEGY}'): Defaulting to Dealer Mimic")
            if player_score < PLAYER_AI_STAND_THRESHOLD:
                 self.player_hit()
            else:
                 self.player_stand()

    def render(self, screen):
        """Draws the game state onto the screen."""
        screen.fill(GREEN)

        # Draw Deck using stored self.deck_image
        if self.deck_image:
            screen.blit(self.deck_image, DECK_POS)
        deck_count_text = SMALL_FONT.render(f"{len(self.deck)}", True, WHITE)
        deck_text_pos = (DECK_POS[0] + self.deck_image.get_width() + 5, DECK_POS[1] + 10) if self.deck_image else (DECK_POS[0] + 5, DECK_POS[1] + CARD_HEIGHT + 5)
        screen.blit(deck_count_text, deck_text_pos)

        # Draw Dealer Cards & Score
        dealer_score_display = 0
        dealer_score_str = "?"
        show_hole_card = self.game_state not in ["PLAYER_TURN", "DEALING", "BETTING"]

        if self.dealer_hand: # Only calculate if dealer has cards
            if show_hole_card:
                dealer_score_display = calculate_hand_value(self.dealer_hand)
                dealer_score_str = str(dealer_score_display)
            else:
                # Only show value of first card
                dealer_score_display = calculate_hand_value([self.dealer_hand[0]])
                dealer_score_str = str(dealer_score_display) + "+?"

        for i, card_obj in enumerate(self.dealer_cards):
            is_hole_card = (i == 1) 
            if is_hole_card and not show_hole_card:
                 # Draw card back
                 if self.deck_image:
                     screen.blit(self.deck_image, card_obj.end_pos)
                 else: # Simple placeholder back
                     pygame.draw.rect(screen, (0,0,100), (*card_obj.end_pos, CARD_WIDTH, CARD_HEIGHT))
            else:
                 card_obj.update_position()
                 card_obj.draw(screen)

        dealer_text = FONT.render(f"Dealer: {dealer_score_str}", True, WHITE)
        screen.blit(dealer_text, (DEALER_CARD_START_POS[0], DEALER_CARD_START_POS[1] - 40))

        # Draw Player Cards & Score
        player_score = calculate_hand_value(self.player_hand)
        for card_obj in self.player_cards:
            card_obj.update_position()
            card_obj.draw(screen)

        player_text = FONT.render(f"Player: {player_score}", True, WHITE)
        screen.blit(player_text, (PLAYER_CARD_START_POS[0], PLAYER_CARD_START_POS[1] - 40))

        # Draw Balance, Bet, and Message
        balance_text = FONT.render(f"Balance: €{self.balance}", True, WHITE)
        screen.blit(balance_text, (10, 10))
        bet_text = FONT.render(f"Bet: €{self.current_bet}", True, WHITE)
        screen.blit(bet_text, (10, 50))

        message_text = FONT.render(self.message, True, BLACK)
        message_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        screen.blit(message_text, message_rect)

        # Draw Buttons (visibility depends on state)
        hit_rect = pygame.Rect(SCREEN_WIDTH - 160, SCREEN_HEIGHT - 110, 150, 40)
        stand_rect = pygame.Rect(SCREEN_WIDTH - 160, SCREEN_HEIGHT - 60, 150, 40)
        bet_rect = pygame.Rect(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 - 20, 150, 40)

        if self.game_state == "PLAYER_TURN":
            pygame.draw.rect(screen, (0, 180, 0), hit_rect)
            hit_text = FONT.render("HIT (H)", True, WHITE)
            screen.blit(hit_text, (hit_rect.x + 10, hit_rect.y + 5))

            pygame.draw.rect(screen, (180, 0, 0), stand_rect)
            stand_text = FONT.render("STAND (S)", True, WHITE)
            screen.blit(stand_text, (stand_rect.x + 10, stand_rect.y + 5))

        elif self.game_state == "BETTING":
             pygame.draw.rect(screen, (0, 0, 180), bet_rect)
             bet_btn_text = FONT.render(f"BET €{DEFAULT_BET} (B)", True, WHITE)
             screen.blit(bet_btn_text, (bet_rect.x + 10, bet_rect.y + 5))