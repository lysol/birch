
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

class QuadAlreadySeededException(Exception):
    def __init__(self, quad):
        itemso = list(filter(lambda x: quad.rect.collidepoint(x.topleft), quad.items))
        messages = ['This quad has already been seeded:', quad.id, quad.rect, quad.meta]
        messages.append(str(list(map(lambda x: '    %s %d, %d, %d, %d' % (
                x.name, x.rect.left, x.rect.top, x.rect.width, x.rect.height),
                itemso))))
        super().__init__(messages)

class MalformedQuadException(Exception):
    def __init__(self, newrect, existingrect):
        message = 'Grow operation generated an illegally dimensioned quadtree. New top level quad rect:', newrect, 'Existing rect:', existingrect
        super().__init__(message)
