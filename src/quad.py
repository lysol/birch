from pygame import Rect

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

    def _rect_points(self, rect):
        return (rect.topleft, rect.topright, rect.bottomleft, rect.bottomright)

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
        if not hasattr(item, 'rect'):
            raise Exception('All Quadtree items must have a rect attribute')

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
        for index in self.rect_indices(item.rect):
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

    def rect_indices(self, rect):
        return set(map(lambda xy: self.pos_quarter(xy),
            [rect.topleft, rect.topright, rect.bottomleft, rect.bottomright]))

    def get(self, rect):
        if not self.leaf:
            indices = self.rect_indices(rect)
            results = []
            for i in indices:
                results = results + self.quarters[i].get(rect)
            return results

        results = list(filter(lambda p: rect.colliderect(p.rect), self.items))
        return results
