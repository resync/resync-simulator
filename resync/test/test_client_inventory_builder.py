import unittest
import re
import os
from resync.client_inventory_builder import ClientInventoryBuilder

class TestClientInventoryBuilder(unittest.TestCase):

    def setUp(self):
        # Set timestamps (mtime) for test data
        os.utime( "resync/test/testdata/dir1/file_a", (0, 1331761564) )
        os.utime( "resync/test/testdata/dir1/file_b", (0, 1331761585) )

    def test1_simple_output(self):
        mb = ClientInventoryBuilder()
        m = mb.from_disk('resync/test/testdata/dir1','http://example.org/t')
        self.assertEqual(str(m),'<?xml version=\'1.0\' encoding=\'UTF-8\'?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:rs="http://resourcesync.org/change/0.1"><url><loc>http://example.org/t/file_a</loc><lastmod>2012-03-14T17:46:04</lastmod><rs:size>20</rs:size></url><url><loc>http://example.org/t/file_b</loc><lastmod>2012-03-14T17:46:25</lastmod><rs:size>45</rs:size></url></urlset>' )

    def test2_pretty_output(self):
        mb = ClientInventoryBuilder()
        m = mb.from_disk('resync/test/testdata/dir1','http://example.org/t')
        m.pretty_xml=True
        self.assertEqual(str(m),'<?xml version=\'1.0\' encoding=\'UTF-8\'?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:rs="http://resourcesync.org/change/0.1">\n<url><loc>http://example.org/t/file_a</loc><lastmod>2012-03-14T17:46:04</lastmod><rs:size>20</rs:size></url>\n<url><loc>http://example.org/t/file_b</loc><lastmod>2012-03-14T17:46:25</lastmod><rs:size>45</rs:size></url>\n</urlset>' )

    def test3_with_md5(self):
        mb = ClientInventoryBuilder(do_md5=True)
        m = mb.from_disk('resync/test/testdata/dir1','http://example.org/t')
        xml=str(m)
        self.assertNotEqual( None, re.search('<loc>http://example.org/t/file_a</loc><lastmod>[\w\:\-]+</lastmod><rs:size>20</rs:size><rs:md5>6bf26fd66601b528d2e0b47eaa87edfd</rs:md5>',xml), 'size/checksum for file_a')
        self.assertNotEqual( None, re.search('<loc>http://example.org/t/file_b</loc><lastmod>[\w\:\-]+</lastmod><rs:size>45</rs:size><rs:md5>452e54bdae1626ac5d6e7be81b39de21</rs:md5>',xml), 'size/checksum for file_b' )


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestClientInventoryBuilder)
    unittest.TextTestRunner(verbosity=2).run(suite)
