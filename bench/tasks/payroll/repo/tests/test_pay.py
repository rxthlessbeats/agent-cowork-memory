import unittest

import payroll


class PayTest(unittest.TestCase):
    def test_straight_time(self):
        self.assertEqual(payroll.pay(37.5, 20), 750)

    def test_no_hours(self):
        self.assertEqual(payroll.pay(0, 18.5), 0)


if __name__ == "__main__":
    unittest.main()
