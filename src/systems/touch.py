"""Сенсорное управление для телефона.

Левая половина экрана: палец ставит джойстик движения там, где коснулся.
Правая половина: второй джойстик, куда тянешь, туда герой целится и стреляет.
Кнопка «E» справа появляется рядом с NPC, кнопка «||» сверху справа ведёт в меню.
Касание во время диалога листает его, на финальном экране возвращает в меню.
Кнопки превращаются в обычные нажатия клавиш, поэтому сцены ничего о пальцах не знают."""
import math
import os
import sys

import pygame

from src import settings

STICK_RADIUS = 60           # насколько далеко тянуть палец до полной скорости
DEAD_ZONE = 10
AIM_MIN = 18                # меньше этого правый палец ещё не целится
AIM_DISTANCE = 200          # точка прицела перед героем
E_BUTTON = (860, 330, 44)   # x, y, радиус в координатах кадра 960x540
PAUSE_BUTTON = (924, 36, 24)
BACK_KEYS = (getattr(pygame, "K_AC_BACK", -1),)

INK = (28, 28, 46)
NOTE = (255, 214, 90)


ON_WEB = sys.platform == "emscripten"


def on_android():
    return hasattr(sys, "getandroidapilevel") or "ANDROID_ARGUMENT" in os.environ


def touch_screen_in_browser():
    """В браузере: палец вместо мыши (телефон или планшет). На ПК с мышью False."""
    if not ON_WEB:
        return False
    try:
        import platform as web
        return bool(web.window.matchMedia("(pointer: coarse)").matches)
    except Exception:
        return False


def portrait_in_browser():
    """Телефон в браузере держат вертикально: кадр 16:9 получается мелким."""
    if not ON_WEB:
        return False
    try:
        import platform as web
        return web.window.innerHeight > web.window.innerWidth
    except Exception:
        return False


def touch_device():
    return on_android() or touch_screen_in_browser()


def to_frame(x, y):
    """Координаты пальца 0..1 по окну -> пиксели кадра 960x540 с учётом чёрных полос по краям."""
    try:
        win_w, win_h = pygame.display.get_window_size()
    except (AttributeError, pygame.error):
        win_w, win_h = settings.SCREEN_W, settings.SCREEN_H
    scale = min(win_w / settings.SCREEN_W, win_h / settings.SCREEN_H)
    off_x = (win_w - settings.SCREEN_W * scale) / 2
    off_y = (win_h - settings.SCREEN_H * scale) / 2
    return (x * win_w - off_x) / scale, (y * win_h - off_y) / scale


def _inside(pos, button):
    bx, by, r = button
    return math.hypot(pos[0] - bx, pos[1] - by) <= r + 12


def _press(key):
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key, mod=0, unicode="", scancode=0))


class Touch:
    def __init__(self):
        self.active = touch_device()   # на ПК включится само, если коснуться сенсорного экрана
        self.fingers = {}       # id -> {"role": "move"|"aim"|"button", "start": (x, y), "pos": (x, y)}

    def _stick(self, role):
        for f in self.fingers.values():
            if f["role"] == role:
                dx, dy = f["pos"][0] - f["start"][0], f["pos"][1] - f["start"][1]
                return f["start"], dx, dy
        return None

    def handle(self, event, scene_name, scene):
        """True, если событие съедено пальцами и сцене его отдавать не надо."""
        if event.type == pygame.KEYDOWN and event.key in BACK_KEYS:
            _press(pygame.K_ESCAPE)
            return True
        if event.type not in (pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP):
            return False
        self.active = True
        pos = to_frame(event.x, event.y)
        fid = event.finger_id
        if event.type == pygame.FINGERDOWN:
            if scene_name == "end":
                _press(pygame.K_RETURN)
            elif scene_name == "game":
                if scene.dialogue is not None:
                    _press(pygame.K_e)
                elif _inside(pos, PAUSE_BUTTON):
                    _press(pygame.K_ESCAPE)
                elif _inside(pos, E_BUTTON) and scene.nearby_npc() is not None:
                    _press(pygame.K_e)
                else:
                    role = "move" if pos[0] < settings.SCREEN_W / 2 else "aim"
                    if self._stick(role) is None:
                        self.fingers[fid] = {"role": role, "start": pos, "pos": pos}
        elif event.type == pygame.FINGERMOTION and fid in self.fingers:
            self.fingers[fid]["pos"] = pos
        elif event.type == pygame.FINGERUP:
            self.fingers.pop(fid, None)
        return scene_name != "menu"   # меню само ловит касания как клики мыши

    def controls(self, player_center):
        """То же, что read_controls(): (движение, точка прицела, стрельба)."""
        move = (0.0, 0.0)
        stick = self._stick("move")
        if stick:
            _, dx, dy = stick
            dist = math.hypot(dx, dy)
            if dist > DEAD_ZONE:
                k = min(1.0, dist / STICK_RADIUS) / dist
                move = (dx * k, dy * k)
        aim, shooting = (player_center[0] + AIM_DISTANCE, player_center[1]), False
        stick = self._stick("aim")
        if stick:
            _, dx, dy = stick
            dist = math.hypot(dx, dy)
            if dist > AIM_MIN:
                aim = (player_center[0] + dx / dist * AIM_DISTANCE, player_center[1] + dy / dist * AIM_DISTANCE)
                shooting = True
        return move, aim, shooting

    def reset(self):
        self.fingers.clear()

    def draw(self, surface, scene_name, scene):
        if self.active and portrait_in_browser():
            from src.ui.text import draw_text
            shade = pygame.Surface((settings.SCREEN_W, settings.SCREEN_H), pygame.SRCALPHA)
            shade.fill((*INK, 210))
            surface.blit(shade, (0, 0))
            draw_text(surface, "Поверните телефон горизонтально", (settings.SCREEN_W // 2, settings.SCREEN_H // 2), 48,
                      NOTE, center=True)
            return
        if not self.active or scene_name != "game":
            return
        layer = pygame.Surface((settings.SCREEN_W, settings.SCREEN_H), pygame.SRCALPHA)
        for role in ("move", "aim"):
            stick = self._stick(role)
            if stick:
                (sx, sy), dx, dy = stick
                dist = math.hypot(dx, dy)
                if dist > STICK_RADIUS:
                    dx, dy = dx / dist * STICK_RADIUS, dy / dist * STICK_RADIUS
                pygame.draw.circle(layer, (255, 255, 255, 50), (int(sx), int(sy)), STICK_RADIUS)
                pygame.draw.circle(layer, (255, 255, 255, 110), (int(sx + dx), int(sy + dy)), 24)
        if scene.dialogue is None:
            px, py, pr = PAUSE_BUTTON
            pygame.draw.circle(layer, (*INK, 170), (px, py), pr)
            pygame.draw.rect(layer, (255, 255, 255, 220), (px - 8, py - 9, 5, 18))
            pygame.draw.rect(layer, (255, 255, 255, 220), (px + 3, py - 9, 5, 18))
        surface.blit(layer, (0, 0))
        if scene.dialogue is None and scene.nearby_npc() is not None:
            ex, ey, er = E_BUTTON
            pygame.draw.circle(surface, INK, (ex, ey), er + 3)
            pygame.draw.circle(surface, NOTE, (ex, ey), er)
            from src.ui.text import draw_text
            draw_text(surface, "E", (ex, ey), 40, INK, center=True)
