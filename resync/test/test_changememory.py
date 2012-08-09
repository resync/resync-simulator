import unittest
import random

from resync.resource import Resource
from resync.source import Source
from resync.changememory import DynamicChangeSet
from resync.change import ChangeEvent

class TestSource(unittest.TestCase):

    def setUp(self):
        """Set up a new changememory before each test case"""
        source = Source(None, "localhost", "8888")
        config = {}
        config['uri_path'] = "changes"
        config['max_changes'] = 100
        self.changememory = DynamicChangeSet(source, config)

    def test_init(self):
        """Test if construction works"""
        self.assertTrue(self.changememory is not None)
        self.assertTrue(self.changememory.config is not None)
        self.assertEqual(self.changememory.uri_path, "changes")
        self.assertEqual(self.changememory.max_changes, 100)
        self.assertTrue(self.changememory.source is not None)
        self.assertEqual(self.changememory.first_change_id, 0)
        self.assertEqual(self.changememory.latest_change_id, 0)
            
    def test_base_uri(self):
        """Test if the the changememory base uri is minted correctly"""
        self.assertEqual(self.changememory.base_uri,
                            "http://localhost:8888/changes")

    def test_current_changeset_uri(self):
        """Tests construction of current changeset URI"""
        self.assertEqual(self.changememory.current_changeset_uri(),
                            "http://localhost:8888/changes/from/0")
        self.create_dummy_changes(5)
        self.assertEqual(self.changememory.current_changeset_uri(),
                            "http://localhost:8888/changes/from/0")
        self.assertEqual(self.changememory.current_changeset_uri(15),
                            "http://localhost:8888/changes/from/15")
    
    def test_next_changeset_uri(self):
        """Tests construction of next changeset URI"""
        self.assertEqual(self.changememory.next_changeset_uri(),
                            "http://localhost:8888/changes/from/1")
        self.create_dummy_changes(5)
        self.assertEqual(self.changememory.latest_change_id, 5)
        self.assertEqual(self.changememory.next_changeset_uri(),
                            "http://localhost:8888/changes/from/6")
    
    def test_change_count(self):
        """Test if change counting works"""
        self.assertEqual(self.changememory.change_count, 0)
        self.create_dummy_changes()
        self.assertEqual(self.changememory.change_count, 5)
        
    def test_changes(self):
        """Test if changes are returned in the correct order"""
        self.create_dummy_changes(50)
        for i in range(self.changememory.change_count):
            change = self.changememory.changes[i]
            self.assertEqual(change.changeid, i+1)
        
    def test_changes_with_limits(self):
        """Test if the change ids are correct when change memory is limited"""
        self.changememory.max_changes = 50
        self.create_dummy_changes(50)
        self.assertEqual(self.changememory.change_count, 50)
        self.assertEqual(self.changememory.changes[0].changeid, 1)
        self.assertEqual(self.changememory.changes[49].changeid, 50)
        self.create_dummy_changes(50)
        self.assertEqual(self.changememory.change_count, 50)
        self.assertEqual(self.changememory.changes[0].changeid, 51)
        self.assertEqual(self.changememory.changes[49].changeid, 100)
        self.create_dummy_changes(16)
        self.assertEqual(self.changememory.change_count, 50)
        self.assertEqual(self.changememory.changes[0].changeid, 67)
        self.assertEqual(self.changememory.changes[49].changeid, 116)
        
    def test_changes_from(self):
        """Tests if the correct changes subsets are retrieved """
        self.create_dummy_changes(50)
        self.assertEqual(len(self.changememory.changes_from(5)), 46)
        self.assertEqual(len(self.changememory.changes_from(67)), 0)
    
    def create_dummy_changes(self, number = 5):
        """Create a given number of dummy changes"""
        for i in range(number):
            r = Resource(uri="a"+str(i), timestamp=1234.0*i) 
            ce = ChangeEvent(random.choice(['create', 'update', 'delete']), r)
            self.changememory.notify(ce)
    
if __name__ == '__main__':
    unittest.main()