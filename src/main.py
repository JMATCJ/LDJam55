import pygame
import random
import enum

from pygame.locals import QUIT, KEYDOWN, MOUSEBUTTONDOWN, K_1, K_2, K_3

from consts import *
from sprites import Enemy, PlayableUnitsText, Class


class GameState:
    class States(enum.Enum):
        TITLE_SCREEN = enum.auto()
        GAME_SCREEN = enum.auto()
        GAME_OVER = enum.auto()

    def __init__(self, state: States, muted: bool):
        # Set initial values for game states
        self.screen_state = state
        self.font = pygame.font.Font(pygame.font.get_default_font(), 24)

        self.selected_unit = Class.WARRIOR
        self.playable_units = {Class.WARRIOR: 2, Class.RANGER: 2, Class.MAGE: 2}

        self.all_enemies = pygame.sprite.Group()
        self.all_players = pygame.sprite.Group()
        self.all_text = pygame.sprite.Group()
        self.all_entities = pygame.sprite.Group()

        self.build_screen()

    # TODO: Can get rid of if only used in build_screen()
    def generate_room(self):
        for entity in self.all_entities:
            entity.kill()
        for _ in range(random.randint(1, 5)):
            Enemy(
                (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)),
                self.all_enemies,
                self.all_entities,
            )

    def spawn_playable_unit(self, pos):
        if self.playable_units[self.selected_unit] > 0:
            self.playable_units[self.selected_unit] -= 1
            self.selected_unit.create_new(pos, self.all_players, self.all_entities)

    def build_screen(self):
        if self.screen_state == GameState.States.GAME_SCREEN:
            PlayableUnitsText(self.font, Class.WARRIOR, self.all_text, topleft=(10, 10))
            PlayableUnitsText(self.font, Class.RANGER, self.all_text, topleft=(10, 30))
            PlayableUnitsText(self.font, Class.MAGE, self.all_text, topleft=(10, 50))

            self.generate_room()

    def update(self, screen):
        if self.screen_state == GameState.States.GAME_SCREEN:
            self.all_players.update(screen.get_rect(), self.all_enemies)
            self.all_enemies.update(screen.get_rect(), self.all_players)
            self.all_text.update(self)

    def draw(self, screen):
        for entity in self.all_entities:
            entity.draw(screen)

        for text in self.all_text:
            text.draw(screen)


pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

game = GameState(GameState.States.GAME_SCREEN, False)

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == MOUSE_LEFT_CLICK:
                game.spawn_playable_unit(event.pos)
            elif event.button == MOUSE_RIGHT_CLICK:
                game.generate_room()
        elif event.type == KEYDOWN:
            if event.key == K_1:
                game.selected_unit = Class.WARRIOR
            if event.key == K_2:
                game.selected_unit = Class.RANGER
            if event.key == K_3:
                game.selected_unit = Class.MAGE

    screen.fill((200, 200, 200))

    game.update(screen)
    game.draw(screen)

    pygame.display.update()
    clock.tick(60)

pygame.quit()
