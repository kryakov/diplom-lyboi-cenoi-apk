# Форматы данных

Общие правила: UTF-8; координаты и размеры — в клетках (1 клетка = settings.TILE пикселей); начало координат — левый верхний угол, x вправо, y вниз; `id` = имя файла без .json; латиница, нижний регистр, подчёркивания.

## data/levels.json
{"levels": [{"id": "level1", "name": "Печерка", "rooms": ["l1_entrance", "l1_battle1", "l1_boss"]}, ...]}
Порядок в "rooms" — порядок прохождения. Ровно 3 уровня. Все id должны существовать в data/rooms.

## data/rooms/<id>.json
Обязательные поля:
- id, name (строка, русский допустим)
- type: "entrance" | "battle" | "boss"
- background: ключ из assets/manifest.json
- size: [ширина, высота] в клетках, всегда [32, 18]
- player_spawn: [x, y]
- walls: список прямоугольников [x, y, ширина, высота]; внешняя рамка обязательна
- enemies: список {"type": <id врага>, "pos": [x, y]}; пустой для entrance
- npcs: список {"id": <строка>, "pos": [x, y], "dialogue": <id диалога>}
- pickups: список {"kind": "heal", "pos": [x, y], "amount": число}
Необязательное:
- door: {"pos": [x, y, ширина, высота], "locked_until_clear": true|false} — выход в следующую комнату. Дверь открыта, когда убиты все враги (если locked_until_clear). У комнаты босса дверь открывается после убийства босса.
Правила: entrance — мирная (enemies пуст), в ней есть NPC и/или лечение; boss — ровно один враг с id, начинающимся на "boss_".

## data/enemies/<id>.json
Общие: id, name, kind ("melee" | "boss"), sprite (ключ manifest), hp (целое), speed (пикселей/с), contact_damage (целое).
kind "melee" — блок attack: {"range": пикселей, "windup": секунд замаха, "cooldown": секунд, "damage": целое}. Поведение: подходит к герою, останавливается на range, замах windup, удар, пауза cooldown.
kind "boss" — список attacks (минимум 2):
- {"type": "fan", "projectiles": N, "spread_deg": угол, "speed": пикс/с, "damage": целое, "cooldown": сек}
- {"type": "dash", "speed": пикс/с, "duration": сек, "windup": сек, "damage": целое, "cooldown": сек}

## data/dialogues/<id>.json
{"id": "...", "lines": [{"speaker": "Имя", "text": "Реплика"}, ...], "on_end": {"heal": число}}
on_end необязателен. Поддерживается только "heal". Имена вымышленные, без фамилий.

## Ключи спрайтов (assets/manifest.json)
Формат <категория>_<имя>: bg_, player_, enemy_, boss_, npc_, ui_, fx_. Заказ новых спрайтов — issue для роли Claude Code (художника).

## Смена формата
Только issue + согласие затронутых ролей + один PR, меняющий FORMAT.md, _examples и tools/validate_data.py. После дня 12 — запрещено.
