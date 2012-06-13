import unittest
from resync.resource import Resource
from resync.inventory import Inventory

class TestInventory(unittest.TestCase):

    def test1_same(self):
        data = { 'a':1, 'b':2 }
        src = Inventory(resources=data)
        dst = Inventory(resources=data)
        ( num_same, changed, deleted, added ) = dst.compare(src)
        self.assertEqual(num_same, 2, "2 things unchanged")
        self.assertEqual(changed, [], "nothing changed")
        self.assertEqual(deleted, [], "nothing deleted")
        self.assertEqual(added, [], "nothing added")

    def test2_changed(self):
        src = Inventory( resources={ 'a':1, 'b':2 } )
        dst = Inventory( resources={ 'a':3, 'b':4 } )
        ( num_same, changed, deleted, added ) = dst.compare(src)
        self.assertEqual(num_same, 0, "0 things unchanged")
        self.assertEqual(changed, ['a', 'b'], "2 things changed")
        self.assertEqual(deleted, [], "nothing deleted")
        self.assertEqual(added, [], "nothing added")

    def test3_deleted(self):
        src = Inventory( resources={ 'a':1, 'b':2 } )
        dst = Inventory( resources={ 'a':1, 'b':2, 'c':3, 'd':4 } )
        ( num_same, changed, deleted, added ) = dst.compare(src)
        self.assertEqual(num_same, 2, "2 things unchanged")
        self.assertEqual(changed, [], "nothing changed")
        self.assertEqual(deleted, ['c','d'], "c and d deleted")
        self.assertEqual(added, [], "nothing added")

    def test4_added(self):
        src = Inventory( resources={ 'a':1, 'b':2, 'c':3, 'd':4 } )
        dst = Inventory( resources={ 'a':1, 'c':3 } )
        ( num_same, changed, deleted, added ) = dst.compare(src)
        self.assertEqual(num_same, 2, "2 things unchanged")
        self.assertEqual(changed, [], "nothing changed")
        self.assertEqual(deleted, [], "nothing deleted")
        self.assertEqual(added, ['b','d'], "b and d added")

    def test5_add(self):
        r1 = Resource(uri='a')
        r2 = Resource(uri='b')
        m = Inventory()
        m.add(r1)
        self.assertRaises( ValueError, m.add, r1)
        m.add(r2)
        self.assertRaises( ValueError, m.add, r2)

    def test6_has_md5(self):
        r1 = Resource(uri='a')
        r2 = Resource(uri='b')
        m = Inventory()
        self.assertFalse( m.has_md5() )
        m.add(r1)
        m.add(r2)
        self.assertFalse( m.has_md5() )
        r1.md5="aabbcc"
        self.assertTrue( m.has_md5() )

if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestInventory)
#    unittest.TextTestRunner(verbosity=1).run(suite)
    unittest.TextTestRunner().run(suite)
