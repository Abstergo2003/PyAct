import unittest
from pamd_helpers.unit import Unit

class TestUnitOperations(unittest.TestCase):
    def setUp(self):
        self.u1 = Unit(10.0, "[m]")
        self.u2 = Unit(5.0, "[s]")
        self.scalar = 2.0

    def test_addition(self):
        # Unit + Unit
        self.assertEqual(self.u1 + self.u2, 15.0)
        # Unit + Scalar
        self.assertEqual(self.u1 + self.scalar, 12.0)
        # Scalar + Unit (radd)
        self.assertEqual(self.scalar + self.u1, 12.0)

    def test_subtraction(self):
        # Unit - Unit
        self.assertEqual(self.u1 - self.u2, 5.0)
        # Unit - Scalar
        self.assertEqual(self.u1 - self.scalar, 8.0)
        # Scalar - Unit (rsub)
        self.assertEqual(self.scalar - self.u1, -8.0)

    def test_multiplication(self):
        # Unit * Unit
        self.assertEqual(self.u1 * self.u2, 50.0)
        # Unit * Scalar
        self.assertEqual(self.u1 * self.scalar, 20.0)
        # Scalar * Unit (rmul)
        self.assertEqual(self.scalar * self.u1, 20.0)

    def test_division(self):
        # Unit / Unit
        self.assertEqual(self.u1 / self.u2, 2.0)
        # Unit / Scalar
        self.assertEqual(self.u1 / self.scalar, 5.0)
        # Scalar / Unit (rtruediv)
        self.assertEqual(self.scalar / self.u1, 0.2)

    def test_power(self):
        # Unit ** Scalar
        self.assertEqual(self.u1 ** self.scalar, 100.0)
        # Unit ** Unit
        self.assertEqual(self.u1 ** self.u2, 100000.0)

    def test_negation_and_abs(self):
        u_neg = -self.u1
        self.assertEqual(u_neg, -10.0)
        self.assertEqual(abs(Unit(-15.5, "[kg]")), 15.5)

    def test_types(self):
        # Ensure that the result is strictly a float, not a Unit object
        result = self.u1 * self.u2
        self.assertIsInstance(result, float)
        self.assertNotIsInstance(result, Unit)

if __name__ == '__main__':
    unittest.main()
