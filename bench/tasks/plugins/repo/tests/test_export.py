import json
import unittest

import export

ORDERS = [{"id": 1, "customer": "Ann", "total": "12.50"}]


class ExportTest(unittest.TestCase):
    def test_json(self):
        self.assertEqual(json.loads(export.export(ORDERS, "json")), ORDERS)

    def test_unknown_format(self):
        with self.assertRaises(KeyError):
            export.export(ORDERS, "xml")


if __name__ == "__main__":
    unittest.main()
