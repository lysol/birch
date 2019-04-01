import json
from random import randint, random
import pyglet
import numpy as np
from ctypes import byref
from pyglet import sprite, resource
from pyglet.image import Texture, ImageData
from pyglet.gl import *
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

    def generate_perlin_noise_2d(self, shape, res):
        def f(t):
            return 6*t**5 - 15*t**4 + 10*t**3
        delta = (res[0] / shape[0], res[1] / shape[1])
        d = (shape[0] // res[0], shape[1] // res[1])
        grid = np.mgrid[0:res[0]:delta[0],0:res[1]:delta[1]].transpose(1, 2, 0) % 1
        # Gradients
        angles = 2*np.pi*np.random.rand(res[0]+1, res[1]+1)
        gradients = np.dstack((np.cos(angles), np.sin(angles)))
        g00 = gradients[0:-1,0:-1].repeat(d[0], 0).repeat(d[1], 1)
        g10 = gradients[1:  ,0:-1].repeat(d[0], 0).repeat(d[1], 1)
        g01 = gradients[0:-1,1:  ].repeat(d[0], 0).repeat(d[1], 1)
        g11 = gradients[1:  ,1:  ].repeat(d[0], 0).repeat(d[1], 1)
        # Ramps
        n00 = np.sum(np.dstack((grid[:,:,0]  , grid[:,:,1]  )) * g00, 2)
        n10 = np.sum(np.dstack((grid[:,:,0]-1, grid[:,:,1]  )) * g10, 2)
        n01 = np.sum(np.dstack((grid[:,:,0]  , grid[:,:,1]-1)) * g01, 2)
        n11 = np.sum(np.dstack((grid[:,:,0]-1, grid[:,:,1]-1)) * g11, 2)
        # Interpolation
        t = f(grid)
        n0 = n00*(1-t[:,:,0]) + t[:,:,0]*n10
        n1 = n01*(1-t[:,:,0]) + t[:,:,0]*n11
        return np.sqrt(2)*((1-t[:,:,1])*n0 + t[:,:,1]*n1)

    def speck(self, arr, y, x, color=(0, 0, 0, 255)):
        arr[y, x] = color[0]
        arr[y, x + 1] = color[1]
        arr[y, x + 2] = color[2]
        arr[y, x + 3] = color[3]

    def create_background(self, dim, ix, iy):
        img = Image.new('RGBA', (dim, dim))
        # draw dirt stuff
        octaves = 3
        freq = 256.0
        dirts = 0
        size = 16
        lower_bound = -1
        upper_bound = 1
        range_amount = upper_bound - lower_bound
        tex_count = 5
        fract = range_amount / tex_count
        imgdata = np.zeros((dim, dim * 4), dtype='uint8')
        noises = self.generate_perlin_noise_2d((dim / size * 2, dim / size * 2), (32, 16))
        clear = (0, 0, 0, 0)
        black = (0, 0, 0, 255)
        def rc():
            return black if randint(0,1) == 0 else clear

        for x in range(0, dim, size):
            for y in range(0, dim, size):
                ox, oy = ix + x, iy + y
                #noised = snoise2(ox / freq, oy / freq)
                noised = noises[int(y / size), int(x / size)]
                for i, lower in enumerate(np.arange(lower_bound, upper_bound, fract)):
                    if i == 0:
                        continue
                    if noised > lower and noised < lower + fract:
                        #tex_key = 'dirt_%d_%d' % (i - 1, randint(0,1))
                        #texdata = self.textures.data(tex_key)
                        texdata = np.zeros((size, size * 4), dtype='uint8')
                        for z in range(randint(0, 4**i)):
                            a, b = randint(0, size - 1), randint(0, size - 1) * 4
                            if a < 14 and a > 0 and b < 14 and random() > 0.9:
                                # big dirt
                                self.speck(texdata, a, b + 4, color=rc())
                                self.speck(texdata, a, b + 8, color=rc())
                                self.speck(texdata, a + 1, b, color=rc())
                                self.speck(texdata, a + 1, b + 4, color=rc())
                                self.speck(texdata, a + 1, b + 8, color=rc())
                            self.speck(texdata, a, b)
                        imgdata[y:y + texdata.shape[0], x * 4: x * 4 + texdata.shape[1]] = texdata
        tex_data = (GLubyte * imgdata.size).from_buffer(imgdata)
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
             tex_data)
        #image = ImageData(dim, dim, "RGBA", tex_data).create_texture(NearestTexture)
        image = Texture(dim, dim, target, gid.value)
        key = 'bg_%d_%d' % (ix, iy)
        self[key] = image
        return key

