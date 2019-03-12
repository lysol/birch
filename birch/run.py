from pygame import Rect
import birch
from birch.game import Game

def main():
    scale = 1024
    print('scale is', scale)
    tl = (-scale, -scale, scale * 2, scale * 2)
    #tl = (-(scale / 2), scale / 2, scale, scale)
    print('tl', tl)
    game = Game(Rect(*tl), '%s/assets' % birch.ROOT)
    game.init()
    game.run()

if __name__ == '__main__':
    main()
