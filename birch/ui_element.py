from pyglet.graphics import Batch

class UIElement:

    width = 100
    height = 100

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.batch = Batch()
        self.click_regions = {}
        self.click_handlers = {}

    def handle_region(self, name, handler, x, y, w, h):
        self.click_regions[name] = (x, y, w, h)
        self.click_handlers[name] = handler

    def hover(self, pos):
        return True

    def in_region(self, x, y, rx, ry, rw, rh):
        return x >= rx and x <= rx + rw and \
            y >= ry and y <= ry + rh

    def check_mouse(self, pos, buttons):
        if len(buttons) == 0:
            # nothing clicked, hover
            if self.in_region(*pos, self.x, self.y, self.width, self.height):
                return self.hover(pos)
        else:
            for region in self.click_regions:
                r = self.click_regions[region]
                args = list(pos)
                args.extend(r)
                if self.in_region(*args):
                    self.click_handlers[region](region, *pos, buttons)
                    return True
        return False


