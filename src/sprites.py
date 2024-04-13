import pygame
import math

from pygame.math import Vector2

class Player(pygame.sprite.Sprite):
    def __init__(self, centerpos: tuple[int, int]):
        super().__init__()

        self.surf = pygame.Surface((25, 50))
        self.surf.fill((0, 255, 0))
        self.rect = self.surf.get_rect(center=centerpos)

    def update(self, all_enemies: pygame.sprite.Group):
        pos = Vector2(self.rect.center)

        if all_enemies:
            enemy, dist = min(
                [(e, pos.distance_to(Vector2(e.rect.center))) for e in all_enemies],
                key=lambda e: e[1],
            )

            angle = math.atan2(enemy.rect.center[1], enemy.rect.center[0])

            speed_x = 5 * math.cos(angle)
            speed_y = 5 * math.sin(angle)

            self.rect.move_ip(speed_x, speed_y)

    def draw(self, screen):
        screen.blit(self.surf, self. rect)


class Enemy(pygame.sprite.Sprite):

    def __init__(self, centerpos: tuple[int, int]):
        super().__init__()

        self.surf = pygame.Surface((25, 50))
        self.surf.fill((255, 0, 0))
        self.rect = self.surf.get_rect(center=centerpos)

    def update(self, all_players):
        pass

    def draw(self, screen):
        screen.blit(self.surf, self.rect)
