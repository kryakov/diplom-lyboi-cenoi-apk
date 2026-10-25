import json
from pathlib import Path

from src import settings
from src.entities.enemy import Enemy


def apply_difficulty(data, difficulty=None):
    """Копия данных врага с поправкой на сложность (settings.DIFFICULTIES). Без настроек данные не меняются."""
    table = getattr(settings, "DIFFICULTIES", {})
    k = table.get(difficulty if difficulty is not None else getattr(settings, "DIFFICULTY", None))
    if not k:
        return data
    d = json.loads(json.dumps(data))
    d["hp"] = max(1, round(d["hp"] * k["hp"]))
    d["speed"] = d["speed"] * k["speed"]
    blocks = [d[name] for name in ("attack", "shoot") if isinstance(d.get(name), dict)] + d.get("attacks", [])
    for b in blocks:
        if "cooldown" in b:
            b["cooldown"] = b["cooldown"] * k["cooldown"]
        if "windup" in b:
            b["windup"] = b["windup"] * k["windup"]
        if b.get("type") == "fan":
            b["projectiles"] = max(3, round(b["projectiles"] * k["projectiles"]))
    return d


def create_enemy(enemy_id, pos, data_dir=None, difficulty=None):
    base = Path(data_dir) if data_dir else settings.DATA_DIR
    with open(base / "enemies" / f"{enemy_id}.json", encoding="utf-8") as f:
        data = apply_difficulty(json.load(f), difficulty)
    if data["kind"] == "boss":
        from src.entities.boss import Boss
        return Boss(data, pos)
    return Enemy(data, pos)


def spawn_all(room, data_dir=None):
    return [create_enemy(eid, pos, data_dir) for eid, pos in room.enemy_spawns]


def alive_count(enemies):
    return sum(1 for e in enemies if e.alive)


def update_all(dt, room, enemies, target):
    for e in enemies:
        e.update(dt, room, target)


def draw_all(surface, enemies):
    for e in enemies:
        if e.alive:
            e.draw(surface)
