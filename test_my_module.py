"""module: unit test for my_module.py"""
import unittest

from my_module import square, double, add

class TestSquare(unittest.TestCase):
    """Unit Test for my_module"""
    def test_square(self):
        """Test square function"""
        self.assertEqual(square(2),4)
        self.assertEqual(square(3.0),9.0)
        self.assertNotEqual(square(-3),-9)

class TestDouble(unittest.TestCase):
    """Unit Test for my_module"""
    def test_double(self):
        """Test double function"""
        self.assertEqual(double(2),4)
        self.assertEqual(double(-3.1),-6.2)
        self.assertEqual(double(0),0)

class TestAdd(unittest.TestCase):
    """Unit Test for my_module"""
    def test_add(self):
        """Test add function"""
        self.assertEqual(add(2, 5),7)
        self.assertEqual(add(-3.1, 3.1),0)
        self.assertEqual(add('hello ', 'world'),'hello world')

unittest.main()
