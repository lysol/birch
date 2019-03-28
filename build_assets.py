from PIL import Image
import json

data = json.load(open('birch/assets/names.json', 'r'))
im = Image.open('assets/spritesheet.png')
out_images = {}
for name in data:
    print('Saving %s' % name)
    position = data[name]['position']
    size = data[name]['size']
    if type(size) == int:
        size = (size, size)
    region = (
        position[0],
        position[1],
        position[0] + size[0],
        position[1] + size[1]
        )
    im.crop(region).save('birch/assets/%s.png' % name)
