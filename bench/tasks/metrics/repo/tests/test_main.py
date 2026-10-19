import unittest

from exporter import main


class RenderTest(unittest.TestCase):
    def test_every_metric_has_the_service_label(self):
        lines = [line for line in main.render().splitlines() if not line.startswith("#")]
        self.assertEqual(len(lines), 3)
        for line in lines:
            self.assertIn('service="shop"', line)


if __name__ == "__main__":
    unittest.main()
