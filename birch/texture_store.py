import json
import pyglet
import numpy as np
from pyglet import sprite, resource
from pyglet.image import Texture
from pyglet.gl import GL_NEAREST
from PIL import Image

class TextureStore(dict):

    def __init__(self, asset_dir, *args, **kwargs):
        super(dict, self).__init__(*args, **kwargs);
        self.asset_dir = asset_dir

        pyglet.resource.path.extend([self.asset_dir, '/tmp'])
        pyglet.resource.reindex()
        names = json.load(open('%s/names.json' % asset_dir))
        for name in names:
            self.load(name)
        self['r_1_0'] = self['r_0_0']
        self['c_1_0'] = self['c_0_0']
        self['i_1_0'] = self['i_0_0']
        self.pil_cache = {}
        self.data_cache = {}

    def data(self, key):
        if key not in self.data_cache:
            tex = self[key]
            data = self[key].get_image_data().get_data('RGBA', (tex.width * 4))
            npdata = np.frombuffer(data, dtype='uint8').reshape((tex.height, tex.width * 4))
            self.data_cache[key] = npdata
            #np.savetxt('/tmp/%s' % key, npdata, fmt='%d')
        return self.data_cache[key]


    def load_pil(self, key):
        if key not in self.pil_cache:
            img = Image.open('%s/%s.png' % (self.asset_dir, key))
            self.pil_cache[key] = img
        return self.pil_cache[key]

    def paste(self, x, y, img, key):
        incoming = self.load_pil(key)
        img.paste(incoming, (x, y))

    def load(self, key, filename=None, reindex=False):
        if filename is None:
            filename = "%s.png" % key
        if reindex:
            pyglet.resource.reindex()
        self[key] = resource.image(filename)
        self[key].anchor_x = 0
        self[key].anchor_y = 0
        return self[key]

    def get_sprite(self, key, x=0, y=0):
        image = self[key]
        outsprite = sprite.Sprite(img=self[key], x=x, y=y)
        outsprite.scale = 2.0
        return outsprite

