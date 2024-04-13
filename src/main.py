import pygame

from pygame.locals import QUIT

from sprites import Enemy

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

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

    screen.fill((200, 200, 200))

    for sprite in all_sprites:
        sprite.update()
        sprite.draw(screen)

    pygame.display.update()
    clock.tick(60)

pygame.quit()
