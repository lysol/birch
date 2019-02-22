from cells.cell import Cell
from random import randint

class Tree(Cell):

    def __init__(self, texture_name, textures, position):
        super().__init__(texture_name, textures, position)

class PineTree(Tree):

    def __init__(self, textures, position):
        super().__init__("pine_tree", textures, position)
