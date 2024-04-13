import pygame

from pygame.locals import QUIT, MOUSEBUTTONDOWN

from consts import *
from sprites import Enemy, Player

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

all_enemies = pygame.sprite.Group()
all_players = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == MOUSE_LEFT_CLICK:
                Player(event.pos, all_players, all_sprites)
            elif event.button == MOUSE_RIGHT_CLICK:
                Enemy(event.pos, all_enemies, all_sprites)

    screen.fill((200, 200, 200))

    all_players.update(screen.get_rect(), all_enemies)
    all_enemies.update(screen.get_rect(), all_players)

    for sprite in all_sprites:
        sprite.draw(screen)

    pygame.display.update()
    clock.tick(60)

pygame.quit()
