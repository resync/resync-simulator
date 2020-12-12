import unittest
import random

from simulator.resource import Resource
from simulator.changememory import DynamicChangeList
from simulator.source import Source


class TestSource(unittest.TestCase):

    def setUp(self):
        """Set up a new changememory before each test case"""
        source = Source(None, "http://localhost:8888", "8888")
        config = {}
        config['uri_path'] = "changes"
        config['max_changes'] = 100
        self.changememory = DynamicChangeList(source, config)

    def test_init(self):
        """Test if construction works"""
        self.assertTrue(self.changememory is not None)
        self.assertTrue(self.changememory.config is not None)
        self.assertEqual(self.changememory.uri_path, "changes")
        self.assertEqual(self.changememory.max_changes, 100)
        self.assertTrue(self.changememory.source is not None)

    def test_base_uri(self):
        """Test if the the changememory base uri is minted correctly"""
        self.assertEqual(self.changememory.base_uri,
                         "http://localhost:8888/changes")

    def test_change_count(self):
        """Test if change counting works"""
        self.assertEqual(self.changememory.change_count, 0)
        self.create_dummy_changes()
        self.assertEqual(self.changememory.change_count, 5)

    def test_changes(self):
        """Test correct changes stored in correct order"""
        self.create_dummy_changes(50)
        for i in range(0, 49):
            change = self.changememory.changes[i]
            self.assertEqual(change.length, i)

        self.assertEqual(len(self.changememory.changes), 50)

    def test_changes_with_limits(self):
        """Test if the change ids are correct when change memory is limited"""
        self.changememory.max_changes = 50
        self.create_dummy_changes(50)
        self.assertEqual(self.changememory.change_count, 50)
        self.assertEqual(self.changememory.changes[0].length, 0)
        self.assertEqual(self.changememory.changes[49].length, 49)
        self.create_dummy_changes(100)
        self.assertEqual(self.changememory.change_count, 50)
        self.assertEqual(self.changememory.changes[0].length, 50)
        self.assertEqual(self.changememory.changes[49].length, 99)
        self.create_dummy_changes(16)
        self.assertEqual(self.changememory.change_count, 50)
        self.assertEqual(self.changememory.changes[0].length, 66)
        self.assertEqual(self.changememory.changes[49].length, 15)

    def create_dummy_changes(self, number=5):
        """Create a given number of dummy changes, use length as a dummy id"""
        for i in range(number):
            r = Resource(uri="a" + str(i), timestamp=1234.0 * i,
                         change=random.choice(
                             ['created', 'updated', 'deleted']),
                         length=i)
            self.changememory.notify(r)


if __name__ == '__main__':
    unittest.main()
