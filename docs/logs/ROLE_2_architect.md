# Роль 2. Архитектор

Лог художника для роли «Архитектор». Общий справочник: `docs/ART_LOG.md`, стиль: `docs/ART.md`, данные: `docs/art_info.json`. Все числа измерены по картинкам и коду `main`.

**Обязательно:** в `data/levels.json` на каждом уровне вставить новую комнату между `lN_battle1` и `lN_boss`: `l1_battle2`, `l2_battle2`, `l3_battle2` (четвёртые комнаты уровней, фоны `bg_level1_yard2`, `bg_level2_class2`, `bg_level3_hall2`; файлы комнат создаёт роль 3).

По желанию дописать в `docs/FORMAT.md`, раздел «Ключи спрайтов», схемы ниже (`validate_data.py` манифест не проверяет, игра работает и без этого).

## Схемы ключей

```
фон:                 bg_<имя>                     960×540, непрозрачный
одиночный спрайт:    enemy_<имя> | boss_<имя> | npc_<имя> | player_idle
анимация:            <имя>_<действие>_<направление>_<номер>
шкала здоровья:      ui_health_<n> (n = 0..5), ui_health_hit_<n>_<k> (n = 0..4, k = 1..6)
```

- Направления: `s se e ne n nw w sw`.
- Стрелки (`player`, `boss_level1`, `boss_level2`, `boss_level3`): действия `idle` (2), `walk` (4), `shoot` (2), `walkshoot` (4).
- Бойцы ближнего боя (`enemy_english_melee`, `enemy_binary_melee`, `enemy_formula_melee`): `idle` (2), `walk` (4), `attack` (2: замах, удар), `walkattack` (4).
- Стреляющий клювом (`enemy_hse_bird`, ворон ВШЭ): `idle` (2), `walk` (4), `shoot` (2: клюв открыт / закрыт); `walkshoot` нет.
- Номер с 1. Каждому из 8 имён по 96 кадров и один запасной статичный ключ (`player_idle` у героя, у остальных ключ без суффикса).

## Новые ключи в манифесте (сверх инструкции художника, заказ оператора)

`bg_entrance_l1/l2/l3`, `bg_level1_yard`, `bg_level1_boss`, `bg_level2_class`, `bg_level2_boss`, `bg_level3_boss`, `enemy_hse_bird`, анимации перечисленных имён, `ui_health_*`. `boss_commission` по решению оператора не рисуется.
