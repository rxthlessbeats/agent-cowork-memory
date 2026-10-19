import unittest

import mailer


class BuildTest(unittest.TestCase):
    def test_to_and_subject(self):
        headers = mailer.build("ann@example.com", "Your order")
        self.assertEqual(headers["To"], "ann@example.com")
        self.assertEqual(headers["Subject"], "Your order")


if __name__ == "__main__":
    unittest.main()
