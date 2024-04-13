from pathlib import Path
import sys

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
MOUSE_LEFT_CLICK = 1
MOUSE_RIGHT_CLICK = 3

# Check if we are in a pyinstaller "onefile" binary. Different path prefix in that case:
if getattr(sys, "frozen", False):
    ASSETS_DIR = Path(sys._MEIPASS) / "assets"
else:
    ASSETS_DIR = Path("assets")
