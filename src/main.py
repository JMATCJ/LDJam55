import enum
import pygame
from pygame.locals import QUIT, KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP, K_1, K_2, K_3
import random

from consts import *
from sprites import (
    Skeleton,
    Zombie,
    TitleScreenArrow,
    TitleScreenPlayableUnitsText,
    TextArea,
    PlayableUnitsText,
    Class,
    Warrior,
    Ranger,
    Mage,
)


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
        self.playable_units = {Class.WARRIOR: 0, Class.RANGER: 0, Class.MAGE: 0}

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
            if random.random() < 0.5:
                Skeleton(
                    (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)),
                    self.all_enemies,
                    self.all_entities,
                )
            else:
                Zombie(
                    (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)),
                    self.all_enemies,
                    self.all_entities,
                )

    def spawn_playable_unit(self, pos):
        if self.playable_units[self.selected_unit] > 0:
            self.playable_units[self.selected_unit] -= 1
            self.selected_unit.create_new(pos, self.all_players, self.all_entities)

    def transition_state(self, new_state: States):
        self.screen_state = new_state
        self.build_screen()

    def build_screen(self):
        self.all_entities.empty()
        self.all_text.empty()
        if self.screen_state == GameState.States.TITLE_SCREEN:
            TextArea(
                self.font,
                "GAME TITLE HERE",
                self.all_text,
                center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 100),
            )

            TextArea(
                self.font,
                "Choose 5 units to start with below:",
                self.all_text,
                center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 70),
            )

            TextArea(
                self.font,
                "# Warriors:",
                self.all_text,
                topleft=(SCREEN_WIDTH / 2 - 200, SCREEN_HEIGHT / 2),
            )

            TitleScreenArrow(
                -1,
                Class.WARRIOR,
                self.all_text,
                center=(SCREEN_WIDTH / 2 - 40, SCREEN_HEIGHT / 2 + 11),
            )

            TitleScreenPlayableUnitsText(
                self.font,
                Class.WARRIOR,
                self.all_text,
                topleft=(SCREEN_WIDTH / 2 - 15, SCREEN_HEIGHT / 2),
            )

            TitleScreenArrow(
                1,
                Class.WARRIOR,
                self.all_text,
                center=(SCREEN_WIDTH / 2 + 20, SCREEN_HEIGHT / 2 + 11),
            )

            TextArea(
                self.font,
                "# Rangers:",
                self.all_text,
                topleft=(SCREEN_WIDTH / 2 - 200, SCREEN_HEIGHT / 2 + 50),
            )

            TitleScreenArrow(
                -1,
                Class.RANGER,
                self.all_text,
                center=(SCREEN_WIDTH / 2 - 40, SCREEN_HEIGHT / 2 + 61),
            )

            TitleScreenPlayableUnitsText(
                self.font,
                Class.RANGER,
                self.all_text,
                topleft=(SCREEN_WIDTH / 2 - 15, SCREEN_HEIGHT / 2 + 50),
            )

            TitleScreenArrow(
                1,
                Class.RANGER,
                self.all_text,
                center=(SCREEN_WIDTH / 2 + 20, SCREEN_HEIGHT / 2 + 61),
            )

            TextArea(
                self.font,
                "# Mages:",
                self.all_text,
                topleft=(SCREEN_WIDTH / 2 - 200, SCREEN_HEIGHT / 2 + 100),
            )

            TitleScreenArrow(
                -1,
                Class.MAGE,
                self.all_text,
                center=(SCREEN_WIDTH / 2 - 40, SCREEN_HEIGHT / 2 + 111),
            )

            TitleScreenPlayableUnitsText(
                self.font,
                Class.MAGE,
                self.all_text,
                topleft=(SCREEN_WIDTH / 2 - 15, SCREEN_HEIGHT / 2 + 100),
            )

            TitleScreenArrow(
                1,
                Class.MAGE,
                self.all_text,
                center=(SCREEN_WIDTH / 2 + 20, SCREEN_HEIGHT / 2 + 111),
            )

        if self.screen_state == GameState.States.GAME_SCREEN:
            PlayableUnitsText(self.font, Class.WARRIOR, self.all_text, topleft=(10, 10))
            PlayableUnitsText(self.font, Class.RANGER, self.all_text, topleft=(10, 30))
            PlayableUnitsText(self.font, Class.MAGE, self.all_text, topleft=(10, 50))

            self.generate_room()

    def update(self, screen, delta_time):
        if self.screen_state == GameState.States.GAME_SCREEN:
            self.all_players.update(screen.get_rect(), self.all_enemies, delta_time)
            self.all_enemies.update(screen.get_rect(), self.all_players, delta_time)

            if self.all_players.__len__() + sum(self.playable_units.values()) <= 0:
                # Game over
                self.screen_state = GameState.States.GAME_OVER
                print("Game Over")
            if self.all_enemies.__len__() <= 0:
                for entity in self.all_players.sprites():
                    if isinstance(entity, Warrior):
                        self.playable_units[Class.WARRIOR] += 1
                    if isinstance(entity, Ranger):
                        self.playable_units[Class.RANGER] += 1
                    if isinstance(entity, Mage):
                        self.playable_units[Class.MAGE] += 1
                    entity.kill()

        self.all_text.update(self)

    def draw(self, screen):
        for entity in self.all_entities:
            entity.draw(screen)

        for text in self.all_text:
            text.draw(screen)


pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

game = GameState(GameState.States.TITLE_SCREEN, False)

running = True
delta_time = 0
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            if game.screen_state == GameState.States.GAME_SCREEN:
                if event.button == MOUSE_LEFT_CLICK:
                    game.spawn_playable_unit(event.pos)
                elif event.button == MOUSE_RIGHT_CLICK:
                    game.generate_room()
        elif event.type == MOUSEBUTTONUP:
            if game.screen_state == GameState.States.TITLE_SCREEN:
                if event.button == MOUSE_LEFT_CLICK:
                    clicked_sprites = [
                        s for s in game.all_text if s.rect.collidepoint(event.pos)
                    ]
                    for sprite in clicked_sprites:
                        if hasattr(sprite, "handle_click"):
                            sprite.handle_click(game)

                    if sum(game.playable_units.values()) == 5:
                        game.transition_state(GameState.States.GAME_SCREEN)
        elif event.type == KEYDOWN:
            if event.key == K_1:
                game.selected_unit = Class.WARRIOR
            if event.key == K_2:
                game.selected_unit = Class.RANGER
            if event.key == K_3:
                game.selected_unit = Class.MAGE

    game.update(screen, delta_time)

    screen.fill((200, 200, 200))
    game.draw(screen)

    pygame.display.update()
    delta_time = clock.tick(60)

pygame.quit()
