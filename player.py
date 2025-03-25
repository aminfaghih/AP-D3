import pygame
import random
import math
from game_objects import ShotMark, FreezeOpponentItem

class Player:
    """Represents a player in the game with aim, shooting, and scoring mechanics."""
    def __init__(self, user, controls, color, screen_width, screen_height):
        self.user = user
        self.name = user.username
        self.uuid = user.uuid
        self.score = 0
        self.aim_position = [random.randint(0, screen_width), random.randint(50, screen_height)]
        self.shot_marks = []
        self.controls = controls
        self.color = color
        self.start_time = None
        self.extra_time = 0
        self.time_left = 0
        self.bullets = 10
        self.last_shot_position = None
        self.last_shot_was_hit = False
        self.next_hit_multiplier = 1
        self.frozen = False
        self.freeze_timer = 0
        self.pause_offset = 0

    def start_timer(self):
        """Starts the player's timer."""
        self.start_time = pygame.time.get_ticks()

    def update_time(self):
        """Updates the remaining time,  for pauses."""
        if self.start_time is not None:
            elapsed = pygame.time.get_ticks() - self.start_time - self.pause_offset
            self.time_left = max(0, 60000 + self.extra_time - elapsed)

    def move_aim(self, keys, screen_width, screen_height):
        """Moves the player's aim, restricted below the thing"""
        if not self.frozen:
            speed = 3
            if keys[self.controls["up"]]:
                self.aim_position[1] -= speed
            if keys[self.controls["down"]]:
                self.aim_position[1] += speed
            if keys[self.controls["left"]]:
                self.aim_position[0] -= speed
            if keys[self.controls["right"]]:
                self.aim_position[0] += speed
            self.aim_position[0] = max(0, min(screen_width, self.aim_position[0]))
            self.aim_position[1] = max(50, min(screen_height, self.aim_position[1]))

    def shoot(self, game, shoot_sound, hit_sound):
        """Handles shooting logic with scoring based on distance from previous shot."""
        if self.bullets <= 0 or self.time_left <= 0 or self.aim_position[1] < 50:
            return
        self.bullets -= 1
        shoot_sound.play()
        shot_mark = ShotMark(self.aim_position[0], self.aim_position[1], self.color)
        self.shot_marks.append(shot_mark)
        hit_regular_target = False

        for target in game.targets[:]:
            if math.hypot(self.aim_position[0] - target.x, self.aim_position[1] - target.y) < 20:
                hit_sound.play()
                if hasattr(target, 'effect'):
                    target.effect(self, game) if isinstance(target, FreezeOpponentItem) else target.effect(self)
                    game.targets.remove(target)
                else:
                    hit_regular_target = True
                    if self.last_shot_position:
                        distance = math.sqrt(
                            (self.aim_position[0] - self.last_shot_position[0])**2 +
                            (self.aim_position[1] - self.last_shot_position[1])**2
                        )
                        base_points = min(10, max(1, int(distance / 20)))
                    else:
                        base_points = 5
                    self.score += base_points * self.next_hit_multiplier
                    self.next_hit_multiplier = 1
                    if self.last_shot_was_hit:
                        self.score += 2
                    game.targets.remove(target)
                    game.spawn_target()
                break
        self.last_shot_was_hit = hit_regular_target
        self.last_shot_position = self.aim_position.copy()

    def to_dict(self):
        """tabeghebandi the player state."""
        return {
            'uuid': self.uuid,
            'score': self.score,
            'aim_position': self.aim_position,
            'shot_marks': [mark.to_dict() for mark in self.shot_marks],
            'controls': self.controls,
            'color': self.color,
            'extra_time': self.extra_time,
            'time_left': self.time_left,
            'bullets': self.bullets,
            'last_shot_position': self.last_shot_position,
            'last_shot_was_hit': self.last_shot_was_hit,
            'next_hit_multiplier': self.next_hit_multiplier,
            'frozen': self.frozen,
            'freeze_timer': self.freeze_timer,
            'pause_offset': self.pause_offset
        }

    @classmethod
    def from_dict(cls, data, user, screen_width, screen_height):
        """Seperate ? a player from a dictionary."""
        player = cls(user, data['controls'], data['color'], screen_width, screen_height)
        player.score = data['score']
        player.aim_position = data['aim_position']
        player.shot_marks = [ShotMark.from_dict(mark) for mark in data['shot_marks']]
        player.extra_time = data['extra_time']
        player.time_left = data['time_left']
        player.bullets = data['bullets']
        player.last_shot_position = data['last_shot_position']
        player.last_shot_was_hit = data['last_shot_was_hit']
        player.next_hit_multiplier = data['next_hit_multiplier']
        player.frozen = data['frozen']
        player.freeze_timer = data['freeze_timer']
        player.pause_offset = data['pause_offset']
        if player.time_left > 0:
            elapsed = 60000 + player.extra_time - player.time_left
            player.start_time = pygame.time.get_ticks() - elapsed - player.pause_offset
        return player