import json
from random import randint, random
import pyglet
import numpy as np
from ctypes import byref
from pyglet import sprite, resource
from pyglet.image import Texture, Animation, AnimationFrame
from pyglet.gl import *
from PIL import Image
from birch._birch import Perlin

class TextureStore(dict):

    def __init__(self, asset_dir, metadata_paths, *args, **kwargs):
        super(dict, self).__init__(*args, **kwargs);
        self.asset_dir = asset_dir
        self.metadata_paths = metadata_paths

        pyglet.resource.path.extend([self.asset_dir, '/tmp'])
        pyglet.resource.reindex()
        for pat in self.metadata_paths:
            prefix = ''
            data = json.load(open('%s/%s' % (asset_dir, pat)))
            other = {}
            if 'inherit' in data['structure']:
                other = json.load(open('%s/%s' % (asset_dir, data['structure']['inherit'])))
            if 'names' not in data:
                data['names'] = other['names']
            if 'prefix' not in data['structure']:
                data['structure'] = other['structure']
            if 'animations' not in data and 'animations' in other:
                data['animations'] = other['animations']
            prefix = '' if 'prefix' not in data['structure'] else data['structure']['prefix'] + '_'
            for name in data['names']:
                prefixed = '%s%s' % (prefix, name)
                self.load('%s%s' % (prefix, name))
            if 'animations' in data:
                for anim in data['animations']:
                    self.create_animation(prefix, anim, data['animations'][anim])
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

    def create_animation(self, prefix, key, framedefs):
        frames = [AnimationFrame(self['%s%s' % (prefix, frame['name'])], frame['duration'])
            for frame in framedefs]
        anim_key = '%s%s' % (prefix, key)
        self[anim_key] = Animation(frames)

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

