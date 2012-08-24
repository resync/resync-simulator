import unittest
import StringIO
from resync.resource import Resource
from resync.inventory import Inventory
from resync.sitemap import Sitemap, SitemapIndexError

class TestSitemapCapabilities(unittest.TestCase):

    def test_01_print(self):
        i = Inventory()
        i.add( Resource(uri='a',lastmod='2001-01-01',size=1234) )
        i.capabilities['http://example.org/changeset1'] = \
            {"type": "changeset", "attributes": ["self next"]}
        self.assertEqual( len(i.capabilities), 1 )
        self.assertEqual( Sitemap().resources_as_xml(i, capabilities=i.capabilities), '<?xml version=\'1.0\' encoding=\'UTF-8\'?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:rs="http://www.openarchives.org/rs/terms/" xmlns:xhtml="http://www.w3.org/1999/xhtml_DEFANGED"><xhtml:link href="http://example.org/changeset1" rel="self next" type="changeset" /><url><loc>a</loc><lastmod>2001-01-01T00:00:00Z</lastmod><rs:size>1234</rs:size></url></urlset>' )

if  __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSitemapCapabilities)
    unittest.TextTestRunner(verbosity=2).run(suite)
