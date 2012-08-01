import unittest
from resync.resource import Resource
from resync.resource_container import ResourceContainer

class TestResourceContainer(unittest.TestCase):

    def test1_create_and_add(self):
        rc = ResourceContainer( resources=[] )
        self.assertEqual( len(rc), 0, "empty" )
        rc.resources.append( Resource('a',timestamp=1) )
        rc.resources.append( Resource('b',timestamp=2) )
        self.assertEqual( len(rc), 2, "two resources" )

    def test2_has_md5(self):
        r1 = Resource(uri='a')
        r2 = Resource(uri='b')
        i = ResourceContainer( resources=[] )
        self.assertFalse( i.has_md5() )
        i.resources.append(r1)
        i.resources.append(r2)
        self.assertFalse( i.has_md5() )
        r1.md5="aabbcc"
        self.assertTrue( i.has_md5() )

    def test3_iter(self):
        rc = ResourceContainer( resources=[] )
        rc.resources.append( Resource('a',timestamp=1) )
        rc.resources.append( Resource('b',timestamp=2) )
        rc.resources.append( Resource('c',timestamp=3) )
        rc.resources.append( Resource('d',timestamp=4) )
        resources=[]
        for r in rc:
            resources.append(r)
        self.assertEqual(len(resources), 4)
        self.assertEqual( resources[0].uri, 'a')
        self.assertEqual( resources[3].uri, 'd')

if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestResourceContainer)
    unittest.TextTestRunner().run(suite)
