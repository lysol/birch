from pygame import Rect

class Quad:

    def __init__(self, rect, threshold=8, max_items=16):
        self.threshold = threshold
        self.max_items = max_items
        self.rect = rect
        self.halves = [
            self.rect.width / 2 + self.rect[0],
            self.rect.height / 2 + self.rect[1]
            ]
        self.items = []
        self.quarters = []

    def dump(self, prefixlen=0):
        print(' ' * prefixlen, 'Quad', self.rect, self.halves)
        if len(self.items) > 0:
            print(' ' * (prefixlen + 2), 'items:')
            for pos, item in self.items:
                print(' ' * (prefixlen + 4), pos, item)
        if len(self.quarters) > 0:
            print(' ' * (prefixlen + 2), 'quarters:')
            for i, q in enumerate(self.quarters):
                q.dump(prefixlen=4 + prefixlen)

    def insert(self, pos, item):
        maxed = len(self.items) >= self.max_items and self.rect.width > self.threshold
        if not maxed and len(self.quarters) == 0:
            self.items.append([pos, item])
            return
        elif maxed and len(self.quarters) == 0:
            self.split()
        self.subinsert(pos, item)

    def pos_quarter(self, pos):
        right = pos[0] >= self.halves[0]
        bottom = pos[1] >= self.halves[1]
        index = int(right) + int(bottom) * 2
        return index

    def subinsert(self, pos, item):
        self.quarters[self.pos_quarter(pos)].insert(pos, item)

    def split(self):
        if len(self.quarters) == 0:
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
        for pos, item in self.items:
            self.subinsert(pos, item)
        self.items = []

    def get(self, pos):
        if len(self.quarters) > 0:
            return self.quarters[self.pos_quarter(pos)].get(pos)
        result = []
        for ipos, item in self.items:
            if pos == ipos:
                result.append([ipos, item])
        return result

    def get_region(self, rect):
        if len(self.quarters) > 0:
            indices = set(map(lambda xy: self.pos_quarter(xy),
                [rect.topleft, rect.topright, rect.bottomleft, rect.bottomright]))
            results = []
            for i in indices:
                results = results + self.quarters[i].get_region(rect)
            return results

        results = list(filter(lambda p: rect.collidepoint(p[0]), self.items))
        return results
