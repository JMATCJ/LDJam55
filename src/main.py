import pygame
import random

from pygame.locals import QUIT, KEYDOWN, MOUSEBUTTONDOWN, K_1, K_2, K_3

from consts import *
from sprites import Enemy, Player, TextArea
from enums import Classes


def generate_room(all_enemies, all_entities):
    for entity in all_entities:
        entity.kill()
    for _ in range(random.randint(1, 5)):
        Enemy(
            (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)),
            all_enemies,
            all_entities,
        )


pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
font = pygame.font.Font(pygame.font.get_default_font(), 24)
clock = pygame.time.Clock()

all_enemies = pygame.sprite.Group()
all_players = pygame.sprite.Group()
all_text = pygame.sprite.Group()
all_entities = pygame.sprite.Group()

player_units = {Classes.WARRIOR: 1, Classes.RANGER: 1, Classes.MAGE: 1}
selected_unit = Classes.WARRIOR

warrior_text = TextArea(
    font,
    f"Warrior units: {player_units[Classes.WARRIOR]}",
    all_text,
    topleft=(10, 10),
)

ranger_text = TextArea(
    font,
    f"Ranger units: {player_units[Classes.RANGER]}",
    all_text,
    topleft=(10, 30),
)

mage_text = TextArea(
    font, f"Mage units: {player_units[Classes.MAGE]}", all_text, topleft=(10, 50)
)


# Room init
generate_room(all_enemies, all_entities)

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == MOUSE_LEFT_CLICK:
                if player_units[selected_unit] > 0:
                    Player(event.pos, selected_unit, all_players, all_entities)
                    player_units[selected_unit] -= 1
                    if selected_unit == Classes.WARRIOR:
                        warrior_text.set_text(
                            f"Warrior units: {player_units[Classes.WARRIOR]}"
                        )
                    elif selected_unit == Classes.RANGER:
                        ranger_text.set_text(
                            f"Ranger units: {player_units[Classes.RANGER]}"
                        )
                    elif selected_unit == Classes.MAGE:
                        mage_text.set_text(f"Mage units: {player_units[Classes.MAGE]}")
            elif event.button == MOUSE_RIGHT_CLICK:
                generate_room(all_enemies, all_entities)
        elif event.type == KEYDOWN:
            if event.key == K_1:
                selected_unit = Classes.WARRIOR
            if event.key == K_2:
                selected_unit = Classes.RANGER
            if event.key == K_3:
                selected_unit = Classes.MAGE

    screen.fill((200, 200, 200))

    all_players.update(screen.get_rect(), all_enemies)
    all_enemies.update(screen.get_rect(), all_players)

    for sprite in all_entities:
        sprite.draw(screen)

    for text in all_text:
        text.draw(screen)

    pygame.display.update()
    clock.tick(60)

pygame.quit()
