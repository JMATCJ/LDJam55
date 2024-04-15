import enum
import pygame
from pygame.locals import (
    QUIT,
    KEYDOWN,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
    K_1,
    K_2,
    K_3,
    K_i,
)
import random

from consts import *
from sprites import (
    Skeleton,
    Zombie,
    TitleScreenArrow,
    TitleScreenPlayableUnitsText,
    GameScreenRoomsClearedText,
    GameScreenStatsText,
    TextArea,
    PlayableUnitsText,
    Warrior,
    Ranger,
    Mage,
    Chest,
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
        self.font = pygame.font.Font(ASSETS_DIR / "font" / "morris-roman.black.ttf", 24)

        self.selected_unit = Warrior
        self.playable_units = {Warrior: 0, Ranger: 0, Mage: 0}
        self.room_transition_timer = None

        self.rooms_cleared = 0

        self.show_stats = False

        self.all_enemies = pygame.sprite.Group()
        self.all_players = pygame.sprite.Group()
        self.all_text = pygame.sprite.Group()
        self.all_entities = pygame.sprite.Group()

        self.stats_text = pygame.sprite.Group()

        self.room_bg = pygame.image.load(ASSETS_DIR / "background.png").convert()
        self.game_over_bg = pygame.image.load(ASSETS_DIR / "game_over" / "background.png").convert()

        self.bg_surf = self.room_bg

        self.build_screen()

    def generate_room(self):
        for entity in self.all_enemies:
            entity.kill()
        for _ in range(random.randint(1, 5)):
            random.choice([Skeleton, Zombie])((random.randint(0, SCREEN_WIDTH), random.randint(75, SCREEN_HEIGHT)), self.all_enemies, self.all_entities)
        if random.random() < 0.05:
            Chest(
                (random.randint(0, SCREEN_WIDTH), random.randint(75, SCREEN_HEIGHT)),
                self.all_enemies,
                self.all_entities,
            )

    def spawn_playable_unit(self, pos):
        if pos[1] >= 75 and not any(e.rect.collidepoint(pos) for e in self.all_enemies):
            if self.playable_units[self.selected_unit] > 0:
                self.playable_units[self.selected_unit] -= 1
                spawned_unit = self.selected_unit(
                    pos, self.all_players, self.all_entities
                )
                print(spawned_unit)

    def transition_state(self, new_state: States):
        self.screen_state = new_state
        self.build_screen()

    def build_screen(self):
        self.all_players.empty()
        self.all_enemies.empty()
        self.all_entities.empty()
        self.all_text.empty()
        self.stats_text.empty()
        if self.screen_state == GameState.States.TITLE_SCREEN:
            self.bg_surf = self.room_bg
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

            for i, class_type in enumerate([Warrior, Ranger, Mage]):
                class_text = TextArea(
                    self.font,
                    f"{class_type.__name__}s:",
                    (0, 0, 0),
                    self.all_text,
                    topright=(SCREEN_WIDTH / 2 - 50, SCREEN_HEIGHT / 2 + (50 * i)),
                )
                class_left_arrow = TitleScreenArrow(
                    -1,
                    class_type,
                    self.all_text,
                    topleft=class_text.rect.move(10, 0).topright,
                )
                class_count_text = TitleScreenPlayableUnitsText(
                    self.font,
                    (0, 0, 0),
                    class_type,
                    self.all_text,
                    topleft=class_left_arrow.rect.move(10, 0).topright,
                )
                TitleScreenArrow(
                    1,
                    class_type,
                    self.all_text,
                    topleft=class_count_text.rect.move(10, 0).topright,
                )

            Button(
                (160, 80),
                ASSETS_DIR / "title_screen" / "play_button.png",
                self.__title_screen_play_click,
                self.all_text,
                center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 200)
            )

        elif self.screen_state == GameState.States.GAME_SCREEN:
            self.bg_surf = self.room_bg
            self.warrior_text = PlayableUnitsText(
                self.font, (0, 200, 0), Warrior, 1, self.all_text, topleft=(10, 10)
            )
            self.ranger_text = PlayableUnitsText(
                self.font, (0, 0, 0), Ranger, 2, self.all_text, topleft=(10, 30)
            )
            self.mage_text = PlayableUnitsText(
                self.font, (0, 0, 0), Mage, 3, self.all_text, topleft=(10, 50)
            )

            pos = 100
            for entity in [Warrior, Ranger, Mage, Skeleton, Zombie]:
                GameScreenStatsText(
                    self.font,
                    (0, 0, 0),
                    entity,
                    "health",
                    lambda e: e.health,
                    self.stats_text,
                    topleft=(10, pos),
                )
                pos += 20
                GameScreenStatsText(
                    self.font,
                    (0, 0, 0),
                    entity,
                    "attack",
                    lambda e: e.attack,
                    self.stats_text,
                    topleft=(10, pos),
                )
                pos += 20
                GameScreenStatsText(
                    self.font,
                    (0, 0, 0),
                    entity,
                    "speed",
                    lambda e: e.speed,
                    self.stats_text,
                    topleft=(10, pos),
                )
                pos += 20
                if entity == Mage:
                    GameScreenStatsText(
                        self.font,
                        (0, 0, 0),
                        entity,
                        "attack speed",
                        lambda e: ((2000 // e.attack_speed_scale) + 1000) / 1000,
                        self.stats_text,
                        topleft=(10, pos),
                    )
                else:
                    GameScreenStatsText(
                        self.font,
                        (0, 0, 0),
                        entity,
                        "attack speed",
                        lambda e: ((1000 // e.attack_speed_scale) + 1000) / 1000,
                        self.stats_text,
                        topleft=(10, pos),
                    )
                pos += 20

            self.rooms_cleared = 0
            rooms_cleared = GameScreenRoomsClearedText(
                self.font,
                (0, 0, 0),
                self.all_text,
                topright=(SCREEN_WIDTH - 10, 10),
            )
            self.room_cleared_text = TextArea(
                self.font, "Room Cleared!", (0, 0, 0), topleft=rooms_cleared.rect.move(0, 25).topleft
            )

            self.generate_room()
        elif self.screen_state == GameState.States.GAME_OVER:
            self.bg_surf = self.game_over_bg

            Button(
                (427, 108),
                ASSETS_DIR / "game_over" / "play_again.png",
                self.__game_over_play_click,
                self.all_text,
                center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 230)
            )

    def update(self, screen, delta_time):
        if self.screen_state == GameState.States.GAME_SCREEN:
            self.all_players.update(screen.get_rect(), self.all_enemies, delta_time)
            self.all_enemies.update(screen.get_rect(), self.all_players, delta_time)

            if len(self.all_players) + sum(self.playable_units.values()) <= 0:
                # Game over
                self.transition_state(GameState.States.GAME_OVER)
            elif not self.all_enemies:
                if self.room_transition_timer is None:
                    self.room_transition_timer = 0
                    self.rooms_cleared += 1
                    self.all_text.add(self.room_cleared_text)
                else:
                    self.room_transition_timer += delta_time
                    if self.room_transition_timer >= 1000:
                        self.room_transition_timer = None
                        self.room_cleared_text.kill()
                        for entity in self.all_players:
                            self.playable_units[type(entity)] += 1
                            entity.kill()
                        if self.rooms_cleared % 3 == 0:
                            Skeleton.health += 1
                            random_stat = random.randint(1, 3)
                            if random_stat == 1:
                                Skeleton.attack += 1
                            elif random_stat == 2:
                                Skeleton.speed += 1
                            elif random_stat == 3:
                                Skeleton.attack_speed_scale += 1
                            Zombie.health += 1
                            random_stat = random.randint(1, 3)
                            if random_stat == 1:
                                Zombie.attack += 1
                            elif random_stat == 2:
                                Zombie.speed += 1
                            elif random_stat == 3:
                                Zombie.attack_speed_scale += 1
                        if self.rooms_cleared % 5 == 0:
                            self.playable_units[random.choice([Warrior, Ranger, Mage])] += 1
                        self.generate_room()

        self.all_text.update(self)
        self.stats_text.update(self)

    def draw(self, screen):
        screen.blit(self.bg_surf, self.bg_surf.get_rect())
        self.all_entities.draw(screen)
        self.all_text.draw(screen)
        if self.show_stats:
            self.stats_text.draw(screen)

    def __title_screen_play_click(self):
        if sum(self.playable_units.values()) == 5:
            self.transition_state(GameState.States.GAME_SCREEN)

    def __game_over_play_click(self):
        Skeleton.reset_stats()
        Zombie.reset_stats()
        self.selected_unit = Warrior
        self.transition_state(GameState.States.TITLE_SCREEN)


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
                    game.selected_unit = Warrior
                    game.warrior_text.set_color((0, 200, 0))
                    game.ranger_text.set_color((0, 0, 0))
                    game.mage_text.set_color((0, 0, 0))
                elif event.key == K_2:
                    game.selected_unit = Ranger
                    game.warrior_text.set_color((0, 0, 0))
                    game.ranger_text.set_color((0, 200, 0))
                    game.mage_text.set_color((0, 0, 0))
                elif event.key == K_3:
                    game.selected_unit = Mage
                    game.warrior_text.set_color((0, 0, 0))
                    game.ranger_text.set_color((0, 0, 0))
                    game.mage_text.set_color((0, 200, 0))
                elif event.key == K_i:
                    game.show_stats = not game.show_stats

    game.update(screen, delta_time)
    game.draw(screen)

    pygame.display.update()
    delta_time = clock.tick(60)

pygame.quit()
