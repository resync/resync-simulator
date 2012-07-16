import unittest
import re
from resync.resource import Resource
from resync.resource_change import ResourceChange

class TestResourceChange(unittest.TestCase):

    def test1_create(self):
        r = Resource('a', timestamp=1234)
        rc = ResourceChange( resource=r )
        self.assertEqual( rc.uri, 'a' )
        self.assertEqual( rc.timestamp, 1234)
        # So far these turn out equal
        self.assertEqual( r, rc )
        self.assertTrue( re.match( r"\[a | 1969",str(rc) ) )

    def test2_create_with_change(self):
        r = Resource( 'a', timestamp=1234)
        rc = ResourceChange( resource=r, changeid=89, changetype='UP' )
        self.assertEqual( rc.changeid, 89 )
        self.assertEqual( rc.changetype, 'UP' )
        # So far these still turn out equal
        self.assertEqual( r, rc )

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase()
    unittest.TextTestRunner(verbosity=2).run(suite)
