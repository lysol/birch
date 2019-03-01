from PIL import Image
import json

data = json.load(open('assets/names.json', 'r'))
im = Image.open('assets/spritesheet.png')
out_images = {}
for name in data:
    print('Saving %s' % name)
    position = data[name]['position']
    size = data[name]['size']
    region = (
        position[0],
        position[1],
        position[0] + size,
        position[1] + size
        )
    im.crop(region).save('assets/%s.png' % name)
