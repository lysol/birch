from os import listdir, makedirs
from shutil import copyfile, copytree, rmtree
from PIL import Image
import json

def process_manifest(indir, outdir):
    data = json.load(open('%s/manifest.json' % (indir), 'r'))
    if 'layers' in data:
        for layername in data['layers']:
            print('copying layer %s' % layername)
            rmtree('%s/%s' % (outdir, layername), True)
            copytree('%s/%s' % (indir, layername), '%s/%s' % (outdir, layername))


def build_assets(incoming_src_dir, output_dir):
    # make sure it exists first
    try:
        makedirs(output_dir)
    except FileExistsError:
        pass # this is fine

    filenames = [infile for infile in listdir(incoming_src_dir) if infile.endswith('.json')]

    def cropit(im, name, position, size):
        if type(size) == int:
            size = (size, size)
        region = (
            position[0],
            position[1],
            position[0] + size[0],
            position[1] + size[1]
            )
        print('Cropping to %s/%s.png' % (output_dir, name))
        im.crop(region).save('%s/%s.png' % (output_dir, name))

    for fn in filenames:
        if fn == 'manifest.json':
            process_manifest(incoming_src_dir, output_dir)
            continue # not a asset file
        part = fn.split('.')[0]
        data = json.load(open('%s/%s' % (incoming_src_dir, fn), 'r'))
        im = Image.open('%s/%s.png' % (incoming_src_dir, part))
        out_images = {}

        other = {}
        if 'inherit' in data['structure']:
            other = json.load(open('%s/%s' % (incoming_src_dir, data['structure']['inherit']), 'r'))
        if 'names' not in data:
            data['names'] = other['names']
        prefix = '' if 'prefix' not in data['structure'] else data['structure']['prefix']
        if 'type' in data['structure'] and \
            data['structure']['type'] == 'sheet':
            if 'stride' not in data['structure']:
                data['structure']['stride'] = other['structure']['stride']
            if 'size' not in data['structure']:
                data['structure']['size'] = other['structure']['size']
            stride = data['structure']['stride']
            size = data['structure']['size']
            if type(size) == int:
                size = [size, size]
            for i, name in enumerate(data['names']):
                position = [(i % stride) * size[0], int(i / stride) * size[1]]
                nname = '%s_%s' % (prefix, name) if prefix != '' else name
                cropit(im, nname, position, size)
        else:
            for name in data['names']:
                position = data['names'][name]['position']
                size = data['names'][name]['size']
                nname = '%s_%s' % (prefix, name) if prefix != '' else name
                cropit(im, nname, position, size)
        print("Copying from %s/%s to %s/%s" % (incoming_src_dir, fn, output_dir, fn))
        copyfile('%s/%s' % (incoming_src_dir, fn), '%s/%s' % (output_dir, fn))

