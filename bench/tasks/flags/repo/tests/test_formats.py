import unittest

from formats import classic, modern

ORDER = {"id": "A-7", "lines": [{"name": "Mug", "qty": 2, "cents": 799}]}


class LayoutTest(unittest.TestCase):
    def test_classic_total(self):
        self.assertIn("TOTAL 15.98", classic.render(ORDER))

    def test_modern_subtotal(self):
        self.assertIn("Subtotal: 15.98", modern.render(ORDER))


if __name__ == "__main__":
    unittest.main()
