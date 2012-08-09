import unittest
import re
import os
import time
from resync.inventory_builder import InventoryBuilder
from resync.sitemap import Sitemap
from resync.mapper import Mapper

class TestInventoryBuilder(unittest.TestCase):

    def setUp(self):
        # Set timestamps (mtime) for test data. Timestamps on disk are
        # in UTC so no conversion issues.
        # Test case file_a: 1343236426 = 2012-07-25T17:13:46Z
        # Test case file_b: 1000000000 = 2001-09-09T01:46:40Z
        os.utime( "resync/test/testdata/dir1/file_a", (0, 1343236426 ) )
        os.utime( "resync/test/testdata/dir1/file_b", (0, 1000000000 ) )

    def test1_simple_output(self):
        ib = InventoryBuilder(verbose=True)
        ib.mapper = Mapper(['http://example.org/t','resync/test/testdata/dir1'])
        i = ib.from_disk()
        self.assertEqual(Sitemap().resources_as_xml(i),'<?xml version=\'1.0\' encoding=\'UTF-8\'?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:rs="http://www.openarchives.org/rs/terms/"><url><loc>http://example.org/t/file_a</loc><lastmod>2012-07-25T17:13:46Z</lastmod><rs:size>20</rs:size></url><url><loc>http://example.org/t/file_b</loc><lastmod>2001-09-09T01:46:40Z</lastmod><rs:size>45</rs:size></url></urlset>' )

    def test2_pretty_output(self):
        ib = InventoryBuilder()
        ib.mapper = Mapper(['http://example.org/t','resync/test/testdata/dir1'])
        i = ib.from_disk()
        s = Sitemap()
        s.pretty_xml=True
        self.assertEqual(s.resources_as_xml(i),'<?xml version=\'1.0\' encoding=\'UTF-8\'?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:rs="http://www.openarchives.org/rs/terms/">\n<url><loc>http://example.org/t/file_a</loc><lastmod>2012-07-25T17:13:46Z</lastmod><rs:size>20</rs:size></url>\n<url><loc>http://example.org/t/file_b</loc><lastmod>2001-09-09T01:46:40Z</lastmod><rs:size>45</rs:size></url>\n</urlset>' )

    def test3_with_md5(self):
        ib = InventoryBuilder(do_md5=True)
        ib.mapper = Mapper(['http://example.org/t','resync/test/testdata/dir1'])
        i = ib.from_disk()
        s = Sitemap()
        xml = s.resources_as_xml(i)
        self.assertNotEqual( None, re.search('<loc>http://example.org/t/file_a</loc><lastmod>[\w\:\-]+Z</lastmod><rs:size>20</rs:size><rs:md5>6bf26fd66601b528d2e0b47eaa87edfd</rs:md5>',xml), 'size/checksum for file_a')
        self.assertNotEqual( None, re.search('<loc>http://example.org/t/file_b</loc><lastmod>[\w\:\-]+Z</lastmod><rs:size>45</rs:size><rs:md5>452e54bdae1626ac5d6e7be81b39de21</rs:md5>',xml), 'size/checksum for file_b' )

    def test4_data(self):
        ib = InventoryBuilder(do_md5=True)
        ib.mapper = Mapper(['http://example.org/t','resync/test/testdata/dir1'])
        i = ib.from_disk()
        self.assertEqual( len(i), 2)
        r1 = i.resources.get('http://example.org/t/file_a')
        self.assertTrue( r1 is not None )
        self.assertEqual( r1.uri, 'http://example.org/t/file_a' )
        self.assertEqual( r1.lastmod, '2012-07-25T17:13:46Z' )
        self.assertEqual( r1.md5, '6bf26fd66601b528d2e0b47eaa87edfd' )
        self.assertEqual( r1.file, 'resync/test/testdata/dir1/file_a' ) 

if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestInventoryBuilder)
    unittest.TextTestRunner(verbosity=2).run(suite)
