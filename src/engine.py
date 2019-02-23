from cells.rci import RCell, CCell, ICell
from cells.cell import Cell

class Engine:

    def __init__(self, state, textures):
        self.state = state
        self.ticks = 0
        self.textures = textures

    def tick(self):
        damage = False
        self.ticks += self.state["speed"]
        changed = []
        for row in self.state["cells"]:
            for cell in row:
                if cell.tick(self.ticks, self):
                    changed.append(cell)
        return changed

    def get_cell(self, x, y):
        return self.state["cells"][y][x]

    def set_cell(self, x, y, cell):
        self.state["cells"][y][x] = cell

    def use_tool(self, name, pos):
        cell = self.get_cell(*pos)
        if name == "bulldoze":
            if cell.name != "dirt":
                self.set_cell(pos[0], pos[1],
                    Cell("dirt", self.textures, pos))
        elif name == "r":
            if cell.name == "dirt":
                self.set_cell(pos[0], pos[1],
                    RCell(self.textures, pos))

        elif name == "c":
            if cell.name == "dirt":
                self.set_cell(pos[0], pos[1],
                    CCell(self.textures, pos))

        elif name == "i":
            if cell.name == "dirt":
                self.set_cell(pos[0], pos[1],
                    ICell(self.textures, pos))

