import json
from random import randint, random
import pyglet
import numpy as np
from ctypes import byref
from pyglet import sprite, resource
from pyglet.image import Texture
from pyglet.gl import *
from PIL import Image
from birch._birch import Perlin

class TextureStore(dict):

    metadata_paths = (
        'spritesheet.json',
        'water.json'
        )

    def __init__(self, asset_dir, *args, **kwargs):
        super(dict, self).__init__(*args, **kwargs);
        self.asset_dir = asset_dir

        pyglet.resource.path.extend([self.asset_dir, '/tmp'])
        pyglet.resource.reindex()
        for pat in self.metadata_paths:
            names = json.load(open('%s/%s' % (asset_dir, pat)))
            if 'structure' in names and 'type' in names['structure'] and \
                    names['structure']['type'] == 'sheet':
                prefix = names['structure']['prefix'] + '_'
            else:
                prefix = ''
            for name in names['names']:
                self.load('%s%s' % (prefix, name))
        self['r_1_0'] = self['r_0_0']
        self['c_1_0'] = self['c_0_0']
        self['i_1_0'] = self['i_0_0']
        self.pil_cache = {}
        self.data_cache = {}
        self.res_angle_cache = {}
        self.perlin = Perlin(randint(0,9999))

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

    def create_background(self, dim, ix, iy):
        # draw dirt stuff
        freq = 1/100
        imgdata = self.perlin.noise2_bytes(ix, iy, freq, 2, dim, 64)
        target = GL_TEXTURE_2D
        gid = GLuint()
        glGenTextures(1, byref(gid))
        glBindTexture(target, gid.value)
        glTexParameteri(target, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexImage2D(target, 0,
             GL_RGBA,
             dim, dim,
             0,
             GL_RGBA, GL_UNSIGNED_BYTE,
             imgdata)
        image = Texture(dim, dim, target, gid.value)
        key = 'bg_%d_%d' % (ix, iy)
        self[key] = image
        return key

