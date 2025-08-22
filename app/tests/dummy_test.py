import unittest

class DummyTest(unittest.TestCase):
    def test_dummy(self):
        """Dummy test để Jenkins/PyCharm chạy thử"""
        self.assertEqual(1 + 1, 2)


if __name__ == '__main__':
    unittest.main()
