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
    Button,
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
        self.room_transition_timer = None

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
        if not any(e.rect.collidepoint(pos) for e in self.all_enemies):
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
                (0, 0, 0),
                self.all_text,
                center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 100),
            )

            TextArea(
                self.font,
                "Choose 5 units to start with below:",
                (0, 0, 0),
                self.all_text,
                center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 70),
            )

            TextArea(
                self.font,
                "# Warriors:",
                (0, 0, 0),
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
                (0, 0, 0),
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
                (0, 0, 0),
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
                (0, 0, 0),
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
                (0, 0, 0),
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
                (0, 0, 0),
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

            Button(
                (50, 25),
                (0, 127, 0),
                self.__title_screen_play_click,
                self.all_text,
                center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 150)
            )

        elif self.screen_state == GameState.States.GAME_SCREEN:
            self.warrior_text = PlayableUnitsText(
                self.font, (0, 200, 0), Class.WARRIOR, self.all_text, topleft=(10, 10)
            )
            self.ranger_text = PlayableUnitsText(
                self.font, (0, 0, 0), Class.RANGER, self.all_text, topleft=(10, 30)
            )
            self.mage_text = PlayableUnitsText(
                self.font, (0, 0, 0), Class.MAGE, self.all_text, topleft=(10, 50)
            )
            self.room_cleared_text = TextArea(
                self.font, "Room Cleared!", (0, 0, 0), center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            )

            self.generate_room()
        elif self.screen_state == GameState.States.GAME_OVER:
            TextArea(
                self.font,
                "GAME OVER LOSER + L + RATIO",
                (0, 0, 0),
                self.all_text,
                center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 100),
            )

            Button(
                (50, 25),
                (127, 0, 0),
                lambda: self.transition_state(GameState.States.TITLE_SCREEN),
                self.all_text,
                center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 150)
            )

    def update(self, screen, delta_time):
        if self.screen_state == GameState.States.GAME_SCREEN:
            self.all_players.update(screen.get_rect(), self.all_enemies, delta_time)
            self.all_enemies.update(screen.get_rect(), self.all_players, delta_time)

            if len(self.all_players) + sum(self.playable_units.values()) <= 0:
                # Game over
                self.transition_state(GameState.States.GAME_OVER)
            if not self.all_enemies:
                if self.room_transition_timer is None:
                    self.room_transition_timer = 0
                    self.all_text.add(self.room_cleared_text)
                else:
                    self.room_transition_timer += delta_time
                    if self.room_transition_timer >= 1000:
                        self.room_transition_timer = None
                        self.room_cleared_text.kill()
                        for entity in self.all_players.sprites():
                            if isinstance(entity, Warrior):
                                self.playable_units[Class.WARRIOR] += 1
                            elif isinstance(entity, Ranger):
                                self.playable_units[Class.RANGER] += 1
                            elif isinstance(entity, Mage):
                                self.playable_units[Class.MAGE] += 1
                            entity.kill()
                        self.generate_room()

        self.all_text.update(self)

    def draw(self, screen):
        self.all_entities.draw(screen)
        self.all_text.draw(screen)

    def __title_screen_play_click(self):
        if sum(self.playable_units.values()) == 5:
            self.transition_state(GameState.States.GAME_SCREEN)


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
            if game.screen_state == GameState.States.GAME_SCREEN and event.button == MOUSE_LEFT_CLICK:
                game.spawn_playable_unit(event.pos)
        elif event.type == MOUSEBUTTONUP:
            if event.button == MOUSE_LEFT_CLICK:
                clicked_sprites = [
                    s for s in game.all_text if s.rect.collidepoint(event.pos)
                ]
                for sprite in clicked_sprites:
                    if hasattr(sprite, "handle_click"):
                        sprite.handle_click(game)
        elif event.type == KEYDOWN:
            if game.screen_state == GameState.States.GAME_SCREEN:
                if event.key == K_1:
                    game.selected_unit = Class.WARRIOR
                    game.warrior_text.set_color((0, 200, 0))
                    game.ranger_text.set_color((0, 0, 0))
                    game.mage_text.set_color((0, 0, 0))
                elif event.key == K_2:
                    game.selected_unit = Class.RANGER
                    game.warrior_text.set_color((0, 0, 0))
                    game.ranger_text.set_color((0, 200, 0))
                    game.mage_text.set_color((0, 0, 0))
                elif event.key == K_3:
                    game.selected_unit = Class.MAGE
                    game.warrior_text.set_color((0, 0, 0))
                    game.ranger_text.set_color((0, 0, 0))
                    game.mage_text.set_color((0, 200, 0))

    game.update(screen, delta_time)

    screen.fill((200, 200, 200))
    game.draw(screen)

    pygame.display.update()
    delta_time = clock.tick(60)

pygame.quit()
