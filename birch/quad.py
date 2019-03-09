from uuid import uuid4
from pygame import Rect
from birch.exceptions import *

class Quad:

    def __init__(self, rect, threshold=32, max_items=16, process_rects=True,
            meta=None):
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
        self._id = uuid4()
        if meta is None:
            self.meta = {}
        else:
            self.meta = meta

    @property
    def id(self):
        return str(self._id.hex[-8:])

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

    def set_meta(self, key, val):
        self.meta[key] = val

    def del_meta(self, key, val):
        del(self.meta[key])

    def meta_is(self, key):
        return key in self.meta and self.meta[key]

    def meta_not(self, key):
        return key not in self.meta or not self.meta[key]

    def point_outside(self, point):
        return point[0] < self.topleft[0] or point[1] < self.topleft[1] or \
            point[0] > self.bottomright[0] or point[1] > self.bottomright[1]

    def rect_outside(self, rect):
        return self.point_outside(rect.topleft) or self.point_outside(rect.bottomright)

    def grow(self, point):
        newindex = 0
        tl = [self.rect.left, self.rect.top]
        if point[0] < self.rect.topleft[0]:
            tl[0] = self.rect.topleft[0] - self.rect.width
            newindex += 1
        elif point[0] > self.rect.bottomright[0]:
            tl[0] = self.rect.topleft[1] + self.rect.width

        if point[1] < self.rect.topleft[1]:
            tl[1] = self.rect.topleft[1] - self.rect.height
            newindex += 2
        elif point[1] > self.rect.bottomright[1]:
            tl[1] = self.rect.topleft[1] + self.rect.height

        if tl == self.rect.topleft:
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
                    Quad(Rect(offset[0], offset[1], self.rect.width, self.rect.height),
                        meta={}))
        return newquad

    def dump(self, prefixlen=0):
        print(' ' * prefixlen, 'Quad (%s)' % str(self.id), self._rect_points(self.rect), self.halves)
        print(' ' * (prefixlen + 2), 'meta:')
        for k in self.meta:
            print(' ' * (prefixlen + 4), '%s:' % k, self.meta[k])
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

    def item_outside(self, item):
        return self.point_outside(item.rect.topleft) and \
            self.point_outside(item.rect.topright) and \
            self.point_outside(item.rect.bottomleft) and \
            self.point_outside(item.rect.bottomright)

    def _check_item(self, item):
        if not hasattr(item, 'rect'):
            raise MalformedQuadTreeItemException(item)
        elif self.item_outside(item):
            raise OutOfBoundsException(item.rect, self.rect)

    def remove(self, item):
        self._check_item(item)
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
                devomer = self.quarters[index].remove(item)
                removed = devomer or removed
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
        try:
            print(self.id, 'insert', self.rect, item.name, item.rect)
            self._check_item(item)
            maxed = len(self.items) >= self.max_items and self.rect.width > self.threshold
            if not maxed and self.leaf:
                self.items.append(item)
                return
            elif maxed and self.leaf:
                self.split()
            self.subinsert(item)
        except OutOfBoundsException as e:
            self.dump()
            raise e

    def pos_quarter(self, pos):
        right = pos[0] >= self.halves[0]
        bottom = pos[1] >= self.halves[1]
        index = int(right) + int(bottom) * 2
        return index

    def subinsert(self, item):
        self._check_item(item)
        ri = self.rect_indices(item.rect)
        #print('me', self._rect_points(self.rect), 'item insert', item.rect, ri)
        for index in ri:
            self.quarters[index].insert(item)

    def split(self, copy_meta=True, existing=None):
        newmeta = {}
        if copy_meta:
            newmeta = self.meta
        if self.leaf:
            wh = [self.rect.width / 2, self.rect.height / 2]
            rects = [
                Rect(self.rect[0], self.rect[1],
                    wh[0], wh[1]),
                Rect(self.halves[0], self.rect[1],
                    wh[0], wh[1]),
                Rect(self.rect[0], self.halves[1],
                    wh[0], wh[1]),
                Rect(self.halves[0], self.halves[1],
                    wh[0], wh[1]),
            ]
            self.quarters = []
            for rect in rects:
                if existing is not None and rect == existing.rect:
                    self.quarters.append(existing)
                else:
                    self.quarters.append(Quad(rect, meta=dict(newmeta)))
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
        return r1.colliderect(r2)

    def get(self, rect):
        if not self.leaf:
            indices = self.rect_indices(rect)
            results = []
            for i in indices:
                results = results + self.quarters[i].get(rect)
            uniq = []
            for result in results:
                if result not in uniq:
                    uniq.append(result)
            return uniq

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
