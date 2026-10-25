"""Загрузка комнат и списка уровней из JSON. Владелец: роль 3.
Форматы — docs/FORMAT.md. Пути строятся от settings.DATA_DIR, не от текущей папки.
"""
import json
from pathlib import Path

from src import settings
from src.systems.rooms import Room


def _read(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_room(room_id, data_dir=None):
    base = Path(data_dir) if data_dir else settings.DATA_DIR
    return Room(_read(base / "rooms" / f"{room_id}.json"))


def load_levels(data_dir=None):
    """Возвращает (levels, names): levels — список списков id комнат (для GameState), names — названия уровней."""
    base = Path(data_dir) if data_dir else settings.DATA_DIR
    d = _read(base / "levels.json")
    return [lv["rooms"] for lv in d["levels"]], [lv["name"] for lv in d["levels"]]