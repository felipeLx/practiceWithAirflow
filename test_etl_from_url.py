import unittest

from etl_from_url import load_to_db

class TestLoadToDB(unittest.TestCase):
    """Unit Test for my_module"""
    def test_load_to_db(self):
        """Test load_to_db function"""
        self.assertEqual(load_to_db(df, sql_connection, table_name),None)

unittest.main()
