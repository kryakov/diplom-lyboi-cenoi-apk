import pygame
from src import settings
from src.core.scene_manager import Scene
from src.core.state import GameState
from src.entities.player import Player
from src.systems.ai import alive_count, spawn_all, update_all
from src.systems.audio import play_music, play_sound, stop_music
from src.systems.combat import CombatSystem, read_controls
from src.systems.level_loader import load_levels, load_room
from src.systems.room_view import draw_room, npc_top_left
from src.ui.dialogue_box import draw_dialogue
from src.ui.hud import Hud
from src.ui.text import draw_text

try:
    from src.systems.dialogue import DialogueSession, apply_result, load_dialogue, nearby_npc
except ImportError:
    # пока dialogue.py не лежит в src/systems, игра идёт без диалогов
    DialogueSession = None

TALK_RADIUS = 80
ADVANCE_KEYS = (pygame.K_e, pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)
EVENT_SOUNDS = (("enemy_killed", "kill"), ("player_hit", "hit"), ("player_dead", "death"))


class GameScene(Scene):
    def on_enter(self, **kwargs):
        levels, _ = load_levels()
        self.state = GameState(levels)
        self.player = Player((0, 0))
        self.combat = CombatSystem()
        self.hud = Hud()
        self.debug = False
        self.dialogue = None
        self.used_dialogues = set()
        self.seen_dialogues = set()
        self.reload_room()
        self.start_dialogue("intro")
        play_music("game")

    def reload_room(self):
        self.room = load_room(self.state.current_room_id)
        self.player.teleport(self.room.player_spawn)
        self.combat.clear()
        self.enemies = spawn_all(self.room)
        if self.room.type == "boss":
            self.start_dialogue(f"{self.room.id}_intro")

    def start_dialogue(self, dialogue_id, once=True):
        """once=True: показать один раз за игру (вступление, речь босса). NPC можно слушать снова."""
        if DialogueSession is None or (once and dialogue_id in self.seen_dialogues):
            return
        try:
            self.dialogue = DialogueSession(load_dialogue(dialogue_id))
        except (OSError, ValueError, KeyError):
            self.dialogue = None
            return
        if once:
            self.seen_dialogues.add(dialogue_id)

    def nearby_npc(self):
        if DialogueSession is None:
            return None
        return nearby_npc(self.room.npcs, self.player.center, TALK_RADIUS)

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if self.dialogue is not None:
            if event.key in ADVANCE_KEYS and self.dialogue.advance():
                if apply_result(self.dialogue, self.state, self.used_dialogues).get("heal"):
                    self.player.on_heal()
                self.dialogue = None
            elif event.key == pygame.K_ESCAPE:
                self.dialogue = None
            return
        if event.key == pygame.K_ESCAPE:
            stop_music()
            self.game.scenes.change("menu")
        elif event.key == pygame.K_F1:
            self.debug = not self.debug
        elif event.key == pygame.K_e:
            npc = self.nearby_npc()
            if npc is not None:
                self.start_dialogue(npc[2], once=False)

    def update(self, dt):
        self.hud.update(dt, self.state.health)
        if self.dialogue is not None:
            return

        touch = self.game.touch
        move, aim, shooting = touch.controls(self.player.center) if touch.active else read_controls()
        shots = self.player.update(dt, self.room, move, aim, shooting)
        if shots:
            play_sound("shoot")
        self.combat.add(shots)
        update_all(dt, self.room, self.enemies, self.player.center)
        events = self.combat.update(dt, self.room, self.player, self.enemies, self.state)
        for name, sound in EVENT_SOUNDS:
            if name in events:
                play_sound(sound)

        self.room.set_enemies_alive(alive_count(self.enemies))
        if self.state.health < self.state.max_health:
            for kind, amount in self.room.collect_pickups(self.player.rect):
                if kind == "heal":
                    self.state.heal(amount)
                    self.player.on_heal()
                    play_sound("pickup")

        if "player_dead" in events:
            self.state.register_death()
            self.reload_room()
        elif self.room.exit_reached(self.player.rect):
            if self.state.advance_room() == "game_end":
                self.game.scenes.change("end", deaths=self.state.deaths)
            else:
                self.reload_room()

    def draw(self, surface):
        draw_room(surface, self.room, self.debug)
        actors = [e for e in self.enemies if e.alive] + [self.player]
        for actor in sorted(actors, key=lambda a: a.y):
            actor.draw(surface)
        self.combat.draw(surface, self.state.level_index + 1)
        self.hud.draw(surface)
        if self.dialogue is not None:
            draw_dialogue(surface, self.dialogue)
            return
        for npc_id, (cx, cy), dialogue_id in self.room.npcs:
            if dialogue_id not in self.used_dialogues:
                x, top = npc_top_left(cx, cy)
                bob = int(pygame.time.get_ticks() / 250) % 2 * 2
                by = top - 6 - bob
                pygame.draw.circle(surface, (28, 28, 46), (cx, by), 11)
                pygame.draw.circle(surface, (255, 214, 90), (cx, by), 9)
                draw_text(surface, "!", (cx, by), 20, (28, 28, 46), center=True)
        npc = self.nearby_npc()
        if npc is not None:
            x, top = npc_top_left(*npc[1])
            draw_text(surface, "E — поговорить", (npc[1][0], top - 30), 18, center=True)
        level = getattr(settings, "DIFFICULTIES", {}).get(getattr(settings, "DIFFICULTY", ""), {}).get("name")
        if level:
            label = pygame.Surface((150, 22), pygame.SRCALPHA)
            label.fill((15, 15, 30, 170))
            surface.blit(label, (16, 60))
            draw_text(surface, f"Сложность: {level}", (24, 62), 16, (220, 220, 230))
