import pygame

from pygame.locals import QUIT, MOUSEBUTTONDOWN

from consts import *
from sprites import Enemy, Player

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

enemy = Enemy()

all_sprites = pygame.sprite.Group()
all_sprites.add(enemy)

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN and event.button == MOUSE_LEFT_CLICK:
            player = Player(event.pos)
            all_sprites.add(player)

    screen.fill((200, 200, 200))

    for sprite in all_sprites:
        sprite.update()

        # if pygame.sprite.collide_rect(enemy):
        #     enemy.rect.move_ip(-250, 0)
        #     player.rect.move_ip(250, 0)

        sprite.draw(screen)

    pygame.display.update()
    clock.tick(60)

pygame.quit()
