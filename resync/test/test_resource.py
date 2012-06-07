import unittest
from resync.resource import Resource

class TestResource(unittest.TestCase):

    def test1a_same(self):
        r1 = Resource('a')
        r2 = Resource('a')
        #print 'r1 == r2 : '+str(r1==r2)
        self.assertEqual( r1, r1 )
        self.assertEqual( r1, r2 )

    def test1b_same(self):
        r1 = Resource(uri='a',timestamp=1234.0)
        r2 = Resource(uri='a',timestamp=1234.0)
        #print 'r1 == r2 : '+str(r1==r2)
        self.assertEqual( r1, r1 )
        self.assertEqual( r1, r2 )

    def test1c_same(self):
        """Same with lastmod instead of direct timestamp"""
        r1 = Resource('a')
        r1.lastmod='2012-01-02'
        r2 = Resource('a')
        r2.lastmod='2012-01-02T00:00:00'
        r3 = Resource('a')
        r3.lastmod='2012-01-02T00:00:00.00'
        self.assertEqual( r1.timestamp, r2.timestamp )
        self.assertEqual( r1.timestamp, r3.timestamp )
        self.assertEqual( r1, r1 )
        self.assertEqual( r1, r2 )
        self.assertEqual( r1, r3 )

    def test1d_same(self):
        """Same with slight timestamp diff"""
        r1 = Resource('a')
        r1.lastmod='2012-01-02T01:02:03'
        r2 = Resource('a')
        r2.lastmod='2012-01-02T01:02:03.99'
        self.assertNotEqual( r1.timestamp, r2.timestamp )
        self.assertEqual( r1, r2 )

    def test2a_diff(self):
        r1 = Resource('a')
        r2 = Resource('b')
        self.assertNotEqual(r1,r2)

    def test2b_diff(self):
        r1 = Resource('a','2012-01-11')
        r2 = Resource('a','2012-01-22')
        #print 'r1 == r2 : '+str(r1==r2)
        self.assertNotEqual( r1, r2 )

    def test4_bad_lastmod(self):
        def setlastmod(r,v):
            r.lastmod=v
        r = Resource('4')
        self.assertRaises( ValueError, setlastmod, r, "bad_lastmod" )
        self.assertRaises( ValueError, setlastmod, r, "" )
        self.assertRaises( ValueError, setlastmod, r, "2012-13-01" )
        self.assertRaises( ValueError, setlastmod, r, "2012-12-32" )
        self.assertRaises( ValueError, setlastmod, r, "2012-11-01T10:10" )
        self.assertRaises( ValueError, setlastmod, r, "2012-11-01T10:10:60" )
        self.assertRaises( ValueError, setlastmod, r, "2012-11-01T10:10:59.9x" )

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestClientResource)
    unittest.TextTestRunner(verbosity=2).run(suite)
