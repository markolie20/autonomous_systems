import pygame
import os
import pathlib

# Pygame-instellingen
pygame.init() # Initialize Pygame early for font loading if needed immediately
pygame.font.init() # Explicitly initialize font module

# Screen Dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 128, 0) # Changed from (34, 139, 34) to standard green
BLACK = (0, 0, 0)

# Card Dimensions
CARD_WIDTH, CARD_HEIGHT = 100, 150
MARGIN = 50 # Margin from the right edge
DECK_POS = (SCREEN_WIDTH - CARD_WIDTH - MARGIN, MARGIN)
PLAYER_CARD_START_POS = (300, 400)
DEALER_CARD_START_POS = (300, 100)
CARD_SPACING = 80 # Horizontal spacing between cards
MAX_CARDS_DISPLAY = 5 # Max cards to display per hand visually

# Font
FONT = pygame.font.Font(None, 36)
SMALL_FONT = pygame.font.Font(None, 24) # Added for potentially smaller text

# Paths
# IMPORTANT: Make sure this path is correct for your system
BASE_DIR = pathlib.Path(__file__).parent.parent # Gets the directory where constants.py is located
DATA_FOLDER = os.path.join(BASE_DIR, "data")
CARDS_FOLDER = os.path.join(DATA_FOLDER, "cards")
DECK_IMAGE_FILENAME = "back_of_card.png"
DECK_IMAGE_PATH = os.path.join(CARDS_FOLDER, DECK_IMAGE_FILENAME)


# Game Settings
SUITS = ['hearts', 'diamonds', 'clubs', 'spades']
VALUES = ['ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king']
DEFAULT_NUM_DECKS = 3
DEALER_STAND_THRESHOLD = 17
PLAYER_AI_STAND_THRESHOLD = 17 # For the simple AI

# Animation
CARD_ANIMATION_SPEED = 10 # Lower is faster for division-based movement

# Balance & Bet
STARTING_BALANCE = 1000
DEFAULT_BET = 50 

# Strategy Names (used in blackjack_env.py)
STRAT_DEALER_MIMIC = "DEALER_MIMIC"
STRAT_NEVER_BUST = "NEVER_BUST"
STRAT_BASIC_HARD = "BASIC_HARD" # Simplified basic strategy for hard hands
STRAT_CAUTIOUS = "CAUTIOUS"     # More conservative based on dealer card
STRAT_AGGRESSIVE = "AGGRESSIVE"   # Hits more often
# Threshold for the Dealer Mimic strategy (can be kept if useful)
PLAYER_AI_STAND_THRESHOLD = 17


# AI Strategy
# Choose one of the strategies for the AI player
AI_STRATEGY = STRAT_BASIC_HARD
