from game import Game
from pygame import Rect

scale = 16 * 32
tl = (-(scale / 2), scale / 2, scale, scale)
game = Game(Rect(*tl))
game.init()
game.run()
