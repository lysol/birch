from pygame import transform, image
import json

class TextureStore(dict):

    def __init__(self, asset_dir, *args, **kwargs):
        super(dict, self).__init__(*args, **kwargs);
        self.asset_dir = asset_dir

        names = json.load(open('%s/names.json' % asset_dir))
        for name in names.values():
            self.load(name)

    def load(self, key):
        self[key] = transform.scale2x(image.load("%s/%s.png" % (self.asset_dir, key)))

