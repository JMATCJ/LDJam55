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
        elif event.type == MOUSEBUTTONDOWN and event.button == MOUSE_LEFT_CLICK:
            player = Player(event.pos)
            all_players.add(player)
            all_sprites.add(player)
        elif event.type == MOUSEBUTTONDOWN and event.button == MOUSE_RIGHT_CLICK:
            enemy = Enemy(event.pos)
            all_enemies.add(enemy)
            all_sprites.add(enemy)

    screen.fill((200, 200, 200))

    for player in all_players:
        player.update(all_enemies)
        player.draw(screen)

    for enemy in all_enemies:
        enemy.update(all_players)
        enemy.draw(screen)

    pygame.display.update()
    clock.tick(60)

pygame.quit()
