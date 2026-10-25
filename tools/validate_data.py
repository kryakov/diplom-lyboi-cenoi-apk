import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
ROOM_TYPES = {"entrance", "battle", "boss"}
ENEMY_KINDS = {"melee", "ranged", "boss"}
ATTACK_TYPES = {"fan", "dash"}


def _load(path, errors):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        errors.append(f"{path.name}: не читается как JSON ({e})")
        return None


def _is_rect(v, n=4):
    return isinstance(v, list) and len(v) == n and all(isinstance(x, int) for x in v)


def check_room(d, name, enemy_ids, dialogue_ids):
    e = []
    for k in ("id", "name", "type", "background", "size", "player_spawn", "walls", "enemies", "npcs", "pickups"):
        if k not in d:
            e.append(f"{name}: нет поля '{k}'")
    if e:
        return e
    if d["id"] != name.removesuffix(".json"):
        e.append(f"{name}: id '{d['id']}' не совпадает с именем файла")
    if d["type"] not in ROOM_TYPES:
        e.append(f"{name}: type должен быть одним из {sorted(ROOM_TYPES)}")
    if not _is_rect(d["size"], 2):
        e.append(f"{name}: size = [ширина, высота] целыми")
    if not _is_rect(d["player_spawn"], 2):
        e.append(f"{name}: player_spawn = [x, y] целыми")
    for w in d["walls"]:
        if not _is_rect(w):
            e.append(f"{name}: стена {w} должна быть [x, y, w, h] целыми")
    for en in d["enemies"]:
        if en.get("type") not in enemy_ids:
            e.append(f"{name}: неизвестный враг '{en.get('type')}'")
        if not _is_rect(en.get("pos", []), 2):
            e.append(f"{name}: у врага нет pos [x, y]")
    for npc in d["npcs"]:
        if npc.get("dialogue") not in dialogue_ids:
            e.append(f"{name}: неизвестный диалог '{npc.get('dialogue')}'")
    door = d.get("door")
    if door and _is_rect(door.get("pos", [])):
        dx, dy, dw, dh = door["pos"]
        for w in d["walls"]:
            if _is_rect(w) and w[0] < dx + dw and dx < w[0] + w[2] and w[1] < dy + dh and dy < w[1] + w[3]:
                e.append(f"{name}: стена {w} перекрывает дверь {door['pos']} (разрежь стену, оставь проход)")
    if d["type"] == "boss" and not any(en.get("type", "").startswith("boss") for en in d["enemies"]):
        e.append(f"{name}: в комнате босса нет босса (id врага должен начинаться с 'boss')")
    return e


def check_enemy(d, name):
    e = []
    for k in ("id", "name", "kind", "sprite", "hp", "speed", "contact_damage"):
        if k not in d:
            e.append(f"{name}: нет поля '{k}'")
    if e:
        return e
    if d["kind"] not in ENEMY_KINDS:
        e.append(f"{name}: kind должен быть одним из {sorted(ENEMY_KINDS)}")
    if d["kind"] == "melee" and "attack" not in d:
        e.append(f"{name}: у melee нужен блок 'attack'")
    if d["kind"] == "boss":
        atk = d.get("attacks", [])
        if len(atk) < 2:
            e.append(f"{name}: у босса нужно минимум 2 атаки")
        for a in atk:
            if a.get("type") not in ATTACK_TYPES:
                e.append(f"{name}: тип атаки должен быть одним из {sorted(ATTACK_TYPES)}")
    return e


def check_dialogue(d, name):
    e = []
    if "id" not in d or not isinstance(d.get("lines"), list) or not d["lines"]:
        return [f"{name}: нужны 'id' и непустой 'lines'"]
    for ln in d["lines"]:
        if "speaker" not in ln or "text" not in ln:
            e.append(f"{name}: у реплики должны быть speaker и text")
    return e


def main():
    errors = []
    enemies, dialogues = {}, {}
    for p in sorted((DATA / "enemies").glob("*.json")):
        d = _load(p, errors)
        if d is not None:
            errors += check_enemy(d, p.name)
            enemies[d.get("id")] = d
    for p in sorted((DATA / "dialogues").glob("*.json")):
        d = _load(p, errors)
        if d is not None:
            errors += check_dialogue(d, p.name)
            dialogues[d.get("id")] = d
    rooms = {}
    for p in sorted((DATA / "rooms").glob("*.json")):
        d = _load(p, errors)
        if d is not None:
            errors += check_room(d, p.name, enemies, dialogues)
            rooms[d.get("id")] = d
    lv = DATA / "levels.json"
    if lv.exists() and "--strict" in sys.argv:
        d = _load(lv, errors)
        if d is not None:
            for level in d.get("levels", []):
                for rid in level.get("rooms", []):
                    if rid not in rooms:
                        errors.append(f"levels.json: комнаты '{rid}' нет в data/rooms")
    for line in errors:
        print("ОШИБКА:", line)
    print(f"Проверено: комнат {len(rooms)}, врагов {len(enemies)}, диалогов {len(dialogues)}. Ошибок: {len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
