import sys
import unittest
import StringIO
from resync.resource import Resource
from resync.resource_change import ResourceChange
from resync.inventory import Inventory
from resync.sitemap import Sitemap, SitemapIndexError

class TestExamplesFromSpec(unittest.TestCase):

    def read_example(self,file,changeset=False):
        s = Sitemap()
        r = s.read('resync/test/testdata/examples_from_spec/'+file)
        self.assertEqual( s.changeset_read, changeset )
        return r

    def test_read_ex2_1(self):
        i = self.read_example('ex2_1.xml')
        self.assertEqual( len(i), 2 )
        sr = sorted(i.resources.keys())
        self.assertEqual( sr[0], 'http://example.com/res1' )
        self.assertEqual( sr[1], 'http://example.com/res2' )

    def test_read_ex2_3(self):
        i = self.read_example('ex2_3.xml')
        self.assertEqual( len(i), 2 )
        sr = sorted(i.resources.keys())
        self.assertEqual( sr[0], 'http://example.com/res1' )
        self.assertEqual( i.resources[sr[0]].lastmod, '2012-08-08T08:15:00Z' )
        self.assertEqual( sr[1], 'http://example.com/res2' )
        self.assertEqual( i.resources[sr[1]].lastmod, '2012-08-08T13:22:00Z' )
        # FIXME - do not yet parse <xhtml:meta> or <xhtml:link>

    def test_read_ex2_4(self):
        i = self.read_example('ex2_4.xml',changeset=True)
        self.assertEqual( len(i), 2 )
        r = i.resources
        self.assertEqual( r[0].uri, 'http://example.com/res1' )
        self.assertEqual( r[0].lastmod, '2012-08-08T08:15:00Z' )
        self.assertEqual( r[0].changetype, 'UPDATED' )
        self.assertEqual( r[1].uri, 'http://example.com/res2' )
        self.assertEqual( r[1].lastmod, '2012-08-08T13:22:00Z' )
        self.assertEqual( r[1].changetype, 'DELETED' )
        # FIXME - do not yet parse <xhtml:meta> or <xhtml:link>

    def test_read_ex3_4(self):
        i = self.read_example('ex3_4.xml')
        self.assertEqual( len(i), 2 )
        sr = sorted(i.resources.keys())
        self.assertEqual( sr[0], 'http://example.com/res1' )
        self.assertEqual( i.resources[sr[0]].lastmod, '2012-08-08T08:15:00Z' )
        self.assertEqual( sr[1], 'http://example.com/res2' )
        self.assertEqual( i.resources[sr[1]].lastmod, '2012-08-08T13:22:00Z' )
        # FIXME - do not yet parse <xhtml:meta> or <xhtml:link>
        # ???? - don't store changetype for inventory, not sure this makes sense

    def test_read_ex3_5(self):
        i = self.read_example('ex3_5.xml')
        self.assertEqual( len(i), 2 )
        sr = sorted(i.resources.keys())
        self.assertEqual( sr[0], 'http://example.com/res1' )
        self.assertEqual( i.resources[sr[0]].lastmod, '2012-08-08T08:15:00Z' )
        self.assertEqual( i.resources[sr[0]].md5, 'Q2hlY2sgSW50ZWdyaXR5IQ==' )
        self.assertEqual( sr[1], 'http://example.com/res2' )
        self.assertEqual( i.resources[sr[1]].lastmod, '2012-08-08T13:22:00Z' )
        self.assertEqual( i.resources[sr[1]].md5, 'A7kjY2sgSW50ZWdyaX6sgt==' )
        # FIXME - do not yet parse <xhtml:meta> or <xhtml:link>

    def test_read_ex3_6(self):
        i = self.read_example('ex3_6.xml')
        self.assertEqual( len(i), 2 )
        sr = sorted(i.resources.keys())
        self.assertEqual( sr[0], 'http://example.com/res1' )
        self.assertEqual( i.resources[sr[0]].lastmod, '2012-08-08T08:15:00Z' )
        self.assertEqual( i.resources[sr[0]].md5, 'Q2hlY2sgSW50ZWdyaXR5IQ==' )
        self.assertEqual( i.resources[sr[0]].size, 15672 )
        self.assertEqual( sr[1], 'http://example.com/res2' )
        self.assertEqual( i.resources[sr[1]].lastmod, '2012-08-08T13:22:00Z' )
        self.assertEqual( i.resources[sr[1]].md5, 'A7kjY2sgSW50ZWdyaX6sgt==' )
        self.assertEqual( i.resources[sr[1]].size, 93660664 )
        # FIXME - do not yet parse <xhtml:meta> or <xhtml:link>

if  __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestExamplesFromSpec)
    unittest.TextTestRunner(verbosity=2).run(suite)
