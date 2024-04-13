import pygame

from pygame.math import Vector2

from enums import Classes


class Player(pygame.sprite.Sprite):

    def __init__(self, centerpos: tuple[int, int], selected_unit: Classes, *groups):
        super().__init__(*groups)

        self.surf = pygame.Surface((25, 50))
        if selected_unit == Classes.WARRIOR:
            self.surf.fill((153, 76, 0))
        elif selected_unit == Classes.RANGER:
            self.surf.fill((76, 153, 0))
        elif selected_unit == Classes.MAGE:
            self.surf.fill((0, 255, 255))
        else:
            self.surf.fill((0, 0, 0))
        self.rect = self.surf.get_rect(center=centerpos)

    def update(self, screen_rect, all_enemies: pygame.sprite.Group):
        if all_enemies:
            p_pos = Vector2(self.rect.center)
            enemy = min([e for e in all_enemies], key=lambda e: p_pos.distance_to(Vector2(e.rect.center)))
            e_pos = Vector2(enemy.rect.center)
            dist = e_pos - p_pos
            if dist:
                vec = dist.normalize() * 5
                self.rect.move_ip(vec)
            pygame.sprite.spritecollide(self, all_enemies, True)
        self.rect.clamp_ip(screen_rect)

    def draw(self, screen):
        screen.blit(self.surf, self. rect)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, centerpos: tuple[int, int], *groups):
        super().__init__(*groups)

        self.surf = pygame.Surface((25, 50))
        self.surf.fill((255, 0, 0))
        self.rect = self.surf.get_rect(center=centerpos)

    def update(self, screen_rect, all_players):
        self.rect.clamp_ip(screen_rect)

    def draw(self, screen):
        screen.blit(self.surf, self.rect)


class TextArea(pygame.sprite.Sprite):
    # Besides value and font_size, takes a third parameter for its position, which must be keyworded.
    # Either specify "topleft" or "center", followed by the tuple position.
    # Examples: TextArea(font, "test value", group, topleft=(10, 10))
    #           TextArea(font, "new value", group, center=(20, 30))
    def __init__(self, font: pygame.font.Font, value: str, *groups, **pos):
        super().__init__(*groups)
        self.font = font
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
