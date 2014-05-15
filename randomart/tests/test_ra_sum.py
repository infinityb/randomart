import unittest
from randomart.formats import (
    ra_sum,
    ra_constant,
    ra_variable_x,
    ra_variable_y
)


class RaSumTestCase(unittest.TestCase):
    locations = [
        (0.646202, -0.289811),
        (-0.104839, -0.52361),
        (0.925392, -0.30059),
        (-0.455872, 0.545205),
        (0.58055, 0.34685),
        (-0.37949, -0.45593),
        (0.448511, 0.58542),
        (0.769115, -0.121607),
        (0.379993, 0.511257),
        (-0.756162, -0.12058)
    ]

    def test_0(self):
        inst = ra_sum(ra_variable_x(), ra_variable_y())
        for x, y in self.locations:
            tmp = inst(x, y)
            self.assertAlmostEqual(tmp.r, (x + y) / 2)
            self.assertAlmostEqual(tmp.g, (x + y) / 2)
            self.assertAlmostEqual(tmp.b, (x + y) / 2)

    def test_1(self):
        inst = ra_sum(ra_constant(0.1, 0.2, 0.3), ra_variable_y())
        for x, y in self.locations:
            tmp = inst(x, y)
            self.assertAlmostEqual(tmp.r, (0.1 + y) / 2)
            self.assertAlmostEqual(tmp.g, (0.2 + y) / 2)
            self.assertAlmostEqual(tmp.b, (0.3 + y) / 2)
