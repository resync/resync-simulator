import unittest
import re
from resync.resource import Resource
from resync.resource_file import ResourceFile

class TestResourceFile(unittest.TestCase):

    def test1_create(self):
        r = Resource('a', timestamp=1234)
        rf = ResourceFile( resource=r )
        self.assertEqual( rf.uri, 'a' )
        self.assertEqual( rf.timestamp, 1234)
        # So far these turn out equal
        self.assertEqual( r, rf )
        #py2.7: self.assertRegexpMatches( str(rf), r"\[a | 1969" )
        self.assertTrue( re.match( r"\[a | 1969", str(rf) ) )

    def test2_create_with_file(self):
        r = Resource( 'a', timestamp=1234)
        rf = ResourceFile( resource=r, file='/tmp/a' )
        self.assertEqual( rf.file, '/tmp/a' )
        # So far these still turn out equal
        self.assertEqual( r, rf )

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestResourceFile)
    unittest.TextTestRunner(verbosity=2).run(suite)
