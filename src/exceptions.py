
class OutOfBoundsException(Exception):
    def __init__(self, point, rect):
        message = 'Point supplied is out of bounds for this quadtree', point, rect
        super().__init__(message)

class MalformedQuadTreeItemException(Exception):
    def __init__(self, item):
        message = 'Item missing rect property', item
        super().__init__(message)

class GrowPointException(Exception):
    def __init__(self, point, rect):
        message = 'Point supplied for grow operation lies within existing Quad', point, rect
        super().__init__(message)
