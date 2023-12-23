"""generate unit test for py_lint_code.py"""
import unittest

from py_lint_code import add

class TestMyModule(unittest.TestCase):
    """test the add function

    Args:
        unittest (_type_): _description_
    """
    def test_add(self):
        # Assert equal(actual value, expected value)
        self.assertEqual(add(1, 2), 3)

if __name__ == '__main__':
    unittest.main()