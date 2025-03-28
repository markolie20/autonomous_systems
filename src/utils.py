import pygame
import os
import random
from constants import (
    CARDS_FOLDER, DECK_IMAGE_PATH, CARD_WIDTH, CARD_HEIGHT, WHITE,
    SUITS, VALUES, DEFAULT_NUM_DECKS
)

def load_card_images():
    """Loads all card images and the deck back image."""
    images = {}
    print(f"Loading card images from: {CARDS_FOLDER}")
    print(CARDS_FOLDER, os.path.isdir(CARDS_FOLDER))
    if not os.path.isdir(CARDS_FOLDER):
        print(f"ERROR: Cards folder not found at {CARDS_FOLDER}")
        return None, {} # Return None for deck_image if folder missing

    for suit in SUITS:
        for value in VALUES:
            card_key = f"{value}_of_{suit}"
            card_filename = f"{card_key}.png"
            card_path = os.path.join(CARDS_FOLDER, card_filename)
            try:
                if os.path.exists(card_path):
                    image = pygame.image.load(card_path).convert_alpha()
                    images[card_key] = pygame.transform.scale(image, (CARD_WIDTH, CARD_HEIGHT))
                else:
                    print(f"Warning: Card image not found: {card_path}. Creating placeholder.")
                    images[card_key] = create_placeholder_card(value, suit)
            except pygame.error as e:
                print(f"Error loading image {card_path}: {e}")
                images[card_key] = create_placeholder_card(value, suit) # Use placeholder on error

    # Load deck image
    deck_image = None
    print(f"Loading deck image from: {DECK_IMAGE_PATH}")
    try:
        if os.path.exists(DECK_IMAGE_PATH):
            deck_image = pygame.image.load(DECK_IMAGE_PATH).convert_alpha()
            deck_image = pygame.transform.scale(deck_image, (CARD_WIDTH, CARD_HEIGHT))
        else:
            print(f"ERROR: Deck image not found at {DECK_IMAGE_PATH}")
            # Create a simple placeholder for the deck back
            deck_image = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
            deck_image.fill((0, 50, 0)) # Dark green
            pygame.draw.rect(deck_image, WHITE, deck_image.get_rect(), 3)

    except pygame.error as e:
        print(f"Error loading deck image {DECK_IMAGE_PATH}: {e}")
        # Create placeholder if loading fails
        deck_image = pygame.Surface((CARD_WIDTH, CARD_HEIGHT)); deck_image.fill(WHITE)

    print(f"Loaded {len(images)} card images.")
    return deck_image, images

def create_placeholder_card(value, suit):
    """Creates a simple placeholder surface for a missing card."""
    surf = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
    surf.fill(WHITE)
    pygame.draw.rect(surf, (100, 100, 100), surf.get_rect(), 1) # Border
    font = pygame.font.Font(None, 18)
    text = font.render(f"{value[:1].upper()}{suit[:1].upper()}", True, (0, 0, 0))
    text_rect = text.get_rect(center=(CARD_WIDTH//2, CARD_HEIGHT//2))
    surf.blit(text, text_rect)
    return surf


def get_card_image_key(card_value, suit):
    """Generates the dictionary key for accessing a card's image."""
    return f"{card_value}_of_{suit}"

def calculate_hand_value(hand):
    """Calculates the value of a hand in Blackjack."""
    value = 0
    aces = 0
    for card_value, _ in hand: # card is a tuple (value, suit)
        if card_value in ['jack', 'queen', 'king']:
            value += 10
        elif card_value == 'ace':
            aces += 1
            value += 11 # Add 11 for Ace initially
        else:
            try:
                value += int(card_value)
            except ValueError:
                print(f"Error: Could not convert card value '{card_value}' to int.")
                # Handle error case, e.g., assign 0 or raise exception
                value += 0

    # Adjust for Aces if value is over 21
    while value > 21 and aces > 0:
        value -= 10
        aces -= 1

    return value

def create_deck(num_decks=DEFAULT_NUM_DECKS):
    """Creates and shuffles a Blackjack deck with a specified number of standard decks."""
    if num_decks < 1:
        num_decks = 1
        print("Warning: Number of decks must be at least 1. Using 1 deck.")

    deck = [(value, suit) for _ in range(num_decks) for suit in SUITS for value in VALUES]
    random.shuffle(deck)
    print(f"Created a shuffled deck with {num_decks} standard deck(s), total {len(deck)} cards.")
    return deck