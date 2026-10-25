from src.core.game import Game


def main():
    game = Game()
    game.scenes.change("menu")
    game.run()


if __name__ == "__main__":
    main()
