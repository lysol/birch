import json
import pyglet
from pyglet import sprite, resource

class TextureStore(dict):

    def __init__(self, asset_dir, *args, **kwargs):
        super(dict, self).__init__(*args, **kwargs);
        self.asset_dir = asset_dir

        pyglet.resource.path.extend([self.asset_dir])
        pyglet.resource.reindex()
        names = json.load(open('%s/names.json' % asset_dir))
        for name in names:
            self.load(name)
        self['r_1_0'] = self['r_0_0']
        self['c_1_0'] = self['c_0_0']
        self['i_1_0'] = self['i_0_0']

    def load(self, key):
        self[key] = resource.image("%s.png" % key)
        self[key].anchor_x = 0
        self[key].anchor_y = 0

    def get_sprite(self, key, x=0, y=0):
        image = self[key]
        outsprite = sprite.Sprite(img=self[key], x=x, y=y)
        outsprite.scale = 2.0
        return outsprite

