from os import listdir
from shutil import copyfile
from PIL import Image
import json


def build_assets(incoming_src_dir, output_dir):

    filenames = [infile for infile in listdir(incoming_src_dir) if infile.endswith('.json')]

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
        im.crop(region).save('%s/%s.png' % (output_dir, name))

    for fn in filenames:
        part = fn.split('.')[0]
        data = json.load(open('%s/%s' % (incoming_src_dir, fn), 'r'))
        im = Image.open('%s/%s.png' % (incoming_src_dir, part))
        out_images = {}
        if 'structure' in data and \
            'type' in data['structure'] and \
            data['structure']['type'] == 'sheet':
            if 'inherit' in data['structure']:
                other = json.load(open('%s/%s' % (incoming_src_dir, data['structure']['inherit']), 'r'))
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
        copyfile('%s/%s' % (incoming_src_dir, fn), '%s/%s' % (output_dir, fn))



if __name__ == "__main__":
  build_assets('birch/examples/scamcity/assets_src', 'birch/examples/scamcity/assets')
