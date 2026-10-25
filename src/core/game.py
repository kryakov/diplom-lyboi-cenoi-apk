import os
import sys

# Без сглаживания при растягивании кадра: пиксель-арт остаётся чётким. Ставится до импорта pygame.
os.environ.setdefault("SDL_RENDER_SCALE_QUALITY", "nearest")

import pygame

from src import settings
from src.core.scene_manager import SceneManager
from src.scenes.menu_scene import MenuScene
from src.scenes.game_scene import GameScene
from src.scenes.end_scene import EndScene
from src.systems.touch import Touch


def make_dpi_aware():
    """Windows с масштабом экрана 125 % или 150 % сам растягивает окно и размывает его.
    Если сказать системе, что игра сама следит за масштабом, она получает настоящие пиксели экрана."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except (AttributeError, OSError):
            ctypes.windll.user32.SetProcessDPIAware()
    except (AttributeError, OSError):
        pass


def open_window(fullscreen):
    """Игра рисует кадр 960x540, а pygame (SCALED) растягивает его на весь экран с сохранением пропорций:
    на Full HD ровно в 2 раза (1920x1080), на других экранах пропорционально, без сглаживания.
    F11 переключает окно и полный экран."""
    size = (settings.SCREEN_W, settings.SCREEN_H)
    flags = pygame.SCALED | (pygame.FULLSCREEN if fullscreen else 0)
    try:
        return pygame.display.set_mode(size, flags)
    except pygame.error:
        return pygame.display.set_mode(size)


class Game:
    def __init__(self):
        make_dpi_aware()
        pygame.init()
        self.screen = open_window(getattr(settings, "FULLSCREEN", True))
        pygame.display.set_caption(settings.TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.touch = Touch()
        self.scenes = SceneManager(self)
        self.scenes.register("menu", MenuScene(self))
        self.scenes.register("game", GameScene(self))
        self.scenes.register("end", EndScene(self))

    def quit(self):
        self.running = False

    def toggle_fullscreen(self):
        try:
            pygame.display.toggle_fullscreen()
        except pygame.error:
            pass

    def scene_name(self):
        for name, scene in self.scenes._scenes.items():
            if scene is self.scenes.current:
                return name
        return None

    def step(self, dt):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif self.touch.handle(event, self.scene_name(), self.scenes.current):
                pass
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                self.toggle_fullscreen()
            elif self.scenes.current:
                self.scenes.current.handle_event(event)
        if self.scenes.current:
            self.scenes.current.update(dt)
            self.screen.fill((20, 20, 30))
            self.scenes.current.draw(self.screen)
            self.touch.draw(self.screen, self.scene_name(), self.scenes.current)
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(settings.FPS) / 1000.0
            self.step(dt)
        pygame.quit()
