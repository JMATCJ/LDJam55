import enum
import pygame
from pygame import image, Surface
from pygame.font import Font
from pygame.math import Vector2
from pygame.sprite import Group, Sprite
from pygame.transform import smoothscale

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
    def __init__(self, centerpos: tuple[int, int], image_folder_name: str, health: int, attack: int, speed: int, *groups):
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
        self.standing_surf = smoothscale(image.load(ASSETS_DIR / image_folder_name / "standing.png").convert_alpha(), (64, 64))
        self.attacking_surf = smoothscale(image.load(ASSETS_DIR / image_folder_name / "attacking.png").convert_alpha(), (64, 64))
        self.walking_1_surf = smoothscale(image.load(ASSETS_DIR / image_folder_name / "walking_1.png").convert_alpha(),(64, 64))
        self.walking_2_surf = smoothscale(image.load(ASSETS_DIR / image_folder_name / "walking_2.png").convert_alpha(), (64, 64))

        # The surface that should be currently drawn
        self.surf = self.standing_surf
        self.rect = self.surf.get_rect(center=centerpos)

    def update(self, screen_rect, group, delta_time):
        self.time_since_last_attack += delta_time
        self.animation_timer += delta_time
        if self.walking:
            if self.surf not in [self.walking_1_surf, self.walking_2_surf]:
                self.animation_timer = 0
                self.surf = self.walking_1_surf
            elif self.animation_timer >= 400:
                if self.surf == self.walking_1_surf:
                    self.surf = self.walking_2_surf
                else:
                    self.surf = self.walking_1_surf
                self.animation_timer = 0
        elif self.surf == self.attacking_surf:
            if self.animation_timer >= 150:
                self.surf = self.standing_surf
        else:
            self.surf = self.standing_surf

    def draw(self, screen):
        screen.blit(self.surf, self.rect)

    def move_nearest_ip(self, group: Group):
        if group and self.surf != self.attacking_surf:
            cur_pos = Vector2(self.rect.center)
            nearest = min([e for e in group], key=lambda e: cur_pos.distance_to(Vector2(e.rect.center)))
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
                self.surf = self.attacking_surf
                self.animation_timer = 0
                if attacked.health <= 0:
                    attacked.kill()
                self.time_since_last_attack = 0
                print(f"{type(self)} health: {self.health} | {type(attacked)} health: {attacked.health}")


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
    # Either specify "topleft" or "center", followed by the tuple position.
    # Examples: TextArea(font, "test value", group, topleft=(10, 10))
    #           TextArea(font, "new value", group, center=(20, 30))
    def __init__(self, font: Font, value: str, *groups, **pos):
        super().__init__(*groups)
        self.font = font
        self.text: Surface | None = None
        self.set_text(value)
        if "topleft" in pos:
            self.rect = self.text.get_rect(topleft=pos["topleft"])
        elif "center" in pos:
            self.rect = self.text.get_rect(center=pos["center"])
        else:
            self.rect = self.text.get_rect()

    def draw(self, screen):
        screen.blit(self.text, self.rect)

    def set_text(self, text: str):
        self.text = self.font.render(text, True, (0, 0, 0))


class PlayableUnitsText(TextArea):
    def __init__(self, font: Font, class_type: Class, *groups, **pos):
        super().__init__(
            font, f"{class_type.name.capitalize()} units: 0", *groups, **pos
        )
        self.class_type = class_type

    def update(self, gamestate):
        self.set_text(
            f"{self.class_type.name.capitalize()} units: {gamestate.playable_units[self.class_type]}"
        )


class TitleScreenArrow(Sprite):
    def __init__(self, arrow_type, class_type, *groups, **pos):
        super().__init__(*groups)
        self.arrow_type = arrow_type
        self.class_type = class_type
        self.surf = Surface((15, 15))
        self.surf.fill((0, 0, 0))
        if "topleft" in pos:
            self.rect = self.surf.get_rect(topleft=pos["topleft"])
        elif "center" in pos:
            self.rect = self.surf.get_rect(center=pos["center"])
        else:
            self.rect = self.surf.get_rect()

    def handle_click(self, game):
        if sum(game.playable_units.values()) + self.arrow_type > 5:
            return
        game.playable_units[self.class_type] += self.arrow_type
        if game.playable_units[self.class_type] < 0:
            game.playable_units[self.class_type] = 0

    def draw(self, screen):
        screen.blit(self.surf, self.rect)


class TitleScreenPlayableUnitsText(TextArea):
    def __init__(self, font: Font, class_type, *groups, **pos):
        super().__init__(font, "0", *groups, **pos)
        self.class_type = class_type

    def update(self, game):
        self.set_text(f"{game.playable_units[self.class_type]}")


class Button(Sprite):
    # Can't type the handle_click_func because of circular imports.
    # It should be a function that takes a gamestate, any returned values are ignored.
    def __init__(self, color: tuple[int, int, int], handle_click_func, *groups, **pos):
        super().__init__(*groups)

        self.surf = Surface((50, 25))
        self.surf.fill(color)
        self.rect = self.surf.get_rect(**pos)
        self.click_func = handle_click_func

    def handle_click(self, gamestate):
        self.click_func(gamestate)

    def draw(self, screen):
        screen.blit(self.surf, self.rect)

