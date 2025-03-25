import pygame
import random
from game_objects import Target, TimeBonusItem, ScoreMultiplierItem, FreezeOpponentItem, ExtraBulletsItem
from player import Player

def draw_text(screen, text, pos, font, color=(0, 0, 0)):
    """Utility function to render text on the screen."""
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, pos)

class Game:
    """Manages the game state, including players, targets, and game loop logic."""
    def __init__(self, player1: Player, player2: Player, screen_width, screen_height):
        self.player1 = player1
        self.player2 = player2
        self.targets = [Target(screen_width, screen_height) for _ in range(3)]
        self.running = True
        self.special_item_timer = 10000  # 10 seconds in milliseconds
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.hud_height = 50  # Height of the HUD area
        self.is_new = True  # Flag to distinguish new vs. loaded games

    def spawn_target(self):
        """Spawns a new regular target."""
        self.targets.append(Target(self.screen_width, self.screen_height))

    def update(self, dt):
        """Updates game state based on elapsed time (dt in milliseconds)."""
        for player in [self.player1, self.player2]:
            player.update_time()
            if player.frozen:
                player.freeze_timer -= dt
                if player.freeze_timer <= 0:
                    player.frozen = False
        # End game if both players are out of bullets or time
        if (self.player1.bullets <= 0 or self.player1.time_left <= 0) and \
           (self.player2.bullets <= 0 or self.player2.time_left <= 0):
            self.running = False
        # Spawn special items periodically
        self.special_item_timer -= dt
        if self.special_item_timer <= 0:
            special_items = [t for t in self.targets if not isinstance(t, Target)]
            if len(special_items) < 2:
                item_type = random.choice([
                    TimeBonusItem, ScoreMultiplierItem, FreezeOpponentItem, ExtraBulletsItem
                ])
                self.targets.append(item_type(self.screen_width, self.screen_height))
            self.special_item_timer = 10000

    def draw(self, screen, background_image, font):
        """Renders all game elements on the screen with a HUD at the top."""
        pygame.draw.rect(screen, (50, 50, 50), (0, 0, self.screen_width, self.hud_height))
        player1_time = max(0, self.player1.time_left // 1000)
        player2_time = max(0, self.player2.time_left // 1000)
        p1_text = f"{self.player1.name}: {self.player1.score} Bullets: {self.player1.bullets} Time: {player1_time}"
        draw_text(screen, p1_text, (10, 10), font, self.player1.color)
        p2_text = f"{self.player2.name}: {self.player2.score} Bullets: {self.player2.bullets} Time: {player2_time}"
        p2_surface = font.render(p2_text, True, self.player2.color)
        screen.blit(p2_surface, (self.screen_width - p2_surface.get_width() - 10, 10))
        screen.blit(background_image, (0, self.hud_height))
        for target in self.targets:
            target.draw(screen)
        for player in [self.player1, self.player2]:
            for shot_mark in player.shot_marks:
                shot_mark.draw(screen)

    def to_dict(self):
        """Serializes the game state to a dictionary for saving."""
        return {
            'player1': self.player1.to_dict(),
            'player2': self.player2.to_dict(),
            'targets': [t.to_dict() for t in self.targets],
            'special_item_timer': self.special_item_timer,
            'running': self.running,
            'is_new': self.is_new
        }

    @classmethod
    def from_dict(cls, data, player1_user, player2_user, screen_width, screen_height):
        """Deserializes a game state from a dictionary."""
        player1 = Player.from_dict(data['player1'], player1_user, screen_width, screen_height)
        player2 = Player.from_dict(data['player2'], player2_user, screen_width, screen_height)
        game = cls(player1, player2, screen_width, screen_height)
        game.targets = []
        for t_data in data['targets']:
            if t_data['type'] == 'Target':
                game.targets.append(Target.from_dict(t_data, screen_width, screen_height))
            elif t_data['type'] == 'TimeBonusItem':
                game.targets.append(TimeBonusItem.from_dict(t_data, screen_width, screen_height))
            elif t_data['type'] == 'ScoreMultiplierItem':
                game.targets.append(ScoreMultiplierItem.from_dict(t_data, screen_width, screen_height))
            elif t_data['type'] == 'FreezeOpponentItem':
                game.targets.append(FreezeOpponentItem.from_dict(t_data, screen_width, screen_height))
            elif t_data['type'] == 'ExtraBulletsItem':
                game.targets.append(ExtraBulletsItem.from_dict(t_data, screen_width, screen_height))
        game.special_item_timer = data['special_item_timer']
        game.running = data['running']
        game.is_new = data.get('is_new', False)  # Default to False for loaded games
        return game