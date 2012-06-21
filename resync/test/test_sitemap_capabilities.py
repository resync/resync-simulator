import unittest
import StringIO
from resync.resource import Resource
from resync.inventory import Inventory
from resync.sitemap import Sitemap, SitemapIndexError

class TestSitemap(unittest.TestCase):

    def test_01_print(self):
        i = Inventory()
        i.add( Resource(uri='a',lastmod='2001-01-01',size=1234) )
        i.capabilities['http://example.org/changeset1'] = \
            {"type": "changeset", "attributes": ["self next"]}
        self.assertEqual( len(i.capabilities), 1 )
        self.assertEqual( Sitemap().inventory_as_xml(i), '<?xml version=\'1.0\' encoding=\'UTF-8\'?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:rs="http://resourcesync.org/change/0.1"><atom:link href="http://example.org/changeset1" rel="self next" type="changeset" /><url><loc>a</loc><lastmod>2001-01-01T00:00:00</lastmod><rs:size>1234</rs:size></url></urlset>' )

if  __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(SitemapResource)
    unittest.TextTestRunner(verbosity=2).run(suite)
