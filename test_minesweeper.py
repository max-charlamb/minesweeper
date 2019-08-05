import unittest
from minesweeper import *
from termcolor import colored

class TestTileMethods(unittest.TestCase):


    def test_init(self):
        a = Tile(1)
        self.assertEqual(a.isBomb, False)
        self.assertEqual(a.neighboring, [])
        self.assertEqual(a.id, 1)
        self.assertEqual(a.mouse, False)
        self.assertEqual(a.flagged, False)
        self.assertEqual(a.hidden, True)

    def test_neighbors(self):
        a = Tile(1)
        b = Tile(2)
        c = Tile(3)
        arr = []
        for i in range(10):
            arr.append(Tile(i + 3))
        a.addNeighboring(b)
        self.assertEqual(a.getNeighboring(), [b])
        a.addNeighboring(arr)
        self.assertEqual(a.getNeighboring(), [b] + arr)
        a.neighboring = []
        self.assertEqual(a.getNeighboring(), [])

    def test_tile_to_string(self):
        a = Tile(1)
        self.assertEqual(str(a), '#')
        a.hidden = False
        a.numNeighboringBombs = 0
        self.assertEqual(str(a), colored(' ', 'cyan'))
        a.hidden = True
        a.flagged = True
        self.assertEqual(str(a), colored('F', 'red'))
        a.mouse = True
        self.assertEqual(str(a), colored('X', 'yellow'))
        a.mouse = False
        a.isBomb = True
        a.hidden = False
        a.flagged = False
        self.assertEqual(str(a), colored('B', 'magenta'))

    def test_show(self):
        a = Tile(1)
        b = Tile(2)
        self.assertEqual(a.hidden, True)
        a.numNeighboringBombs = 1
        self.assertEqual(a.show(), 0)
        b.numNeighboringBombs = 1
        b.isBomb = True
        self.assertEqual(b.show(), 1)


if __name__ == '__main__':
    unittest.main(verbosity=3)
