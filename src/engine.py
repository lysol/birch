class Engine:

    def __init__(self, state):
        self.state = state
        self.ticks = 0

    def tick(self):
        self.ticks += self.state["speed"]
        for row in self.state["cells"]:
            for cell in row:
                cell.tick(self.ticks)
