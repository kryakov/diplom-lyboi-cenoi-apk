class Scene:

    def __init__(self, game):
        self.game = game

    def on_enter(self, **kwargs):
        pass

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, surface):
        pass


class SceneManager:
    def __init__(self, game):
        self.game = game
        self._scenes = {}
        self.current = None

    def register(self, name, scene):
        self._scenes[name] = scene

    def change(self, name, **kwargs):
        if name not in self._scenes:
            raise KeyError(f"Сцена '{name}' не зарегистрирована")
        self.current = self._scenes[name]
        self.current.on_enter(**kwargs)
