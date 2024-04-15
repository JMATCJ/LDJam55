import random
import pygame
from pygame import image, Surface, Rect
from pygame.font import Font
from pygame.math import Vector2
from pygame.sprite import Group, Sprite
from pygame.transform import smoothscale, flip
from typing import Any, Callable

from consts import *


def attack_2_to_1(scale: int) -> int:
    return 1000 // scale + 1000


def attack_3_to_2(scale: int) -> int:
    return 1000 // scale + 2000


class Unit(Sprite):
    image_folder_name = None
    health = 0
    attack = 0
    speed = 0
    attack_speed = None
    attack_speed_scale = 1
    attack_distance = 0
    aoe_attack = 0
    health_bar_bg = None
    health_bar_fg_green = None
    health_bar_fg_red = None
    is_enemy = False

    def __init__(
        self,
        centerpos: tuple[int, int],
        *groups,
    ):
        super().__init__(*groups)

        # Stats
        self.health = type(self).health
        self.time_since_last_attack = 0

        # For animations
        self.walking = False
        self.animation_timer = 0

        # Surfaces
        self.standing_surf = smoothscale(
            image.load(ASSETS_DIR / type(self).image_folder_name / "standing.png").convert_alpha(),
            (64, 64),
        )
        self.attacking_surf = smoothscale(
            image.load(
                ASSETS_DIR / type(self).image_folder_name / "attacking.png"
            ).convert_alpha(),
            (64, 64),
        )
        self.walking_1_surf = smoothscale(
            image.load(
                ASSETS_DIR / type(self).image_folder_name / "walking_1.png"
            ).convert_alpha(),
            (64, 64),
        )
        self.walking_2_surf = smoothscale(
            image.load(
                ASSETS_DIR / type(self).image_folder_name / "walking_2.png"
            ).convert_alpha(),
            (64, 64),
        )

        if Unit.health_bar_bg is None:
            Unit.health_bar_bg = smoothscale(image.load(ASSETS_DIR / "health_bar" / "background.png").convert(), (64, 6))
            Unit.health_bar_fg_green = smoothscale(image.load(ASSETS_DIR / "health_bar" / "green.png").convert(), (64, 6))
            Unit.health_bar_fg_red = smoothscale(image.load(ASSETS_DIR / "health_bar" / "red.png").convert(), (64, 6))

        # The surface that should be currently drawn
        self.image = self.standing_surf
        self.rect = self.image.get_rect(center=centerpos)
        self.health_bar_surf = Unit.health_bar_fg_red if type(self).is_enemy else Unit.health_bar_fg_green
        self.health_bar_rect = self.health_bar_bg.get_rect(topleft=self.rect.move(0, -10).topleft)

    def __repr__(self):
        attack_speed = type(self).attack_speed(self.attack_speed_scale)
        return f"{self.__class__.__name__}(pos={self.rect.center}, {self.health=}, {self.attack=}, {self.speed=}, self.attack_speed={attack_speed})"

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
        self.health_bar_rect = self.health_bar_bg.get_rect(topleft=self.rect.move(0, -10).topleft)
        self.do_attack(group)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        screen.blit(self.health_bar_bg, self.health_bar_rect)
        screen.blit(self.health_bar_surf, self.health_bar_rect, self.health_bar_surf.get_rect(w=self.health_bar_surf.get_width() * (self.health / type(self).health)))


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
        if self.time_since_last_attack >= type(self).attack_speed(self.attack_speed_scale):
            attacked = pygame.sprite.spritecollide(self, group, False, self.__collided)
            if attacked:
                self.image = self.attacking_surf
                self.animation_timer = 0
                for entity in attacked:
                    entity.health -= self.attack
                    if entity.health <= 0:
                        entity.kill()
                    print(
                        f"{type(self).__name__} health: {self.health} | {type(entity).__name__} health: {entity.health}"
                    )
                    if not self.aoe_attack:
                        break
                self.time_since_last_attack = 0


class Warrior(Unit):
    image_folder_name = "knight"
    health = 5
    attack = 2
    speed = 5
    attack_speed = attack_2_to_1

    def __init__(self, centerpos: tuple[int, int], *groups):
        super().__init__(centerpos, *groups)

    @classmethod
    def reset_stats(cls):
        cls.health = 5
        cls.attack = 2
        cls.speed = 5
        cls.attack_speed_scale = 1


class Ranger(Unit):
    image_folder_name = "ranger"
    health = 3
    attack = 3
    speed = 6
    attack_speed = attack_2_to_1
    attack_distance = 200

    def __init__(self, centerpos: tuple[int, int], *groups):
        super().__init__(centerpos, *groups)

    @classmethod
    def reset_stats(cls):
        cls.health = 3
        cls.attack = 3
        cls.speed = 6
        cls.attack_speed_scale = 1


class Mage(Unit):
    image_folder_name = "mage"
    health = 1
    attack = 5
    speed = 4
    attack_speed = attack_3_to_2
    attack_distance = 300
    aoe_attack = True

    def __init__(self, centerpos: tuple[int, int], *groups):
        super().__init__(centerpos, *groups)

    @classmethod
    def reset_stats(cls):
        cls.health = 1
        cls.attack = 5
        cls.speed = 4
        cls.attack_speed_scale = 1


class Skeleton(Unit):
    image_folder_name = "skeleton"
    health = 3
    attack = 1
    speed = 3
    attack_speed = attack_2_to_1
    is_enemy = True

    def __init__(self, centerpos: tuple[int, int], *groups):
        super().__init__(centerpos, *groups)

    @classmethod
    def reset_stats(cls):
        cls.health = 3
        cls.attack = 1
        cls.speed = 3
        cls.attack_speed_scale = 1


class Zombie(Unit):
    image_folder_name = "zombie"
    health = 2
    attack = 2
    speed = 2
    attack_speed = attack_2_to_1
    is_enemy = True

    def __init__(self, centerpos: tuple[int, int], *groups):
        super().__init__(centerpos,  *groups)

    @classmethod
    def reset_stats(cls):
        cls.health = 2
        cls.attack = 2
        cls.speed = 2
        cls.attack_speed_scale = 1


class Chest(Sprite):
    health = 10

    def __init__(self, centerpos, *groups):
        super().__init__(*groups)
        self.health = 10
        self.image = smoothscale(image.load(ASSETS_DIR / "chest.png").convert_alpha(), (64, 44))
        self.rect = self.image.get_rect(center=centerpos)

        if Unit.health_bar_bg is None:
            Unit.health_bar_bg = smoothscale(image.load(ASSETS_DIR / "health_bar" / "background.png").convert(), (64, 6))
            Unit.health_bar_fg_green = smoothscale(image.load(ASSETS_DIR / "health_bar" / "green.png").convert(), (64, 6))
            Unit.health_bar_fg_red = smoothscale(image.load(ASSETS_DIR / "health_bar" / "red.png").convert(), (64, 6))

        self.health_bar_surf = Unit.health_bar_fg_red
        self.health_bar_rect = Unit.health_bar_bg.get_rect(topleft=self.rect.move(0, -10).topleft)

        self.random_class = random.choice([Warrior, Ranger, Mage])
        self.random_stat = random.randint(0, 3)

    def update(self, screen_rect, group, delta_time):
        self.rect.clamp_ip(screen_rect)
        self.health_bar_rect.clamp_ip(screen_rect)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        screen.blit(Unit.health_bar_bg, self.health_bar_rect)
        screen.blit(self.health_bar_surf, self.health_bar_rect, self.health_bar_surf.get_rect(
            w=self.health_bar_surf.get_width() * (self.health / type(self).health)))

    def kill(self):
        if self.random_stat == 0:
            self.random_class.health += 1
        elif self.random_stat == 1:
            self.random_class.attack += 1
        elif self.random_stat == 2:
            self.random_class.speed += 1
        elif self.random_stat == 3:
            self.random_class.attack_speed_scale += 1
        pygame.event.post(pygame.event.Event(SHOW_NOTIFICATION, text=f"Upgraded {self.random_class.__name__}'s {NUMBER_TO_STAT_NAME[self.random_stat]}"))
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
        self.rect: Rect | None = None
        self.pos = pos
        self.set_text(value)

    def set_text(self, text: str, color: tuple[int, int, int] | None = None):
        if color is not None:
            self.color = color
        self.image = self.font.render(text, True, self.color)
        self.rect = self.image.get_rect(**self.pos)

    def set_color(self, color):
        self.color = color


class TimedTextArea(TextArea):
    def __init__(
            self,
            font: Font,
            value: str,
            color,
            timeout: int,
            *groups,
            **pos,
    ):
        super().__init__(font, value, color, *groups, **pos)
        self.timeout = timeout
        self.timer = 0

    def update(self, game, delta_time):
        self.timer += delta_time
        if self.timer >= self.timeout:
            self.kill()

    def set_text(self, text: str, color: tuple[int, int, int] | None = None):
        self.timer = 0
        super().set_text(text, color)

    def add(self, *groups):
        self.timer = 0
        super().add(*groups)


class UpdatableTextArea(TextArea):
    def __init__(
            self,
            font: Font,
            color,
            text_callback,
            *groups,
            **pos,
    ):
        super().__init__(font, text_callback(), color, *groups, **pos)
        self.text_callback = text_callback

    def update(self, game, delta_time):
        self.set_text(self.text_callback())


class TitleScreenArrow(Sprite):
    def __init__(self, arrow_type, class_type, *groups, **pos):
        super().__init__(*groups)
        self.arrow_type = arrow_type
        self.class_type = class_type
        self.image = smoothscale(image.load(ASSETS_DIR / "title_screen" / "arrow.png").convert_alpha(), (51, 20))
        if arrow_type == -1:
            self.image = flip(self.image, True, False)
        self.rect = self.image.get_rect(**pos)

    def handle_click(self, game):
        if sum(game.playable_units.values()) + self.arrow_type > 5:
            return
        game.playable_units[self.class_type] += self.arrow_type
        if game.playable_units[self.class_type] < 0:
            game.playable_units[self.class_type] = 0


class Button(Sprite):
    def __init__(self, button_size: tuple[int, int], image_path: Path, handle_click_func: Callable[[], Any], *groups, **pos):
        super().__init__(*groups)

        self.image = smoothscale(image.load(image_path).convert_alpha(), button_size)
        self.rect = self.image.get_rect(**pos)
        self.click_func = handle_click_func

    def handle_click(self, _):
        self.click_func()
