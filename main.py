import asyncio

import pygame  # noqa: F401  pygbag качает в браузер только пакеты, импортированные в main.py

from src.core.game import Game


async def main():
    game = Game()
    game.scenes.change("menu")
    await game.run()


asyncio.run(main())
