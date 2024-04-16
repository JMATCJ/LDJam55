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
    TextArea,
    TimedTextArea,
    UpdatableTextArea,
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
        self.lower_bound = 1
        self.upper_bound = 1

        self.show_stats = False

        self.all_enemies = pygame.sprite.Group()
        self.all_players = pygame.sprite.Group()
        self.all_text = pygame.sprite.Group()
        self.all_entities = pygame.sprite.Group()
        self.stats_text = pygame.sprite.Group()
        self.all_notifications = pygame.sprite.Group()

        self.title_screen = pygame.image.load(ASSETS_DIR / "title_screen/title.png").convert()
        self.room_bg = pygame.image.load(ASSETS_DIR / "background.png").convert()
        self.game_over_bg = pygame.image.load(ASSETS_DIR / "game_over" / "background.png").convert()

        self.bg_surf = self.room_bg

        self.build_screen()

    def generate_room(self):
        for entity in self.all_enemies:
            entity.kill()

        if self.rooms_cleared == 1:
            self.upper_bound += 2

        if self.rooms_cleared % 5 == 0 and self.rooms_cleared != 0:
            self.lower_bound += 1
            self.upper_bound += 1

        for _ in range(random.randint(self.lower_bound, self.upper_bound)):
            random.choice([Skeleton, Zombie])((random.randint(0, SCREEN_WIDTH), random.randint(75, SCREEN_HEIGHT)), self.all_enemies, self.all_entities)
        if random.random() < CHEST_SPAWN_CHANCE:
            Chest(
                (random.randint(0, SCREEN_WIDTH), random.randint(75, SCREEN_HEIGHT)),
                self.all_enemies,
                self.all_entities,
            )

    def spawn_playable_unit(self, pos):
        if pos[1] >= 75 and not any(e.rect.collidepoint(pos) for e in self.all_enemies):
            if self.playable_units[self.selected_unit] > 0:
                self.playable_units[self.selected_unit] -= 1
                self.selected_unit(pos, self.all_players, self.all_entities)

    def transition_state(self, new_state: States):
        self.screen_state = new_state
        self.build_screen()

    def add_notification(self, text: str):
        centerpos = (SCREEN_WIDTH / 2, 45)
        for notif in self.all_notifications:
            if notif.rect.collidepoint(centerpos):
                centerpos = (SCREEN_WIDTH / 2, notif.rect.centery + notif.rect.h)
        TimedTextArea(
            self.font,
            text,
            BLACK,
            3000,
            self.all_notifications,
            self.all_text,
            center=centerpos
        )

    def build_screen(self):
        self.all_players.empty()
        self.all_enemies.empty()
        self.all_entities.empty()
        self.all_text.empty()
        self.stats_text.empty()
        self.all_notifications.empty()
        if self.screen_state == GameState.States.TITLE_SCREEN:
            self.bg_surf = self.title_screen

            TextArea(
                self.font,
                "[M] Mute music/sounds",
                BLACK,
                self.all_text,
                center=(SCREEN_WIDTH - 110, SCREEN_HEIGHT - 15),
            )

            TextArea(
                self.font,
                "Choose 5 units to start with below:",
                BLACK,
                self.all_text,
                center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50),
            )

            for i, class_type in enumerate([Warrior, Ranger, Mage]):
                class_text = TextArea(
                    self.font,
                    f"{class_type.__name__}s:",
                    BLACK,
                    self.all_text,
                    topright=(SCREEN_WIDTH / 2 - 50, (SCREEN_HEIGHT - 225) + (50 * i)),
                )
                class_left_arrow = TitleScreenArrow(
                    -1,
                    class_type,
                    self.all_text,
                    topleft=class_text.rect.move(10, 0).topright,
                )
                class_count_text = UpdatableTextArea(
                    self.font,
                    BLACK,
                    lambda c=class_type: f"{self.playable_units[c]}",
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
                center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 250)
            )

        elif self.screen_state == GameState.States.GAME_SCREEN:
            self.bg_surf = self.room_bg
            self.warrior_text = UpdatableTextArea(
                self.font, GREEN, lambda: f"[1] Warrior units: {self.playable_units[Warrior]}", self.all_text, topleft=(10, 10)
            )
            self.ranger_text = UpdatableTextArea(
                self.font, BLACK, lambda: f"[2] Ranger units: {self.playable_units[Ranger]}", self.all_text, topleft=(10, 30)
            )
            self.mage_text = UpdatableTextArea(
                self.font, BLACK, lambda: f"[3] Mage units: {self.playable_units[Mage]}", self.all_text, topleft=(10, 50)
            )

            TextArea(
                self.font,
                "[i] Stats page",
                BLACK,
                self.all_text,
                center=(SCREEN_WIDTH / 2, 20),
            )

            pos = 100
            for entity in [Warrior, Ranger, Mage, Skeleton, Zombie]:
                UpdatableTextArea(
                    self.font,
                    BLACK,
                    lambda e=entity: f"{e.__name__} health: {e.health}",
                    self.stats_text,
                    topleft=(10, pos)
                )
                pos += 20
                UpdatableTextArea(
                    self.font,
                    BLACK,
                    lambda e=entity: f"{e.__name__} attack: {e.attack}",
                    self.stats_text,
                    topleft=(10, pos),
                )
                pos += 20
                UpdatableTextArea(
                    self.font,
                    BLACK,
                    lambda e=entity: f"{e.__name__} speed: {e.speed}",
                    self.stats_text,
                    topleft=(10, pos),
                )
                pos += 20
                UpdatableTextArea(
                    self.font,
                    BLACK,
                    lambda e=entity: f"{e.__name__} attack speed: {e.attack_speed(e.attack_speed_scale) / 1000}s",
                    self.stats_text,
                    topleft=(10, pos),
                )
                pos += 20

            self.rooms_cleared = 0
            rooms_cleared = UpdatableTextArea(
                self.font,
                BLACK,
                lambda: f"Rooms cleared: {self.rooms_cleared}",
                self.all_text,
                topright=(SCREEN_WIDTH - 10, 10),
            )
            self.room_cleared_text = TimedTextArea(
                self.font, "Room Cleared!", BLACK, 1000, topleft=rooms_cleared.rect.move(0, 25).topleft
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
                    self.rooms_cleared += 1
                    self.room_transition_timer = 0
                    self.room_cleared_text.add(self.all_text)
                    if self.rooms_cleared % 3 == 0:
                        pygame.event.post(pygame.event.Event(SHOW_NOTIFICATION, text="Enemies are getting stronger..."))
                else:
                    self.room_transition_timer += delta_time
                    if self.room_transition_timer >= 1000:
                        self.room_transition_timer = None
                        for entity in self.all_players:
                            self.playable_units[type(entity)] += 1
                            entity.kill()
                        if self.rooms_cleared % 3 == 0:
                            for enemy_type in [Skeleton, Zombie]:
                                random_stat = random.randint(0, 3)
                                if random_stat == 0:
                                    enemy_type.health += 1
                                elif random_stat == 1:
                                    enemy_type.attack += 1
                                elif random_stat == 2:
                                    enemy_type.speed += 1
                                elif random_stat == 3:
                                    enemy_type.attack_speed_scale += 1
                        if self.rooms_cleared % 5 == 0:
                            new_unit = random.choice([Warrior, Ranger, Mage])
                            self.playable_units[new_unit] += 1
                            pygame.event.post(pygame.event.Event(SHOW_NOTIFICATION, text=f"A {new_unit.__name__} has joined your party"))
                        self.generate_room()

        self.all_text.update(self, delta_time)
        self.stats_text.update(self, delta_time)

    def draw(self, screen):
        screen.blit(self.bg_surf, self.bg_surf.get_rect())
        for entity in self.all_entities:
            entity.draw(screen)
        self.all_text.draw(screen)
        if self.show_stats:
            self.stats_text.draw(screen)

    def __title_screen_play_click(self):
        if sum(self.playable_units.values()) == 5:
            self.transition_state(GameState.States.GAME_SCREEN)

    def __game_over_play_click(self):
        for unit in [Warrior, Ranger, Mage, Skeleton, Zombie]:
            unit.reset_stats()

        self.selected_unit = Warrior
        self.transition_state(GameState.States.TITLE_SCREEN)


pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Storm the Castle")
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
                    game.warrior_text.set_color(GREEN)
                    game.ranger_text.set_color(BLACK)
                    game.mage_text.set_color(BLACK)
                elif event.key == K_2:
                    game.selected_unit = Ranger
                    game.warrior_text.set_color(BLACK)
                    game.ranger_text.set_color(GREEN)
                    game.mage_text.set_color(BLACK)
                elif event.key == K_3:
                    game.selected_unit = Mage
                    game.warrior_text.set_color(BLACK)
                    game.ranger_text.set_color(BLACK)
                    game.mage_text.set_color(GREEN)
                elif event.key == K_i:
                    game.show_stats = not game.show_stats
        elif event.type == SHOW_NOTIFICATION and game.screen_state == GameState.States.GAME_SCREEN:
            game.add_notification(event.text)

    game.update(screen, delta_time)
    game.draw(screen)

    pygame.display.update()
    delta_time = clock.tick(60)

pygame.quit()
