import unittest
from randomart.formats import ra_constant


class RaConstantTestCase(unittest.TestCase):
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

    def test_persist(self):
        inst = ra_constant(0.10, 0.20, 0.30)
        for x, y in self.locations:
            out = inst(x, y)
            self.assertAlmostEqual(out.r, 0.10)
            self.assertAlmostEqual(out.g, 0.20)
            self.assertAlmostEqual(out.b, 0.30)
