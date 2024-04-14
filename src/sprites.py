import enum
import pygame
from pygame import image, Surface
from pygame.font import Font
from pygame.math import Vector2
from pygame.sprite import Group, Sprite
from pygame.transform import smoothscale
from typing import Any, Callable

from consts import *


class Class(enum.Enum):
    WARRIOR = enum.auto()
    RANGER = enum.auto()
    MAGE = enum.auto()
    SKELETON = enum.auto()
    ZOMBIE = enum.auto()

    def create_new(self, centerpos: tuple[int, int], *groups):
        match self:
            case self.WARRIOR:
                return Warrior(centerpos, *groups)
            case self.RANGER:
                return Ranger(centerpos, *groups)
            case self.MAGE:
                return Mage(centerpos, *groups)
            case self.SKELETON:
                return Skeleton(centerpos, *groups)
            case self.ZOMBIE:
                return Zombie(centerpos, *groups)


class Unit(Sprite):
    def __init__(
        self,
        centerpos: tuple[int, int],
        image_folder_name: str,
        health: int,
        attack: int,
        speed: int,
        *groups,
    ):
        super().__init__(*groups)

        # Stats
        self.health = health
        self.attack = attack
        self.speed = speed
        self.time_since_last_attack = 0

        # For animations
        self.walking = False
        self.animation_timer = 0

        # Surfaces
        self.standing_surf = smoothscale(
            image.load(ASSETS_DIR / image_folder_name / "standing.png").convert_alpha(),
            (64, 64),
        )
        self.attacking_surf = smoothscale(
            image.load(
                ASSETS_DIR / image_folder_name / "attacking.png"
            ).convert_alpha(),
            (64, 64),
        )
        self.walking_1_surf = smoothscale(
            image.load(
                ASSETS_DIR / image_folder_name / "walking_1.png"
            ).convert_alpha(),
            (64, 64),
        )
        self.walking_2_surf = smoothscale(
            image.load(
                ASSETS_DIR / image_folder_name / "walking_2.png"
            ).convert_alpha(),
            (64, 64),
        )

        # The surface that should be currently drawn
        self.image = self.standing_surf
        self.rect = self.image.get_rect(center=centerpos)

    def update(self, screen_rect, group, delta_time):
        self.time_since_last_attack += delta_time
        self.animation_timer += delta_time
        if self.walking:
            if self.image not in [self.walking_1_surf, self.walking_2_surf]:
                self.animation_timer = 0
                self.image = self.walking_1_surf
            elif self.animation_timer >= 400:
                if self.image == self.walking_1_surf:
                    self.image = self.walking_2_surf
                else:
                    self.image = self.walking_1_surf
                self.animation_timer = 0
        elif self.image == self.attacking_surf:
            if self.animation_timer >= 150:
                self.image = self.standing_surf
        else:
            self.image = self.standing_surf

    def move_nearest_ip(self, group: Group):
        if group and self.image != self.attacking_surf:
            cur_pos = Vector2(self.rect.center)
            nearest = min(
                [e for e in group],
                key=lambda e: cur_pos.distance_to(Vector2(e.rect.center)),
            )
            nearest_pos = Vector2(nearest.rect.center)
            dist = nearest_pos - cur_pos
            if dist:
                vec = dist.normalize() * self.speed
                if not pygame.sprite.spritecollideany(self, group):
                    self.rect.move_ip(vec)
                    self.walking = True
                    return
        self.walking = False

    def attack_one(self, group: Group):
        if self.time_since_last_attack >= 2000:
            attacked: Unit = pygame.sprite.spritecollideany(self, group)
            if attacked:
                attacked.health -= self.attack
                self.image = self.attacking_surf
                self.animation_timer = 0
                if attacked.health <= 0:
                    attacked.kill()
                self.time_since_last_attack = 0
                print(
                    f"{type(self)} health: {self.health} | {type(attacked)} health: {attacked.health}"
                )


class Warrior(Unit):
    def __init__(self, centerpos: tuple[int, int], *groups):
        super().__init__(centerpos, "knight", 5, 2, 5, *groups)

    def update(self, screen_rect, all_enemies, delta_time):
        super().update(screen_rect, all_enemies, delta_time)
        self.move_nearest_ip(all_enemies)
        self.rect.clamp_ip(screen_rect)
        self.attack_one(all_enemies)


class Ranger(Unit):
    def __init__(self, centerpos: tuple[int, int], *groups):
        super().__init__(centerpos, "ranger", 3, 3, 6, *groups)

    def update(self, screen_rect, all_enemies, delta_time):
        super().update(screen_rect, all_enemies, delta_time)
        self.move_nearest_ip(all_enemies)
        self.rect.clamp_ip(screen_rect)
        self.attack_one(all_enemies)


class Mage(Unit):
    def __init__(self, centerpos: tuple[int, int], *groups):
        super().__init__(centerpos, "mage", 1, 5, 4, *groups)

    def update(self, screen_rect, all_enemies, delta_time):
        super().update(screen_rect, all_enemies, delta_time)
        self.move_nearest_ip(all_enemies)
        self.rect.clamp_ip(screen_rect)
        self.attack_one(all_enemies)


class Skeleton(Unit):
    def __init__(self, centerpos: tuple[int, int], *groups):
        super().__init__(centerpos, "skeleton", 3, 1, 3, *groups)

    def update(self, screen_rect, all_players, delta_time):
        super().update(screen_rect, all_players, delta_time)
        self.rect.clamp_ip(screen_rect)
        self.attack_one(all_players)


class Zombie(Unit):
    def __init__(self, centerpos: tuple[int, int], *groups):
        super().__init__(centerpos, "zombie", 2, 2, 1, *groups)

    def update(self, screen_rect, all_players, delta_time):
        super().update(screen_rect, all_players, delta_time)
        self.rect.clamp_ip(screen_rect)
        self.attack_one(all_players)


class TextArea(Sprite):
    # Besides font and value, takes a third parameter for its position, which must be keyworded.
    # This can use all the same arguments as get_rect() for positioning Rects (topleft, center, etc)
    # Examples: TextArea(font, "test value", group, topleft=(10, 10))
    #           TextArea(font, "new value", group, center=(20, 30))
    def __init__(
        self,
        font: Font,
        value: str,
        color,
        *groups,
        **pos,
    ):
        super().__init__(*groups)
        self.font = font
        self.color = color
        self.image: Surface | None = None
        self.set_text(value)
        self.rect = self.image.get_rect(**pos)

    def set_text(self, text: str):
        self.image = self.font.render(text, True, self.color)

    def set_color(self, color):
        self.color = color


class PlayableUnitsText(TextArea):

    def __init__(
        self,
        font: Font,
        color,
        class_type: Class,
        *groups,
        **pos,
    ):
        super().__init__(
            font, f"{class_type.name.capitalize()} units: 0", color, *groups, **pos
        )
        self.class_type = class_type

    def update(self, gamestate):
        self.set_text(
            f"{self.class_type.name.capitalize()} units: {gamestate.playable_units[self.class_type]}"
        )
        self.set_color(self.color)


class TitleScreenArrow(Sprite):
    def __init__(self, arrow_type, class_type, *groups, **pos):
        super().__init__(*groups)
        self.arrow_type = arrow_type
        self.class_type = class_type
        self.image = Surface((15, 15))
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect(**pos)

    def handle_click(self, game):
        if sum(game.playable_units.values()) + self.arrow_type > 5:
            return
        game.playable_units[self.class_type] += self.arrow_type
        if game.playable_units[self.class_type] < 0:
            game.playable_units[self.class_type] = 0


class TitleScreenPlayableUnitsText(TextArea):

    def __init__(self, font: Font, color, class_type, *groups, **pos):
        super().__init__(font, "0", color, *groups, **pos)
        self.class_type = class_type

    def update(self, game):
        self.set_text(f"{game.playable_units[self.class_type]}")


class Button(Sprite):
    def __init__(self, button_size: tuple[int, int], color: tuple[int, int, int], handle_click_func: Callable[[], Any], *groups, **pos):
        super().__init__(*groups)

        self.image = Surface(button_size)
        self.image.fill(color)
        self.rect = self.image.get_rect(**pos)
        self.click_func = handle_click_func

    def handle_click(self, _):
        self.click_func()
