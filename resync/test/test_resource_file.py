import unittest
from resync.resource import Resource
from resync.resource_file import ResourceFile

class TestResource(unittest.TestCase):

    def test1_create(self):
        r = Resource('a', timestamp=1234)
        rf = ResourceFile( resource=r )
        self.assertEqual( rf.uri, 'a' )
        self.assertEqual( rf.timestamp, 1234)
        # So far these turn out equal
        self.assertEqual( r, rf )
        self.assertRegexpMatches( str(rf), r"\[a | 1969" )

    def test2_create_with_file(self):
        r = Resource( 'a', timestamp=1234)
        rf = ResourceFile( resource=r, file='/tmp/a' )
        self.assertEqual( rf.file, '/tmp/a' )
        # So far these still turn out equal
        self.assertEqual( r, rf )

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestClientResource)
    unittest.TextTestRunner(verbosity=2).run(suite)
