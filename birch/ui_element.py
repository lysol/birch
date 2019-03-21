from pyglet.graphics import Batch

class UIElement:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.batch = Batch()
        self.click_regions = {}
        self.click_handlers = {}

    def handle_region(self, name, handler, x, y, w, h):
        self.click_regions[name] = (x, y, w, h)
        self.click_handlers[name] = handler

    def check_mouse(self, pos, buttons):
        for region in self.click_regions:
            r = self.click_regions[region]
            if pos[0] >= r[0] and pos[0] <= r[0] + r[2] and \
                pos[1] >= r[1] and pos[1] <= r[1] + r[3]:
                self.click_handlers[region](region, *pos, buttons)
                return True
        return False


