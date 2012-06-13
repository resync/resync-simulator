import unittest
import StringIO
from xml.etree.ElementTree import ParseError
from resync.resource import Resource
from resync.inventory import Inventory
from resync.sitemap import Sitemap, SitemapIndexError

class TestSitemap(unittest.TestCase):

    def test_01_resooure_str(self):
        r1 = Resource('a3')
        r1.lastmod='2012-01-11T01:02:03'
        self.assertEqual( Sitemap().resource_as_xml(r1), "<?xml version='1.0' encoding='UTF-8'?>\n<url><loc>a3</loc><lastmod>2012-01-11T01:02:03</lastmod></url>" )

    def test_02_resource_str(self):
        r1 = Resource('3b',1234.1,9999,'ab54de')
        self.assertEqual( Sitemap().resource_as_xml(r1), "<?xml version='1.0' encoding='UTF-8'?>\n<url><loc>3b</loc><lastmod>1969-12-31T19:20:34.100000</lastmod><rs:size>9999</rs:size><rs:md5>ab54de</rs:md5></url>" )

    def test_08_print(self):
        r1 = Resource(uri='a',lastmod='2001-01-01',size=1234)
        r2 = Resource(uri='b',lastmod='2002-02-02',size=56789)
        r3 = Resource(uri='c',lastmod='2003-03-03',size=0)
        m = Inventory()
        m.add(r1)
        m.add(r2)
        m.add(r3)
        #print m
        self.assertEqual( Sitemap().inventory_as_xml(m), "<?xml version='1.0' encoding='UTF-8'?>\n<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\" xmlns:rs=\"http://resourcesync.org/change/0.1\"><url><loc>a</loc><lastmod>2001-01-01T00:00:00</lastmod><rs:size>1234</rs:size></url><url><loc>b</loc><lastmod>2002-02-02T00:00:00</lastmod><rs:size>56789</rs:size></url><url><loc>c</loc><lastmod>2003-03-03T00:00:00</lastmod><rs:size>0</rs:size></url></urlset>")

    def test_09_print_subset(self): 
        r1 = Resource(uri='a',lastmod='2001-01-01',size=1234)
        r2 = Resource(uri='b',lastmod='2002-02-02',size=56789)
        r3 = Resource(uri='c',lastmod='2003-03-03',size=0)
        r3 = Resource(uri='d',lastmod='2003-03-04',size=444)
        m = Inventory()
        m.add(r1)
        m.add(r2)
        m.add(r3)
        self.assertEqual( Sitemap().inventory_as_xml(m, entries=['d','b']), "<?xml version='1.0' encoding='UTF-8'?>\n<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\" xmlns:rs=\"http://resourcesync.org/change/0.1\"><url><loc>d</loc><lastmod>2003-03-04T00:00:00</lastmod><rs:size>444</rs:size></url><url><loc>b</loc><lastmod>2002-02-02T00:00:00</lastmod><rs:size>56789</rs:size></url></urlset>")

    def test_10_sitemap(self):
        xml='<?xml version=\'1.0\' encoding=\'UTF-8\'?>\n\
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:rs="http://resourcesync.org/change/0.1">\
<url><loc>http://e.com/a</loc><lastmod>2012-03-14T18:37:36</lastmod><rs:size>12</rs:size><rs:md5>aabbccdd</rs:md5></url>\
</urlset>'
        fh=StringIO.StringIO(xml)
        s=Sitemap()
        i=s.inventory_parse_xml(fh)
        self.assertEqual( s.resources_added, 1, 'got 1 resources')
        r=i.resources['http://e.com/a']
        self.assertTrue( r is not None, 'got the uri expected')
        self.assertEqual( r.uri, 'http://e.com/a' )
        self.assertEqual( r.lastmod, '2012-03-14T18:37:36' )
        self.assertEqual( r.size, 12 )
        self.assertEqual( r.md5, 'aabbccdd' )

    def test_11_parse_2(self):
        xml='<?xml version=\'1.0\' encoding=\'UTF-8\'?>\n\
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:rs="http://resourcesync.org/change/0.1">\
<url><loc>/tmp/rs_test/src/file_a</loc><lastmod>2012-03-14T18:37:36</lastmod><rs:size>12</rs:size></url>\
<url><loc>/tmp/rs_test/src/file_b</loc><lastmod>2012-03-14T18:37:36</lastmod><rs:size>32</rs:size></url>\
</urlset>'
        fh=StringIO.StringIO(xml)
        s=Sitemap()
        i=s.inventory_parse_xml(fh)
        self.assertEqual( s.resources_added, 2, 'got 2 resources')

    def test_12_parse_illformed(self):
        s=Sitemap()
        # was ExpatError in python2.6
        self.assertRaises( ParseError, s.inventory_parse_xml, StringIO.StringIO('not xml') )
        self.assertRaises( ParseError, s.inventory_parse_xml, StringIO.StringIO('<urlset><url>something</urlset>') )

    def test_13_parse_valid_xml_but_other(self):
        s=Sitemap()
        self.assertRaises( ValueError, s.inventory_parse_xml, StringIO.StringIO('<urlset xmlns="http://example.org/other_namespace"> </urlset>') )
        self.assertRaises( ValueError, s.inventory_parse_xml, StringIO.StringIO('<other xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"> </other>') )

    def test_14_parse_sitemapindex(self):
        s=Sitemap()
        self.assertRaises( SitemapIndexError, s.inventory_parse_xml, StringIO.StringIO('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"> </sitemapindex>') )


if  __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(SitemapResource)
    unittest.TextTestRunner(verbosity=2).run(suite)
