import os
import birch
from birch.pyglame import BirchGame

def main():
    asset_path = os.path.realpath('%s/assets' % birch.ROOT)
    game = BirchGame(asset_path)
    game.run()

if __name__ == '__main__':
    main()
