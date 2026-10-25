import json
from pathlib import Path

from src import settings

NPC_RADIUS = 48


def load_dialogue(dialogue_id, data_dir=None):
    base = Path(data_dir) if data_dir else settings.DATA_DIR
    with open(base / "dialogues" / f"{dialogue_id}.json", encoding="utf-8") as f:
        return json.load(f)


class DialogueSession:
    def __init__(self, data):
        if not data.get("lines"):
            raise ValueError("В диалоге нет реплик")
        self.id = data["id"]
        self.lines = data["lines"]
        self.on_end = data.get("on_end") or {}
        self.index = 0

    @property
    def finished(self):
        return self.index >= len(self.lines)

    @property
    def current(self):
        return None if self.finished else self.lines[self.index]

    def advance(self):
        if not self.finished:
            self.index += 1
        return self.finished


def nearby_npc(npcs, pos, radius=NPC_RADIUS):
    best, best_dist = None, radius
    for npc in npcs:
        dx, dy = npc[1][0] - pos[0], npc[1][1] - pos[1]
        dist = (dx * dx + dy * dy) ** 0.5
        if dist <= best_dist:
            best, best_dist = npc, dist
    return best


def apply_result(session, state, used):
    if session.id in used:
        return {}
    used.add(session.id)
    result = {}
    heal = session.on_end.get("heal")
    if heal:
        state.heal(heal)
        result["heal"] = heal
    return result
