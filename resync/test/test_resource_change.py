import unittest
from resync.resource import Resource
from resync.resource_change import ResourceChange

class TestResource(unittest.TestCase):

    def test1_create(self):
        r = Resource('a', timestamp=1234)
        rc = ResourceChange( r )
        self.assertEqual( rc.uri, 'a' )
        self.assertEqual( rc.timestamp, 1234)
        # So far these turn out equal
        self.assertEqual( r, rc )

    def test2_create_with_change(self):
        r = Resource('a', timestamp=1234)
        rc = ResourceChange( r, changeid=89, changetype='UP' )
        self.assertEqual( rc.changeid, 89 )
        self.assertEqual( rc.changetype, 'UP' )
        # So far these still turn out equal
        self.assertEqual( r, rc )

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestClientResource)
    unittest.TextTestRunner(verbosity=2).run(suite)
