from PIL import Image
import json


def build_assets():
    filenames = [
        'spritesheet.json',
        'water.json',
        'road.json',
        'rail.json'
        ]

    def cropit(im, name, position, size):
        print('Cropping %s' % name)
        if type(size) == int:
            size = (size, size)
        region = (
            position[0],
            position[1],
            position[0] + size[0],
            position[1] + size[1]
            )
        im.crop(region).save('birch/assets/%s.png' % name)

    for fn in filenames:
        part = fn.split('.')[0]
        data = json.load(open('birch/assets/%s' % fn, 'r'))
        im = Image.open('assets/%s.png' % part)
        out_images = {}
        if 'structure' in data and \
            'type' in data['structure'] and \
            data['structure']['type'] == 'sheet':
            if 'inherit' in data['structure']:
                other = json.load(open('birch/assets/%s' % data['structure']['inherit'], 'r'))
                if 'stride' not in data['structure']:
                    data['structure']['stride'] = other['structure']['stride']
                if 'size' not in data['structure']:
                    data['structure']['size'] = other['structure']['size']
                if 'names' not in data:
                    data['names'] = other['names']
            stride = data['structure']['stride']
            size = data['structure']['size']
            prefix = data['structure']['prefix']
            for i, name in enumerate(data['names']):
                position = [(i % stride) * size, int(i / stride) * size]
                nname = '%s_%s' % (prefix, name)
                cropit(im, nname, position, size)
        else:
            for name in data['names']:
                position = data['names'][name]['position']
                size = data['names'][name]['size']
                cropit(im, name, position, size)


if __name__ == "__main__":
  build_assets()
