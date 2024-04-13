import pygame
import enum

from pygame.font import Font
from pygame.math import Vector2


class Class(enum.Enum):
    WARRIOR = enum.auto()
    RANGER = enum.auto()
    MAGE = enum.auto()
    ENEMY = enum.auto()

    def create_new(self, centerpos: tuple[int, int], *groups):
        match self:
            case self.WARRIOR:
                return Warrior(centerpos, *groups)
            case self.RANGER:
                return Ranger(centerpos, *groups)
            case self.MAGE:
                return Mage(centerpos, *groups)
            case self.ENEMY:
                return Enemy(centerpos, *groups)


class Unit(pygame.sprite.Sprite):
    def __init__(self, centerpos: tuple[int, int], color: tuple[int, int, int], *groups):
        super().__init__(*groups)

        self.surf = pygame.Surface((25, 50))
        self.surf.fill(color)
        self.rect = self.surf.get_rect(center=centerpos)
        self.speed = 5

    def draw(self, screen):
        screen.blit(self.surf, self.rect)

    def move_nearest_ip(self, group: pygame.sprite.Group):
        if group:
            cur_pos = Vector2(self.rect.center)
            nearest = min([e for e in group], key=lambda e: cur_pos.distance_to(Vector2(e.rect.center)))
            nearest_pos = Vector2(nearest.rect.center)
            dist = nearest_pos - cur_pos
            if dist:
                vec = dist.normalize() * self.speed
                self.rect.move_ip(vec)


class Warrior(Unit):
    def __init__(self, centerpos: tuple[int, int], *groups):
        super().__init__(centerpos, (153, 76, 0), *groups)

    def update(self, screen_rect, all_enemies):
        self.move_nearest_ip(all_enemies)
        pygame.sprite.spritecollide(self, all_enemies, True)
        self.rect.clamp_ip(screen_rect)


class Ranger(Unit):
    def __init__(self, centerpos: tuple[int, int], *groups):
        super().__init__(centerpos, (76, 153, 0), *groups)

    def update(self, screen_rect, all_enemies):
        self.move_nearest_ip(all_enemies)
        pygame.sprite.spritecollide(self, all_enemies, True)
        self.rect.clamp_ip(screen_rect)


class Mage(Unit):
    def __init__(self, centerpos: tuple[int, int], *groups):
        super().__init__(centerpos, (0, 255, 255), *groups)

    def update(self, screen_rect, all_enemies):
        self.move_nearest_ip(all_enemies)
        pygame.sprite.spritecollide(self, all_enemies, True)
        self.rect.clamp_ip(screen_rect)


class Enemy(Unit):
    def __init__(self, centerpos: tuple[int, int], *groups):
        super().__init__(centerpos, (255, 0, 0), *groups)

    def update(self, screen_rect, all_players):
        self.rect.clamp_ip(screen_rect)


class TextArea(pygame.sprite.Sprite):
    # Besides font and value, takes a third parameter for its position, which must be keyworded.
    # Either specify "topleft" or "center", followed by the tuple position.
    # Examples: TextArea(font, "test value", group, topleft=(10, 10))
    #           TextArea(font, "new value", group, center=(20, 30))
    def __init__(self, font: pygame.font.Font, value: str, *groups, **pos):
        super().__init__(*groups)
        self.font = font
        self.text: pygame.Surface | None = None
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
    def __init__(self, font: pygame.font.Font, class_type: Class, *groups, **pos):
        super().__init__(
            font, f"{class_type.name.capitalize()} units: 0", *groups, **pos
        )
        self.class_type = class_type

    def update(self, gamestate):
        self.set_text(
            f"{self.class_type.name.capitalize()} units: {gamestate.playable_units[self.class_type]}"
        )
