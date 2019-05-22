from birch.game import BirchGame

class Bristol:

    @property
    def state(self):
        return self.game.engine.state

    @property
    def world(self):
        return self.game.engine.world

    @property
    def textures(self):
        return self.game.engine.textures

    @property
    def engine(self):
        return self.game.engine

    def get_cell(self, *args, **kwargs):
        return self.game.engine.get_cell(*args, **kwargs)

    def del_cell(self, *args, **kwargs):
        return self.game.engine.del_cell(*args, **kwargs)

    def set_cell(self, *args, **kwargs):
        return self.game.engine.set_cell(*args, **kwargs)

    def tick_handler(self, engine, rt, ticks):
        self.ticks = ticks

    def __init__(self):
        self.ticks = 0
        self.game = BirchGame('birch/examples/bristol/assets')
        self.game.register_tick_handler(self.tick_handler)
        #self.game.register_seed_handler(self.seed_handler)
        #self.game.register_mouse_handler(self.mouse_handler)
        #self.game.register_mouse_press_handler(self.mouse_press_handler)
        #self.game.register_map_click_handler(self.map_click_handler)
        self.game.camera_controlled = False
        self.game.player_controlled = True
        self.game.set_player('player')

    def run(self):
        self.game.run()

if __name__ == '__main__':
    bristol = Bristol()
    bristol.run()
