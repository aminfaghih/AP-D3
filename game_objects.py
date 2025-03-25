import pygame
import random
import math

class GameObject:
    """Base class for all game objects with position attributes."""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, screen):
        """Abstract method to draw the object on the screen."""
        pass

    def to_dict(self):
        """Serializes the object to a dictionary."""
        return {'x': self.x, 'y': self.y}

    @classmethod
    def from_dict(cls, data, screen_width, screen_height):
        """Deserializes the object from a dictionary."""
        return cls(data['x'], data['y'])

class ShotMark(GameObject):
    """Represents a mark left by a player's shot."""
    def __init__(self, x, y, color):
        super().__init__(x, y)
        self.color = color

    def draw(self, screen):
        """Draws a small circle representing the shot mark."""
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 5)

    def to_dict(self):
        """Serializes the shot mark."""
        return {'x': self.x, 'y': self.y, 'color': self.color}

    @classmethod
    def from_dict(cls, data):
        """Deserializes the shot mark."""
        return cls(data['x'], data['y'], data['color'])

class Target(GameObject):
    """A basic target that players can shoot for points."""
    def __init__(self, screen_width, screen_height, x=None, y=None):
        super().__init__(
            x if x is not None else random.randint(20, screen_width - 20),
            y if y is not None else random.randint(70, screen_height - 20)
        )
        self.image = pygame.transform.scale(
            pygame.image.load('target.png').convert_alpha(), (40, 40)
        )
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def draw(self, screen):
        """Draws the target image on the screen."""
        screen.blit(self.image, self.rect)

    def to_dict(self):
        """Serializes the target."""
        return {'type': 'Target', 'x': self.x, 'y': self.y}

    @classmethod
    def from_dict(cls, data, screen_width, screen_height):
        """Deserializes the target."""
        return cls(screen_width, screen_height, data['x'], data['y'])

class TimeBonusItem(Target):
    """A special target that adds time when hit."""
    def __init__(self, screen_width, screen_height, x=None, y=None):
        super().__init__(screen_width, screen_height, x, y)
        self.image = pygame.transform.scale(
            pygame.image.load('time_bonus.png').convert_alpha(), (40, 40)
        )
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def effect(self, player):
        """Adds 10 seconds to the player's extra_time."""
        player.extra_time += 10000

    def to_dict(self):
        """Serializes the time bonus item."""
        return {'type': 'TimeBonusItem', 'x': self.x, 'y': self.y}

    @classmethod
    def from_dict(cls, data, screen_width, screen_height):
        """Deserializes the time bonus item."""
        return cls(screen_width, screen_height, data['x'], data['y'])

class ScoreMultiplierItem(Target):
    """A special target that doubles the score of the next hit."""
    def __init__(self, screen_width, screen_height, x=None, y=None):
        super().__init__(screen_width, screen_height, x, y)
        self.image = pygame.transform.scale(
            pygame.image.load('score_multiplier.png').convert_alpha(), (40, 40)
        )
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def effect(self, player):
        """Sets the player's next hit multiplier to 2."""
        player.next_hit_multiplier = 2

    def to_dict(self):
        """Serializes the score multiplier item."""
        return {'type': 'ScoreMultiplierItem', 'x': self.x, 'y': self.y}

    @classmethod
    def from_dict(cls, data, screen_width, screen_height):
        """Deserializes the score multiplier item."""
        return cls(screen_width, screen_height, data['x'], data['y'])

class FreezeOpponentItem(Target):
    """A special target that freezes the opponent for 5 seconds."""
    def __init__(self, screen_width, screen_height, x=None, y=None):
        super().__init__(screen_width, screen_height, x, y)
        self.image = pygame.transform.scale(
            pygame.image.load('freeze_opponent.png').convert_alpha(), (40, 40)
        )
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def effect(self, player, game):
        """Freezes the opponent player for 5 seconds."""
        opponent = game.player2 if player == game.player1 else game.player1
        opponent.frozen = True
        opponent.freeze_timer = 5000

    def to_dict(self):
        """Serializes the freeze opponent item."""
        return {'type': 'FreezeOpponentItem', 'x': self.x, 'y': self.y}

    @classmethod
    def from_dict(cls, data, screen_width, screen_height):
        """Deserializes the freeze opponent item."""
        return cls(screen_width, screen_height, data['x'], data['y'])

class ExtraBulletsItem(Target):
    """A special target that grants extra bullets."""
    def __init__(self, screen_width, screen_height, x=None, y=None):
        super().__init__(screen_width, screen_height, x, y)
        self.image = pygame.transform.scale(
            pygame.image.load('extra_bullets.png').convert_alpha(), (40, 40)
        )
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def effect(self, player):
        """Adds 5 bullets to the player's ammo."""
        player.bullets += 5

    def to_dict(self):
        """Serializes the extra bullets item."""
        return {'type': 'ExtraBulletsItem', 'x': self.x, 'y': self.y}

    @classmethod
    def from_dict(cls, data, screen_width, screen_height):
        """Deserializes the extra bullets item."""
        return cls(screen_width, screen_height, data['x'], data['y'])