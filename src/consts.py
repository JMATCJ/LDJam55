from pathlib import Path
from pygame.event import custom_type
import sys

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
MOUSE_LEFT_CLICK = 1
MOUSE_RIGHT_CLICK = 3
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
CHEST_SPAWN_CHANCE = 0.05
SHOW_NOTIFICATION = custom_type()


NUMBER_TO_STAT_NAME = ["Health", "Attack", "Speed", "Attack Speed"]

# Check if we are in a pyinstaller "onefile" binary. Different path prefix in that case:
if getattr(sys, "frozen", False):
    ASSETS_DIR = Path(sys._MEIPASS) / "assets"
else:
    ASSETS_DIR = Path("assets")
