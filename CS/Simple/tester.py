#!/usr/bin/env python
from Simple import Game
game = Game("Player1","TestScene")
game.join("Player2")
game.start()
print game.getUpdate()
print game.getUpdate("Player1")
print game.getUpdate("Player2")

