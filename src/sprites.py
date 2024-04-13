import pygame


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.surf = pygame.Surface((25, 50))
        self.surf.fill((255, 0, 0))
        self.rect = self.surf.get_rect()

    def update(self):
        self.rect.move_ip(5, 0)

    def draw(self, screen):
        screen.blit(self.surf, self.rect)