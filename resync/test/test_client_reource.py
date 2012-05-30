import unittest
from resync.client_resource import ClientResource

class TestClientResource(unittest.TestCase):

    def test1a_same(self):
        r1 = ClientResource('a')
        r2 = ClientResource('a')
        #print 'r1 == r2 : '+str(r1==r2)
        self.assertEqual( r1, r1 )
        self.assertEqual( r1, r2 )

    def test1b_same(self):
        r1 = ClientResource(uri='a',timestamp=1234.0)
        r2 = ClientResource(uri='a',timestamp=1234.0)
        #print 'r1 == r2 : '+str(r1==r2)
        self.assertEqual( r1, r1 )
        self.assertEqual( r1, r2 )

    def test1c_same(self):
        """Same with lastmod instead of direct timestamp"""
        r1 = ClientResource('a')
        r1.set_lastmod('2012-01-02')
        r2 = ClientResource('a')
        r2.set_lastmod('2012-01-02T00:00:00')
        r3 = ClientResource('a')
        r3.set_lastmod('2012-01-02T00:00:00.00')
        self.assertEqual( r1.timestamp, r2.timestamp )
        self.assertEqual( r1.timestamp, r3.timestamp )
        self.assertEqual( r1, r1 )
        self.assertEqual( r1, r2 )
        self.assertEqual( r1, r3 )

    def test1d_same(self):
        """Same with slight timestamp diff"""
        r1 = ClientResource('a')
        r1.set_lastmod('2012-01-02T01:02:03')
        r2 = ClientResource('a')
        r2.set_lastmod('2012-01-02T01:02:03.99')
        self.assertNotEqual( r1.timestamp, r2.timestamp )
        self.assertEqual( r1, r2 )

    def test2a_diff(self):
        r1 = ClientResource('a')
        r2 = ClientResource('b')
        self.assertNotEqual(r1,r2)

    def test2b_diff(self):
        r1 = ClientResource('a','2012-01-11')
        r2 = ClientResource('a','2012-01-22')
        #print 'r1 == r2 : '+str(r1==r2)
        self.assertNotEqual( r1, r2 )

    def test3a_str(self):
        r1 = ClientResource('a3')
        r1.set_lastmod('2012-01-11T01:02:03')
        self.assertEqual( str(r1), "<?xml version='1.0' encoding='UTF-8'?>\n<url><loc>a3</loc><lastmod>2012-01-11T01:02:03</lastmod></url>" )

    def test3b_str(self):
        r1 = ClientResource('3b',1234.1,9999,'ab54de')
        self.assertEqual( str(r1), "<?xml version='1.0' encoding='UTF-8'?>\n<url><loc>3b</loc><lastmod>1969-12-31T19:20:34.100000</lastmod><rs:size>9999</rs:size><rs:md5>ab54de</rs:md5></url>" )

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestClientResource)
    unittest.TextTestRunner(verbosity=2).run(suite)
