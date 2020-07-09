import unittest
from cographs import utilities


class TestUtilities(unittest.TestCase):
    def test_pick(self):
        element = "elem"
        a_set = {element}
        self.assertEqual(utilities.pick(a_set), element)


if __name__ == "__main__":
    unittest.main()
