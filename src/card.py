import pygame
from utils import get_card_image_key
from constants import CARD_WIDTH, CARD_HEIGHT, CARD_ANIMATION_SPEED, WHITE

class Card:
    """Represents a playing card with visual properties and animation."""
    def __init__(self, card_value, suit, start_pos, end_pos, card_images_dict):
        self.card_value = card_value
        self.suit = suit
        self.image_key = get_card_image_key(card_value, suit)
        self.image = card_images_dict.get(self.image_key)

        if self.image is None:
             print(f"ERROR: Image not found for key '{self.image_key}' in card_images_dict.")
             self.image = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
             self.image.fill(WHITE)
             pygame.draw.rect(self.image, (255, 0, 0), self.image.get_rect(), 3)

        self.start_pos = tuple(start_pos)
        self.end_pos = tuple(end_pos)
        self.position = list(start_pos)
        self.is_moving = True

    def update_position(self):
        """Moves the card towards its end position smoothly."""
        if self.is_moving:
            target_x, target_y = self.end_pos
            current_x, current_y = self.position

            dx = target_x - current_x
            dy = target_y - current_y
            dist = (dx**2 + dy**2)**0.5 # Calculate remaining distance

            # --- Stopping Condition 1: Check if already very close ---
            # Use a small threshold instead of checking for exact zero distance
            CLOSE_ENOUGH_THRESHOLD = 100 # pixels (adjust if needed)
            if dist < CLOSE_ENOUGH_THRESHOLD:
                self.position = list(self.end_pos) # Snap to exact final position
                self.is_moving = False
                return # Stop processing for this card this frame

            # --- Calculate Movement Step ---
            move_speed = CARD_ANIMATION_SPEED
            # Avoid division by zero if dist happens to be exactly 0 (though threshold should catch it)
            if dist == 0:
                 self.position = list(self.end_pos)
                 self.is_moving = False
                 return

            step_x = (dx / dist) * move_speed
            step_y = (dy / dist) * move_speed

            # --- Stopping Condition 2: Check if the step would overshoot ---
            # If the calculated step is larger than the remaining distance, just move to the target
            if abs(step_x) >= abs(dx) and abs(step_y) >= abs(dy):
                 # print(f"DEBUG: Card {self.card_value} {self.suit} stopped - Overshot/Arrived") # Optional debug
                 self.position = list(self.end_pos)
                 self.is_moving = False
            else:
                 # --- Update position normally ---
                 self.position[0] += step_x
                 self.position[1] += step_y
                 # Safety check: If somehow landed exactly on target after move
                 if self.position[0] == target_x and self.position[1] == target_y:
                      self.is_moving = False

    def draw(self, surface):
        """Draws the card on the given surface."""
        int_pos = (int(self.position[0]), int(self.position[1]))
        surface.blit(self.image, int_pos)
