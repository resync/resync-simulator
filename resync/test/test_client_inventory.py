import unittest
import StringIO
from resync.client_inventory import ClientInventory
from resync.client_resource import ClientResource
from xml.etree.ElementTree import ParseError
#from xml.parsers.expat import ParseError

class TestClientInventory(unittest.TestCase):

    def test1_same(self):
        data = { 'a':1, 'b':2 }
        src = ClientInventory(data)
        dst = ClientInventory(data)
        ( num_same, changed, deleted, added ) = dst.compare(src)
        self.assertEqual(num_same, 2, "2 things unchanged")
        self.assertEqual(changed, [], "nothing changed")
        self.assertEqual(deleted, [], "nothing deleted")
        self.assertEqual(added, [], "nothing added")

    def test2_changed(self):
        data = { 'a':1, 'b':2 }
        src = ClientInventory( { 'a':1, 'b':2 } )
        dst = ClientInventory( { 'a':3, 'b':4 } )
        ( num_same, changed, deleted, added ) = dst.compare(src)
        self.assertEqual(num_same, 0, "0 things unchanged")
        self.assertEqual(changed, ['a', 'b'], "2 things changed")
        self.assertEqual(deleted, [], "nothing deleted")
        self.assertEqual(added, [], "nothing added")

    def test3_deleted(self):
        data = { 'a':1, 'b':2 }
        src = ClientInventory( { 'a':1, 'b':2 } )
        dst = ClientInventory( { 'a':1, 'b':2, 'c':3, 'd':4 } )
        ( num_same, changed, deleted, added ) = dst.compare(src)
        self.assertEqual(num_same, 2, "2 things unchanged")
        self.assertEqual(changed, [], "nothing changed")
        self.assertEqual(deleted, ['c','d'], "c and d deleted")
        self.assertEqual(added, [], "nothing added")

    def test4_added(self):
        data = { 'a':1, 'b':2 }
        src = ClientInventory( { 'a':1, 'b':2, 'c':3, 'd':4 } )
        dst = ClientInventory( { 'a':1, 'c':3 } )
        ( num_same, changed, deleted, added ) = dst.compare(src)
        self.assertEqual(num_same, 2, "2 things unchanged")
        self.assertEqual(changed, [], "nothing changed")
        self.assertEqual(deleted, [], "nothing deleted")
        self.assertEqual(added, ['b','d'], "b and d added")

    def test5_print(self):
        r1 = ClientResource(uri='a',lastmod='2001-01-01',size=1234)
        r2 = ClientResource(uri='b',lastmod='2002-02-02',size=56789)
        r3 = ClientResource(uri='c',lastmod='2003-03-03',size=0)
        m = ClientInventory()
        m.add(r1)
        m.add(r2)
        m.add(r3)
        #print m
        self.assertEqual(str(m), "<?xml version='1.0' encoding='UTF-8'?>\n<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\" xmlns:rs=\"http://resourcesync.org/change/0.1\"><url><loc>a</loc><lastmod>2001-01-01T00:00:00</lastmod><rs:size>1234</rs:size></url><url><loc>b</loc><lastmod>2002-02-02T00:00:00</lastmod><rs:size>56789</rs:size></url><url><loc>c</loc><lastmod>2003-03-03T00:00:00</lastmod><rs:size>0</rs:size></url></urlset>")

    def test6_print_subset(self): 
        r1 = ClientResource(uri='a',lastmod='2001-01-01',size=1234)
        r2 = ClientResource(uri='b',lastmod='2002-02-02',size=56789)
        r3 = ClientResource(uri='c',lastmod='2003-03-03',size=0)
        r3 = ClientResource(uri='d',lastmod='2003-03-04',size=444)
        m = ClientInventory()
        m.add(r1)
        m.add(r2)
        m.add(r3)
        self.assertEqual(m.as_xml(entries=['d','b']), "<?xml version='1.0' encoding='UTF-8'?>\n<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\" xmlns:rs=\"http://resourcesync.org/change/0.1\"><url><loc>d</loc><lastmod>2003-03-04T00:00:00</lastmod><rs:size>444</rs:size></url><url><loc>b</loc><lastmod>2002-02-02T00:00:00</lastmod><rs:size>56789</rs:size></url></urlset>")

    def test7_add(self):
        r1 = ClientResource(uri='a')
        r2 = ClientResource(uri='b')
        m = ClientInventory()
        m.add(r1)
        self.assertRaises( ValueError, m.add, r1)
        m.add(r2)
        self.assertRaises( ValueError, m.add, r2)

    def test_parse_1(self):
        xml='<?xml version=\'1.0\' encoding=\'UTF-8\'?>\n\
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:rs="http://resourcesync.org/change/0.1">\
<url><loc>http://e.com/a</loc><lastmod>2012-03-14T18:37:36</lastmod><rs:size>12</rs:size><rs:md5>aabbccdd</rs:md5></url>\
</urlset>'
        fh=StringIO.StringIO(xml)
        m=ClientInventory()
        num_resources=m.parse_xml(fh)
        self.assertEqual( num_resources, 1, 'got 1 resources')
        r=m.resources['http://e.com/a']
        self.assertTrue( r is not None, 'got the uri expected')
        self.assertEqual( r.uri, 'http://e.com/a' )
        self.assertEqual( r.lastmod, '2012-03-14T18:37:36' )
        self.assertEqual( r.size, 12 )
        self.assertEqual( r.md5, 'aabbccdd' )

    def test_parse_2(self):
        xml='<?xml version=\'1.0\' encoding=\'UTF-8\'?>\n\
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:rs="http://resourcesync.org/change/0.1">\
<url><loc>/tmp/rs_test/src/file_a</loc><lastmod>2012-03-14T18:37:36</lastmod><rs:size>12</rs:size></url>\
<url><loc>/tmp/rs_test/src/file_b</loc><lastmod>2012-03-14T18:37:36</lastmod><rs:size>32</rs:size></url>\
</urlset>'
        fh=StringIO.StringIO(xml)
        m=ClientInventory()
        num_resources=m.parse_xml(fh)
        self.assertEqual( num_resources, 2, 'got 2 resources')

    def test_parse_3_illformed(self):
        m=ClientInventory()
        # was ExpatError in python2.6
        self.assertRaises( ParseError, m.parse_xml, StringIO.StringIO('not xml') )
        self.assertRaises( ParseError, m.parse_xml, StringIO.StringIO('<urlset><url>something</urlset>') )

if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestClientInventory)
#    unittest.TextTestRunner(verbosity=1).run(suite)
    unittest.TextTestRunner().run(suite)

