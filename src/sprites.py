import pygame

from pygame.math import Vector2


class Player(pygame.sprite.Sprite):
    def __init__(self, centerpos: tuple[int, int], *groups):
        super().__init__(*groups)

        self.surf = pygame.Surface((25, 50))
        self.surf.fill((0, 255, 0))
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
