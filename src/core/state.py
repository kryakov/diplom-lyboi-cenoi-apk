from src import settings


class GameState:

    def __init__(self, levels):
        if not levels or any(not rooms for rooms in levels):
            raise ValueError("levels должен содержать хотя бы одну комнату в каждом уровне")
        self.levels = levels
        self.reset()

    def reset(self):
        self.max_health = settings.PLAYER_MAX_HEALTH
        self.health = self.max_health
        self.level_index = 0
        self.room_index = 0
        self.deaths = 0

    @property
    def current_room_id(self):
        return self.levels[self.level_index][self.room_index]

    @property
    def is_alive(self):
        return self.health > 0

    @property
    def red_diploma(self):
        return self.deaths <= settings.RED_DIPLOMA_MAX_DEATHS

    def damage(self, amount=1):
        if amount < 0:
            raise ValueError("amount должен быть >= 0")
        if self.health <= 0:
            return False
        self.health = max(0, self.health - amount)
        return self.health == 0

    def heal(self, amount=1):
        if amount < 0:
            raise ValueError("amount должен быть >= 0")
        self.health = min(self.max_health, self.health + amount)

    def register_death(self):
        self.deaths += 1
        self.health = self.max_health

    def advance_room(self):
        if self.room_index + 1 < len(self.levels[self.level_index]):
            self.room_index += 1
            return "room"
        if self.level_index + 1 < len(self.levels):
            self.level_index += 1
            self.room_index = 0
            return "level"
        return "game_end"
