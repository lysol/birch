from shapely.geometry import Polygon
from pygame import Rect
from exceptions import *

class Quad:

    def __init__(self, rect, threshold=32, max_items=16, process_rects=True):
        self.threshold = threshold
        self.max_items = max_items
        self.process_rects = process_rects
        self.rect = rect
        self.halves = [
            self.rect.width / 2 + self.rect[0],
            self.rect.height / 2 + self.rect[1]
            ]
        self.items = []
        self.quarters = []

    @property
    def leaf(self):
        return len(self.quarters) == 0

    @property
    def topleft(self):
        return self.rect.topleft

    @property
    def topright(self):
        return self.rect.topright

    @property
    def bottomleft(self):
        return self.rect.bottomleft

    @property
    def bottomright(self):
        return self.rect.bottomright

    @property
    def width(self):
        return self.rect.width

    @property
    def height(self):
        return self.rect.height

    def point_outside(self, point):
        return point[0] < self.topleft[0] or point[1] < self.topleft[1] or \
            point[0] > self.bottomright[0] or point[1] > self.bottomright[1]

    def rect_outside(self, rect):
        return self.point_outside(rect.topleft) or self.point_outside(rect.bottomright)

    def grow(self, point):
        newindex = 0
        tl = [None, None]
        if point[0] < self.rect.topleft[0]:
            tl[0] = self.rect.topleft[0] - self.rect.width
            newindex += 1
        elif point[0] > self.rect.bottomright[0]:
            tl[0] = self.rect.topleft[1] + self.rect.width
        else:
            raise GrowPointException(point, self.rect)
        if point[1] < self.rect.topleft[1]:
            tl[1] = self.rect.topleft[1] - self.rect.height
            newindex += 2
        elif point[1] > self.rect.bottomright[1]:
            tl[1] = self.rect.topleft[1] + self.rect.height
        else:
            raise GrowPointException(point, self.rect)

        newquad = Quad(Rect(tl[0], tl[1], self.rect.width * 2, self.rect.height * 2))

        for i in range(4):
            if i == newindex:
                newquad.quarters.append(self)
            else:
                left = i == 0 or i == 2
                top = i == 0 or i == 1
                offset = [
                    tl[0] + self.rect.width * int(not left),
                    tl[1] + self.rect.height * int(not top)
                    ]
                newquad.quarters.append(
                    Quad(Rect(offset[0], offset[1], self.rect.width, self.rect.height)))
        return newquad

    def dump(self, prefixlen=0):
        print(' ' * prefixlen, 'Quad', self._rect_points(self.rect), self.halves)
        if self.leaf and len(self.items) > 0:
            print(' ' * (prefixlen + 2), 'items:')
            for item in self.items:
                collide = self.rect.colliderect(item.rect)
                print(' ' * (prefixlen + 4), item.name, 'Collides: %s' % bool(collide),
                        self._rect_points(item.rect))
        if not self.leaf:
            print(' ' * (prefixlen + 2), 'quarters:')
            for i, q in enumerate(self.quarters):
                q.dump(prefixlen=4 + prefixlen)

    def check_item(self, item):
        atleastone = not self.point_outside(item.rect.topleft) or \
            not self.point_outside(item.rect.topright) or \
            not self.point_outside(item.rect.bottomleft) or \
            not self.point_outside(item.rect.bottomright)
        if not hasattr(item, 'rect'):
            raise MalformedQuadTreeItemException(item)
        elif not atleastone:
            raise OutOfBoundsException(item.rect, self.rect)

    def remove(self, item):
        self.check_item(item)
        if self.leaf:
            if item in self.items:
                self.items.remove(item)
                return True
            removed = item.id in list(map(lambda tem: tem.id == item.id, self.items))
            if removed:
                self.items = list(filter(lambda tem: tem.id != item.id, self.items))
            return removed
        else:
            removed = False
            for index in self.rect_indices(item.rect):
                removed = removed or self.quarters[index].remove_item(item)
            return removed

    def remove_rect(self, rect):
        items = self.get(rect)
        for item in items:
            self.remove(item)

    def remove_rect(self, rect, comparator):
        if not self.leaf:
            indices = set(map(lambda xy: self.pos_quarter(xy),
                [rect.topleft, rect.topright, rect.bottomleft, rect.bottomright]))
            removed = []
            for i in indices:
                removed = removed + self.quarters[i].remove(rect, comparator)
            return removed
        removed = []
        newitems = []
        for item in self.items:
            if comparator(item):
                removed.append(item)
            else:
                newitems.append(item)
        self.items = newitems
        return removed

    def insert(self, item):
        self.check_item(item)
        maxed = len(self.items) >= self.max_items and self.rect.width > self.threshold
        if not maxed and self.leaf:
            self.items.append(item)
            return
        elif maxed and self.leaf:
            self.split()
        self.subinsert(item)

    def pos_quarter(self, pos):
        right = pos[0] >= self.halves[0]
        bottom = pos[1] >= self.halves[1]
        index = int(right) + int(bottom) * 2
        return index

    def subinsert(self, item):
        self.check_item(item)
        ri = self.rect_indices(item.rect)
        #print('me', self._rect_points(self.rect), 'item insert', item.rect, ri)
        for index in ri:
            self.quarters[index].insert(item)

    def split(self):
        if self.leaf:
            wh = [self.rect.width / 2, self.rect.height / 2]
            self.quarters = [
                Quad(Rect(self.rect[0], self.rect[1],
                    wh[0], wh[1])),
                Quad(Rect(self.halves[0], self.rect[1],
                    wh[0], wh[1])),
                Quad(Rect(self.rect[0], self.halves[1],
                    wh[0], wh[1])),
                Quad(Rect(self.halves[0], self.halves[1],
                    wh[0], wh[1]))
                ]
        for item in self.items:
            self.subinsert(item)
        self.items = []

    def _rect_points(self, rect):
        return (rect.topleft, rect.topright, rect.bottomleft, rect.bottomright)

    def rect_indices(self, rect):
        return set(map(lambda xy: self.pos_quarter(xy), self._rect_points(rect)))

    def _pgte(self, p1, p2):
        return p1[0] >= p2[0] and p1[1] >= p2[1]

    def _plte(self, p1, p2):
        return p1[0] <= p2[0] and p1[1] <= p2[1]

    def _intersect(self, r1, r2):
        ri1 = Polygon(self._rect_points(r1))
        ri2 = Polygon(self._rect_points(r2))
        return ri1.intersects(ri2)

    def get(self, rect):
        if not self.leaf:
            indices = self.rect_indices(rect)
            results = []
            for i in indices:
                results = results + self.quarters[i].get(rect)
            return results

        #results = list(filter(lambda p: rect.colliderect(p.rect), self.items))
        results = list(filter(lambda p: self._intersect(rect, p.rect), self.items))
        unique = []
        for item in results:
            if item in unique:
                continue
            for uitem in unique:
                if hasattr(uitem, 'id') and hasattr(item, 'id') and uitem.id == item.id:
                    continue
            unique.append(item)
        return unique
