import os
from pygame import Rect
import birch
from birch.pyglame import BirchGame

def main():
    scale = 2048
    tl = (-scale, -scale, scale * 2, scale * 2)
    #tl = (-(scale / 2), scale / 2, scale, scale)
    asset_path = os.path.realpath('%s/assets' % birch.ROOT)
    game = BirchGame(Rect(*tl), asset_path)
    game.run()

if __name__ == '__main__':
    main()
