from pygame import Rect
import birch
from birch.game import Game

def main():
    scale = 16 * 32
    print('scale is', scale)
    tl = (0, 0, scale, scale)
    #tl = (-(scale / 2), scale / 2, scale, scale)
    print('tl', tl)
    game = Game(Rect(*tl), '%s/assets' % birch.ROOT)
    game.init()
    game.run()

if __name__ == '__main__':
    main()
