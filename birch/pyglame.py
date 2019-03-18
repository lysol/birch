import pyglet

class BirchWindow(pyglet.window.Window):

    def on_draw(self):
        self.clear()


class BirchGame:

    def __init__(self, initial_rect, asset_dir):
        self.asset_dir = asset_dir
        self.window = BirchWindow()

    def init(self):
        pass

    def run(self):
        pyglet.clock.schedule_interval(self.update, 0.5)
        pyglet.app.run()

    def update(self, dt):
        pass

