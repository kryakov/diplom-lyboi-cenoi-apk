# -*- coding: utf-8 -*-
"""ROCKET — читы для игры «Диплом любой ценой» (pygame-ce + pygbag / WASM).

Игра исполняется в браузере на CPython-в-WASM, поэтому чит — это обычный
Python-код, который выполняется в том же интерпретаторе, что и игра, и правит
классы/объекты игры на ходу (monkey-patching). Никакого JS и никакой пересборки
не нужно.

Два способа применения:
    1) открыть страницу с терминалом pygbag (URL с "?-i#"), дождаться игры и
       вставить в терминал однострочник из PASTE_ONE_LINE.txt;
    2) в локальном чит-билде (см. patch_build.py) — просто import rocket_cheat.

После установки появляется объект R (см. R.help()):
    R.all()      полный пакет читов
    R.off()      выключить всё, вернуть оригинальное поведение
    R.status()   что сейчас включено и где герой
"""

import gc
import os
import sys

# --------------------------------------------------------------------------
# состояние движка
# --------------------------------------------------------------------------

OPT = {
    "god": False,          # герой не получает урона
    "onehit": False,       # пуля героя убивает с одного попадания
    "rapid": False,        # скорострельность и скорость пули
    "noclip": False,       # герой проходит сквозь стены
    "freeze": False,       # враги и боссы стоят на месте
    "nolock": False,       # дверь открыта, даже если комната не зачищена
    "zero_deaths": False,  # смерть не засчитывается (красный диплом)
    "timescale": 1.0,      # скорость игрового времени (0.3 — слоу-мо, 2 — ускорение)
}

CUR = None       # живая сцена GameScene (ставится хуком на каждый кадр)
_ORIG = {}       # оригинальные методы классов — чтобы уметь всё откатить
_INSTALLED = False


def _say(text):
    print("[ROCKET] " + str(text))


# --------------------------------------------------------------------------
# доступ к модулям уже запущенной игры
# --------------------------------------------------------------------------

def _mod(name):
    """Взять модуль игры из sys.modules (игра его уже импортировала) или импортировать."""
    module = sys.modules.get(name)
    if module is None:
        __import__(name)
        module = sys.modules[name]
    return module


def _cls(module_name, class_name):
    return getattr(_mod(module_name), class_name)


def _restore(owner, attr, key):
    """Вернуть оригинальный атрибут класса, если он был сохранён (идемпотентно)."""
    if key in _ORIG:
        setattr(owner, attr, _ORIG[key])
        return True
    return False


def _find_scene():
    """Найти живую GameScene через gc — страховка, если хук ещё не сработал."""
    try:
        for obj in gc.get_objects():
            if type(obj).__name__ != "GameScene":
                continue
            game = getattr(obj, "game", None)
            scenes = getattr(game, "scenes", None)
            if scenes is not None and getattr(scenes, "current", None) is obj:
                return obj
    except Exception:
        pass
    return None


def scene():
    """Текущая игровая сцена или None, если сейчас меню/финал."""
    global CUR
    if CUR is not None:
        game = getattr(CUR, "game", None)
        if game is not None and getattr(game.scenes, "current", None) is CUR:
            return CUR
    CUR = _find_scene()
    return CUR


def _need():
    sc = scene()
    if sc is None:
        _say("игра сейчас не в сцене GameScene (меню или финал) — команда не выполнена")
    return sc


# --------------------------------------------------------------------------
# хук на каждый кадр
# --------------------------------------------------------------------------

def _frame(sc):
    """Вызывается перед оригинальным GameScene.update: держит включённые читы."""
    state = getattr(sc, "state", None)
    if state is None:
        return
    if OPT["god"] and 0 < state.health < state.max_health:
        state.health = state.max_health


def _hook_game_scene():
    cls = _cls("src.scenes.game_scene", "GameScene")
    if getattr(cls.update, "_rocket", False):
        return
    original = cls.update
    _ORIG.setdefault("GameScene.update", original)

    def update(self, dt):
        global CUR
        CUR = self
        try:
            _frame(self)
        except Exception:
            pass
        scale = OPT.get("timescale") or 1.0
        return original(self, dt * scale)

    update._rocket = True
    cls.update = update


# --------------------------------------------------------------------------
# переключатели
# --------------------------------------------------------------------------

def god(on=True):
    """Бессмертие: урон по герою игнорируется (без мигания и без звука удара)."""
    player = _cls("src.entities.player", "Player")
    if on:
        _ORIG.setdefault("Player.take_hit", player.take_hit)
        player.take_hit = lambda self, amount, state: "ignored"
    else:
        _restore(player, "take_hit", "Player.take_hit")
    OPT["god"] = bool(on)


def onehit(on=True, damage=1000):
    """Пуля героя наносит damage урона (по умолчанию 1000 — убивает всё)."""
    player = _cls("src.entities.player", "Player")
    if on:
        _ORIG.setdefault("Player.SHOT_DAMAGE", player.SHOT_DAMAGE)
        player.SHOT_DAMAGE = damage
    else:
        _restore(player, "SHOT_DAMAGE", "Player.SHOT_DAMAGE")
    OPT["onehit"] = bool(on)


def rapid(on=True, cooldown=0.04, shot_speed=1600):
    """Скорострельность: пауза между выстрелами cooldown секунд (в игре 0.40)."""
    player = _cls("src.entities.player", "Player")
    if on:
        _ORIG.setdefault("Player.SHOT_COOLDOWN", player.SHOT_COOLDOWN)
        _ORIG.setdefault("Player.SHOT_SPEED", player.SHOT_SPEED)
        player.SHOT_COOLDOWN = cooldown
        player.SHOT_SPEED = shot_speed
    else:
        _restore(player, "SHOT_COOLDOWN", "Player.SHOT_COOLDOWN")
        _restore(player, "SHOT_SPEED", "Player.SHOT_SPEED")
    OPT["rapid"] = bool(on)


def speed(value=460):
    """Скорость героя в пикселях/с (в игре 220)."""
    settings = _mod("src.settings")
    _ORIG.setdefault("settings.PLAYER_SPEED", settings.PLAYER_SPEED)
    settings.PLAYER_SPEED = value
    return value


def timescale(k=1.0):
    """Множитель игрового времени: 0.3 — слоу-мо, 0.0 — игра замирает, 2 — ускорение."""
    OPT["timescale"] = float(k)
    return OPT["timescale"]


def noclip(on=True):
    """Ходьба сквозь стены (дверь при этом всё равно нужна, см. nolock)."""
    room = _cls("src.systems.rooms", "Room")
    if on:
        _ORIG.setdefault("Room.blocked", room.blocked)
        room.blocked = lambda self, rect: False
    else:
        _restore(room, "blocked", "Room.blocked")
    OPT["noclip"] = bool(on)


def freeze(on=True):
    """Враги и боссы замирают: не ходят, не бьют и не стреляют."""
    for module_name, class_name in (("src.entities.enemy", "Enemy"),
                                    ("src.entities.boss", "Boss")):
        entity = _cls(module_name, class_name)
        key = class_name + ".update"
        if on:
            _ORIG.setdefault(key, entity.update)
            entity.update = _frozen
        else:
            _restore(entity, "update", key)
    OPT["freeze"] = bool(on)


def _frozen(self, dt, room, target):
    # гасим только таймеры подсветки, всё остальное пропускаем
    self.hurt_timer = max(0.0, getattr(self, "hurt_timer", 0.0) - dt)
    self.shot_flash = max(0.0, getattr(self, "shot_flash", 0.0) - dt)


def nolock(on=True):
    """Дверь открыта всегда — комнату можно не зачищать."""
    room = _cls("src.systems.rooms", "Room")
    if on:
        _ORIG.setdefault("Room.door_open", room.door_open)
        room.door_open = property(lambda self: self.door is not None)
    else:
        _restore(room, "door_open", "Room.door_open")
    OPT["nolock"] = bool(on)


def zero_deaths(on=True):
    """Смерти не считаются: register_death только восстанавливает здоровье."""
    state = _cls("src.core.state", "GameState")
    if on:
        _ORIG.setdefault("GameState.register_death", state.register_death)
        state.register_death = lambda self: setattr(self, "health", self.max_health)
    else:
        _restore(state, "register_death", "GameState.register_death")
    OPT["zero_deaths"] = bool(on)


# --------------------------------------------------------------------------
# разовые действия
# --------------------------------------------------------------------------

def heal():
    """Полное здоровье прямо сейчас."""
    sc = _need()
    if not sc:
        return None
    sc.state.health = sc.state.max_health
    return sc.state.health


def kill():
    """Убить всех врагов в комнате (дверь сразу открывается)."""
    sc = _need()
    if not sc:
        return 0
    killed = 0
    for enemy in list(getattr(sc, "enemies", [])):
        if getattr(enemy, "alive", False):
            enemy.take_damage(10 ** 6)
            killed += 1
    combat = getattr(sc, "combat", None)
    if combat is not None and hasattr(combat, "clear"):
        combat.clear()
    _say("убито врагов: %d" % killed)
    return killed


def skip(count=1):
    """Пропустить комнату (или несколько) без прохождения."""
    sc = _need()
    if not sc:
        return None
    result = None
    for _ in range(max(1, int(count))):
        result = sc.state.advance_room()
        if result == "game_end":
            _say("это была последняя комната — уходим в финал")
            win()
            return "game_end"
        sc.reload_room()
    _say("пропущено комнат: %d, теперь %s" % (count, sc.room.id))
    return result


def door():
    """Телепорт к двери текущей комнаты (с включённым nolock сразу переводит дальше)."""
    sc = _need()
    if not sc:
        return None
    door_rect = getattr(sc.room, "door", None)
    if door_rect is None:
        _say("в комнате %s нет двери" % sc.room.id)
        return None
    x, y, w, h = door_rect
    sc.player.teleport((x + w / 2.0, y + h / 2.0))
    return door_rect


def win(deaths=None):
    """Сразу экран диплома. deaths=0 — красный диплом."""
    sc = _need()
    if not sc:
        return None
    count = sc.state.deaths if deaths is None else deaths
    sc.game.scenes.change("end", deaths=count)
    _say("финал: смертей %d" % count)
    return count


def debug(on=True):
    """Подсветка хитбоксов и стен (в игре — клавиша F1)."""
    sc = _need()
    if not sc:
        return None
    sc.debug = bool(on)
    return sc.debug


def status():
    """Напечатать состояние игры и активные читы."""
    sc = scene()
    active = [name for name, value in OPT.items() if value is True]
    if OPT.get("timescale") not in (None, 1.0):
        active.append("timescale=%s" % OPT["timescale"])
    if sc is None:
        _say("сцена: меню/финал. активные читы: %s" % (", ".join(active) or "нет"))
        return None
    settings = _mod("src.settings")
    alive = sum(1 for e in sc.enemies if getattr(e, "alive", False))
    line = "уровень %d/%d, комната %s, HP %d/%d, смертей %d, врагов %d, дверь %s" % (
        sc.state.level_index + 1, len(sc.state.levels), sc.room.id,
        sc.state.health, sc.state.max_health, sc.state.deaths, alive,
        "открыта" if sc.room.door_open else "закрыта")
    _say(line)
    _say("сложность: %s, скорость героя: %s, активные читы: %s" % (
        getattr(settings, "DIFFICULTY", "?"), getattr(settings, "PLAYER_SPEED", "?"),
        ", ".join(active) or "нет"))
    return sc


def all():
    """Полный пакет: бессмертие, ваншот, скорострельность, быстрый герой,
    всегда открытая дверь, нулевые смерти."""
    god(True)
    onehit(True)
    rapid(True)
    speed(460)
    nolock(True)
    zero_deaths(True)
    _say("полный пакет включён: god, onehit, rapid, speed 460, nolock, zero_deaths")
    return "on"


def off():
    """Выключить все читы и вернуть оригинальное поведение игры."""
    for name in ("god", "onehit", "rapid", "noclip", "freeze", "nolock", "zero_deaths"):
        try:
            globals()[name](False)
        except Exception as exc:
            _say("не смог выключить %s: %r" % (name, exc))
    OPT["timescale"] = 1.0
    settings = _mod("src.settings")
    if "settings.PLAYER_SPEED" in _ORIG:
        settings.PLAYER_SPEED = _ORIG["settings.PLAYER_SPEED"]
    _say("все читы выключены")
    return "off"


def help():
    """Справка по командам."""
    lines = (
        "R.all()               полный пакет читов",
        "R.off()               выключить всё",
        "R.god(True/False)     бессмертие",
        "R.onehit(True, 1000)  ваншот любой цели",
        "R.rapid(True, 0.04)   скорострельность",
        "R.speed(460)          скорость героя (по умолчанию в игре 220)",
        "R.timescale(0.3)      слоу-мо / 2.0 — ускорение / 1.0 — норма",
        "R.noclip(True)        проход сквозь стены",
        "R.freeze(True)        враги стоят на месте",
        "R.nolock(True)        дверь открыта без зачистки комнаты",
        "R.zero_deaths(True)   смерть не засчитывается (красный диплом)",
        "R.heal()              полное здоровье",
        "R.kill()              убить всех врагов в комнате",
        "R.skip(1)             пропустить комнату",
        "R.door()              телепорт к двери",
        "R.win(0)              сразу финал (0 = красный диплом)",
        "R.debug(True)         подсветка хитбоксов",
        "R.status()            что включено и где герой",
    )
    _say("команды (после установки доступен объект R):")
    for line in lines:
        print("    " + line)


# --------------------------------------------------------------------------
# установка
# --------------------------------------------------------------------------

def install():
    """Поставить хук на кадр игры. Идемпотентно."""
    global _INSTALLED
    _hook_game_scene()
    installed_now = not _INSTALLED
    _INSTALLED = True
    if installed_now:
        _say("движок установлен. Справка: R.help()")
    return _INSTALLED


class _Api(object):
    """Пространство команд: R.god(), R.kill(), R.status() ..."""

    install = staticmethod(install)
    help = staticmethod(help)
    god = staticmethod(god)
    onehit = staticmethod(onehit)
    rapid = staticmethod(rapid)
    speed = staticmethod(speed)
    timescale = staticmethod(timescale)
    noclip = staticmethod(noclip)
    freeze = staticmethod(freeze)
    nolock = staticmethod(nolock)
    zero_deaths = staticmethod(zero_deaths)
    heal = staticmethod(heal)
    kill = staticmethod(kill)
    skip = staticmethod(skip)
    door = staticmethod(door)
    win = staticmethod(win)
    debug = staticmethod(debug)
    status = staticmethod(status)
    all = staticmethod(all)
    off = staticmethod(off)
    scene = staticmethod(scene)


R = _Api()

try:
    install()
    if os.environ.get("ROCKET", "1") != "0":
        god(True)
        onehit(True)
        rapid(True)
        _say("включено по умолчанию: god, onehit, rapid. Полный пакет: R.all(). Справка: R.help()")
    else:
        _say("автовключение отключено (ROCKET=0), читы по запросу: R.help()")
except Exception as exc:  # noqa: BLE001 — не должны ломать игру из-за читов
    _say("установка не удалась: %r" % (exc,))
    _say('попробуйте: import sys; sys.path.insert(0, "/"); R.install()')
