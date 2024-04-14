import enum
import random
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
        attack_speed: int,
        attack_distance: int,
        aoe_attack: bool,
        *groups,
    ):
        super().__init__(*groups)

        # Stats
        self.health = health
        self.attack = attack
        self.speed = speed
        self.attack_speed = attack_speed
        self.attack_distance = attack_distance
        self.aoe_attack = aoe_attack
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

    def __repr__(self):
        return f"{self.__class__.__name__}(pos={self.rect.center}, {self.health=}, {self.attack=}, {self.speed=}, {self.attack_speed=})"

    def __set_surf(self):
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

    def update(self, screen_rect, group, delta_time):
        self.time_since_last_attack += delta_time
        self.animation_timer += delta_time
        self.__set_surf()
        self.move_nearest_ip(group)
        self.rect.clamp_ip(screen_rect)
        self.do_attack(group)

    @staticmethod
    def __collided(me: 'Unit', other: 'Unit') -> bool:
        is_colliding = me.rect.colliderect(other.rect)
        me_pos = Vector2(me.rect.center)
        other_pos = Vector2(other.rect.center)
        return is_colliding or me_pos.distance_to(other_pos) < me.attack_distance

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
                if not pygame.sprite.spritecollideany(self, group, self.__collided):
                    self.rect.move_ip(vec)
                    self.walking = True
                    return
        self.walking = False

    def do_attack(self, group: Group):
        if self.time_since_last_attack >= self.attack_speed:
            attacked = pygame.sprite.spritecollide(self, group, False, self.__collided)
            if attacked:
                self.image = self.attacking_surf
                self.animation_timer = 0
                for entity in attacked:
                    entity.health -= self.attack
                    if entity.health <= 0:
                        entity.kill()
                    print(
                        f"{type(self)} health: {self.health} | {type(entity)} health: {entity.health}"
                    )
                    if not self.aoe_attack:
                        break
                self.time_since_last_attack = 0


class Warrior(Unit):
    health = 5
    attack = 2
    speed = 5
    attack_speed_scale = 1

    def __init__(self, centerpos: tuple[int, int], *groups):
        super().__init__(
            centerpos,
            "knight",
            Warrior.health,
            Warrior.attack,
            Warrior.speed,
            (1000 // Warrior.attack_speed_scale) + 1000,
            0,
            False,
            *groups,
        )


class Ranger(Unit):
    health = 3
    attack = 3
    speed = 6
    attack_speed_scale = 1

    def __init__(self, centerpos: tuple[int, int], *groups):
        super().__init__(
            centerpos,
            "ranger",
            Ranger.health,
            Ranger.attack,
            Ranger.speed,
            (1000 // Ranger.attack_speed_scale) + 1000,
            200,
            False,
            *groups,
        )


class Mage(Unit):
    health = 1
    attack = 5
    speed = 4
    attack_speed_scale = 1

    def __init__(self, centerpos: tuple[int, int], *groups):
        super().__init__(
            centerpos,
            "mage",
            Mage.health,
            Mage.attack,
            Mage.speed,
            (1000 // Mage.attack_speed_scale) + 2000,
            300,
            True,
            *groups,
        )


class Skeleton(Unit):
    health = 3
    attack = 1
    speed = 3
    attack_speed_scale = 1

    def __init__(self, centerpos: tuple[int, int], *groups):
        super().__init__(centerpos, "skeleton", Skeleton.health, Skeleton.attack, Skeleton.speed, (1000//Skeleton.attack_speed_scale) + 1000, 0, False, *groups)

    @classmethod
    def reset_stats(cls):
        cls.health = 3
        cls.attack = 1
        cls.speed = 3
        cls.attack_speed_scale = 1


class Zombie(Unit):
    health = 2
    attack = 2
    speed = 2
    attack_speed_scale = 1

    def __init__(self, centerpos: tuple[int, int], *groups):
        super().__init__(centerpos, "zombie", Zombie.health, Zombie.attack, Zombie.speed, (1000//Zombie.attack_speed_scale) + 1000, 0, False, *groups)

    @classmethod
    def reset_stats(cls):
        cls.health = 2
        cls.attack = 2
        cls.speed = 2
        cls.attack_speed_scale = 1


class Chest(Sprite):
    def __init__(self, centerpos, *groups):
        super().__init__(*groups)
        self.health = 10
        self.image = pygame.Surface((50, 50))
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect(center=centerpos)

    def update(self, screen_rect, group, delta_time):
        self.rect.clamp_ip(screen_rect)

    def kill(self):
        random_class = random.choice([Warrior, Ranger, Mage])
        random_stat = random.randint(1, 4)
        if random_stat == 1:
            random_class.attack += 1
        elif random_stat == 2:
            random_class.speed += 1
        elif random_stat == 3:
            random_class.attack_speed_scale += 1
        elif random_stat == 4:
            random_class.health += 1
        print(f"CHEST GAVE: {random_class} - {random_stat}")
        super().kill()


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


class GameScreenRoomsClearedText(TextArea):
    def __init__(self, font: Font, color, *groups, **pos):
        super().__init__(font, f"Rooms cleared: XX", color, *groups, **pos)

    def update(self, game):
        self.set_text(f"Rooms cleared: {game.rooms_cleared}")


class Button(Sprite):
    def __init__(self, button_size: tuple[int, int], color: tuple[int, int, int], handle_click_func: Callable[[], Any], *groups, **pos):
        super().__init__(*groups)

        self.image = Surface(button_size)
        self.image.fill(color)
        self.rect = self.image.get_rect(**pos)
        self.click_func = handle_click_func

    def handle_click(self, _):
        self.click_func()
