import sys
import unittest
import StringIO
from resync.resource_change import ResourceChange
from resync.inventory import Inventory
from resync.sitemap import Sitemap, SitemapIndexError

# etree gives ParseError in 2.7, ExpatError in 2.6
etree_error_class = None
if (sys.version_info < (2,7)):
    from xml.parsers.expat import ExpatError
    etree_error_class = ExpatError
else:
    from xml.etree.ElementTree import ParseError
    etree_error_class = ParseError

class TestSitemapChanges(unittest.TestCase):

    def test_01_resource_str(self):
        # ResourceChange but with no change info
        r1 = ResourceChange('http://example.org/r/1',1234,9999,'Q2hlY2sgSW50ZWdyaXR5IQ==')
        self.assertEqual( Sitemap().resource_as_xml(r1), "<?xml version='1.0' encoding='UTF-8'?>\n<url><loc>http://example.org/r/1</loc><lastmod>1970-01-01T00:20:34Z</lastmod><rs:size>9999</rs:size><rs:fixity type=\"md5\">Q2hlY2sgSW50ZWdyaXR5IQ==</rs:fixity></url>" )

    def test_02_resource_created(self):
        # ResourceChange with created
        r1 = ResourceChange('http://example.org/r/1',1234,9999,'Q2hlY2sgSW50ZWdyaXR5IQ==',changetype='CREATED')
        xml = Sitemap().resource_as_xml(r1)
        self.assertEqual( xml, "<?xml version='1.0' encoding='UTF-8'?>\n<url><loc>http://example.org/r/1</loc><lastmod rs:type=\"created\">1970-01-01T00:20:34Z</lastmod><rs:size>9999</rs:size><rs:fixity type=\"md5\">Q2hlY2sgSW50ZWdyaXR5IQ==</rs:fixity></url>" )
        # Now make inventory
        i = Inventory()
        i.add(r1)
        inv_xml = Sitemap().resources_as_xml(i)
        self.assertEqual( inv_xml, "<?xml version='1.0' encoding='UTF-8'?>\n<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\" xmlns:rs=\"http://www.openarchives.org/rs/terms/\"><url><loc>http://example.org/r/1</loc><lastmod rs:type=\"created\">1970-01-01T00:20:34Z</lastmod><rs:size>9999</rs:size><rs:fixity type=\"md5\">Q2hlY2sgSW50ZWdyaXR5IQ==</rs:fixity></url></urlset>" )
        # and try parsing back
        s = Sitemap()
        s.resource_class = ResourceChange
        i = s.inventory_parse_xml(fh=StringIO.StringIO(inv_xml))
        self.assertEqual( len(i), 1 )
        r = iter(i).next()
        self.assertEqual( r.uri, 'http://example.org/r/1')
        self.assertEqual( r.timestamp, 1234)
        self.assertEqual( r.changetype, 'CREATED')

    def test_03_resource_updated(self):
        # ResourceChange with updated
        r1 = ResourceChange('http://example.org/r/1',1234,9999,'Q2hlY2sgSW50ZWdyaXR5IQ==',changetype='UPDATED')
        self.assertEqual( Sitemap().resource_as_xml(r1), "<?xml version='1.0' encoding='UTF-8'?>\n<url><loc>http://example.org/r/1</loc><lastmod rs:type=\"updated\">1970-01-01T00:20:34Z</lastmod><rs:size>9999</rs:size><rs:fixity type=\"md5\">Q2hlY2sgSW50ZWdyaXR5IQ==</rs:fixity></url>" )
        # Now make inventory
        i = Inventory()
        i.add(r1)
        inv_xml = Sitemap().resources_as_xml(i)
        # and try parsing back
        s = Sitemap()
        s.resource_class = ResourceChange
        i = s.inventory_parse_xml(fh=StringIO.StringIO(inv_xml))
        self.assertEqual( len(i), 1 )
        r = iter(i).next()
        self.assertEqual( r.uri, 'http://example.org/r/1')
        self.assertEqual( r.timestamp, 1234)
        self.assertEqual( r.changetype, 'UPDATED')

    def test_02_resource_deleted(self):
        # ResourceChange with deleted
        r1 = ResourceChange('http://example.org/r/1',1234,9999,'Q2hlY2sgSW50ZWdyaXR5IQ==',changetype='DELETED')
        self.assertEqual( Sitemap().resource_as_xml(r1), "<?xml version='1.0' encoding='UTF-8'?>\n<url><loc>http://example.org/r/1</loc><expires>1970-01-01T00:20:34Z</expires><rs:size>9999</rs:size><rs:fixity type=\"md5\">Q2hlY2sgSW50ZWdyaXR5IQ==</rs:fixity></url>" )
        # Now make inventory
        i = Inventory()
        i.add(r1)
        inv_xml = Sitemap().resources_as_xml(i)
        # and try parsing back
        s = Sitemap()
        s.resource_class = ResourceChange
        i = s.inventory_parse_xml(fh=StringIO.StringIO(inv_xml))
        self.assertEqual( len(i), 1 )
        r = iter(i).next()
        self.assertEqual( r.uri, 'http://example.org/r/1')
        self.assertEqual( r.timestamp, 1234)
        self.assertEqual( r.changetype, 'DELETED')

if  __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSitemapChanges)
    unittest.TextTestRunner(verbosity=2).run(suite)
