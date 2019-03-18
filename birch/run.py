from pygame import Rect
import birch
from birch.pyglame import BirchGame

def main():
    scale = 2048
    print('scale is', scale)
    tl = (-scale, -scale, scale * 2, scale * 2)
    #tl = (-(scale / 2), scale / 2, scale, scale)
    print('tl', tl)
    game = BirchGame(Rect(*tl), '%s/assets' % birch.ROOT)
    game.init()
    game.run()

if __name__ == '__main__':
    main()
