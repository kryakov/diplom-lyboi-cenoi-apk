import pygame

from src import settings

MUSIC_DIR = settings.ASSETS_DIR / "music"
SOUND_DIR = settings.ASSETS_DIR / "sounds"
EXTENSIONS = (".ogg", ".wav", ".mp3")

_ready = None
_sounds = {}
_music_name = None


def _init():
    global _ready
    if _ready is None:
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            _ready = True
        except pygame.error:
            _ready = False
    return _ready


def _find(folder, name):
    for ext in EXTENSIONS:
        path = folder / f"{name}{ext}"
        if path.exists():
            return path
    return None


SOUND_NAMES = ("shoot", "hit", "kill", "death", "pickup")


def _load(name):
    path = _find(SOUND_DIR, name)
    try:
        return pygame.mixer.Sound(str(path)) if path else None
    except pygame.error:
        return None


def preload_sounds():
    if _init():
        for name in SOUND_NAMES:
            if name not in _sounds:
                _sounds[name] = _load(name)


def play_sound(name, volume=0.6):
    """Короткий звук из assets/sounds/<name>.ogg|wav|mp3. Нет файла или звука: тишина, без ошибки."""
    if not _init():
        return
    if name not in _sounds:
        _sounds[name] = _load(name)
    sound = _sounds[name]
    if sound is not None:
        sound.set_volume(volume)
        sound.play()


def play_music(name, volume=0.4, loop=True):
    """Фоновая музыка из assets/music/<name>.ogg|wav|mp3. Если этот трек уже играет, ничего не делает."""
    global _music_name
    if not _init() or name == _music_name:
        return
    path = _find(MUSIC_DIR, name)
    if path is None:
        return
    try:
        pygame.mixer.music.load(str(path))
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1 if loop else 0)
        _music_name = name
    except pygame.error:
        _music_name = None


def stop_music():
    global _music_name
    if _init():
        pygame.mixer.music.stop()
    _music_name = None
