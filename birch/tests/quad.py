import unittest
from random import randint
from pygame import Rect
from birch.quad import Quad

class TestItem:

    def __init__(self, name, rect):
        self.name = name
        self.rect = rect
        self.id = randint(0,1000000)

    def copy(self, rect):
        return TestItem(self.name, rect)


class QuadCase(unittest.TestCase):

    def setUp(self):
        self.quad = Quad(Rect(-128, -128, 256, 256),
            max_items=2)

    def tearDown(self):
        self.quad = None

    def test_basics(self):
        quad = self.quad
        self.assertEqual(type(quad), Quad)
        self.assertEqual(len(quad.halves), 2)
        self.assertEqual(quad.halves, [0, 0])
        self.assertEqual(quad.meta, {})

    def test_inserts(self):
        quad = self.quad
        item = TestItem('dirt', Rect(
            0, 0, 32, 32))
        item2 = item.copy(Rect(
            32, 32, 32, 32))
        quad.insert(item)
        self.assertEqual(quad.items, [item])
        quad.insert(item2)
        self.assertEqual(quad.items, [
            item, item2])

    def test_inserts(self):
        quad = self.quad
        items = []
        rects = [
            [0, 0, 32, 32],
            [32, 32, 32, 32],
            [64, 64, 32, 32],
            [32, 64, 32, 32]
            ]
        for rect in rects:
            items.append(TestItem('dirt', Rect(
                *rect)))
        for item in items:
            quad.insert(item)
        # should have split
        self.assertNotEqual(quad.items, items)
        self.assertEqual(len(quad.quarters), 4)
        self.assertEqual(quad.quarters[0].rect,
            Rect(-128, -128, 128, 128))
        self.assertEqual(quad.quarters[1].rect,
            Rect(0, -128, 128, 128))
        self.assertEqual(quad.quarters[2].rect,
            Rect(-128, 0, 128, 128))
        self.assertEqual(quad.quarters[3].rect,
            Rect(0, 0, 128, 128))

        newquad = quad.quarters[2]
        self.assertEqual(len(newquad.items), 0)

