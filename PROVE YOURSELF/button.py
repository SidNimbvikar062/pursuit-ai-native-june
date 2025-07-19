import pygame

# --- Colors ---
# Define BLACK here as it's used directly in the Button class for the border
BLACK = (0, 0, 0)

class Button:
    def __init__(self, x, y, width, height, text, font, color, text_color, action=None, disable_on_states=None, enabled_func=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.text_color = text_color
        self.action = action
        self.disable_on_states = disable_on_states if disable_on_states is not None else []
        self.enabled_func = enabled_func # Optional function to check if button should be enabled

    def is_enabled(self):
        # This method is simplified for standalone button.py.
        # The complex state-dependent logic related to current_game_state,
        # current_combat_sub_state, and displaying_stats from main.py
        # should primarily be handled in main.py before calling
        # button.draw() or button.handle_event().
        # However, the 'enabled_func' still allows external state checks
        # if the function passed captures those global states.
        if self.enabled_func:
            return self.enabled_func()
        return True


    def draw(self, surface):
        current_color = self.color
        current_text_color = self.text_color

        # Drawing the main rectangle
        pygame.draw.rect(surface, current_color, self.rect)
        # Drawing the border using the locally defined BLACK
        pygame.draw.rect(surface, BLACK, self.rect, 2)

        text_surface = self.font.render(self.text, True, current_text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        # The is_enabled() check should typically happen *before* calling handle_event
        # on a button from the main game loop, to prevent interaction with disabled buttons.
        # However, if enabled_func handles all disabling, then it can be checked here too.
        if not self.is_enabled(): # Re-adding this check for robustness, relies on enabled_func
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()
                return True
        return False