from PIL import Image
import json

filenames = [
    'spritesheet.json',
    'water.json'
    ]

def cropit(im, name, position, size):
    if type(size) == int:
        size = (size, size)
    region = (
        position[0],
        position[1],
        position[0] + size[0],
        position[1] + size[1]
        )
    print(name, 'region', region)
    im.crop(region).save('birch/assets/%s.png' % name)

for fn in filenames:
    part = fn.split('.')[0]
    data = json.load(open('birch/assets/%s' % fn, 'r'))
    im = Image.open('assets/%s.png' % part)
    out_images = {}
    if 'structure' in data and \
        'type' in data['structure'] and \
        data['structure']['type'] == 'sheet':
        stride = data['structure']['stride']
        size = data['structure']['size']
        prefix = data['structure']['prefix']
        for i, name in enumerate(data['names']):
            print('Saving %s' % name)
            position = [(i % stride) * size, int(i / stride) * size]
            nname = '%s_%s' % (prefix, name)
            cropit(im, nname, position, size)
    else:
        for name in data['names']:
            print('Saving %s' % name)
            position = data['names'][name]['position']
            size = data['names'][name]['size']
            cropit(im, name, position, size)
