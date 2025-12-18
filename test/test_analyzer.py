import unittest
from src.utils import ip_to_int

class TestUtils(unittest.TestCase):
    def test_ip_to_int(self):
        self.assertEqual(ip_to_int("192.168.1.1"), 192168001001)
        self.assertEqual(ip_to_int("10.0.0.5"), 100000005)
        self.assertEqual(ip_to_int(""), 0)

if __name__ == "__main__":
    unittest.main()
