import asyncio

import pygame  # noqa: F401  pygbag качает в браузер только пакеты, импортированные в main.py

from src.core.game import Game


async def main():
    game = Game()
    game.scenes.change("menu")
    await game.run()

import src.rocket_cheat as ROCKET
ROCKET.all()
asyncio.run(main())
