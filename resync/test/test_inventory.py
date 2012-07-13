import unittest
from resync.resource import Resource
from resync.inventory import Inventory, InventoryDupeError

class TestInventory(unittest.TestCase):

    def test1_same(self):
        src = Inventory()
        src.add( Resource('a',timestamp=1) )
        src.add( Resource('b',timestamp=2) )
        dst = Inventory()
        dst.add( Resource('a',timestamp=1) )
        dst.add( Resource('b',timestamp=2) )
        ( num_same, changed, deleted, added ) = dst.compare(src)
        self.assertEqual(num_same, 2, "2 things unchanged")
        self.assertEqual(changed, [], "nothing changed")
        self.assertEqual(deleted, [], "nothing deleted")
        self.assertEqual(added, [], "nothing added")

    def test2_changed(self):
        src = Inventory()
        src.add( Resource('a',timestamp=1) )
        src.add( Resource('b',timestamp=2) )
        dst = Inventory()
        dst.add( Resource('a',timestamp=3) )
        dst.add( Resource('b',timestamp=4) )
        ( num_same, changed, deleted, added ) = dst.compare(src)
        self.assertEqual(num_same, 0, "0 things unchanged")
        self.assertEqual(changed, ['a', 'b'], "2 things changed")
        self.assertEqual(deleted, [], "nothing deleted")
        self.assertEqual(added, [], "nothing added")

    def test3_deleted(self):
        src = Inventory()
        src.add( Resource('a',timestamp=1) )
        src.add( Resource('b',timestamp=2) )
        dst = Inventory()
        dst.add( Resource('a',timestamp=1) )
        dst.add( Resource('b',timestamp=2) )
        dst.add( Resource('c',timestamp=3) )
        dst.add( Resource('d',timestamp=4) )
        ( num_same, changed, deleted, added ) = dst.compare(src)
        self.assertEqual(num_same, 2, "2 things unchanged")
        self.assertEqual(changed, [], "nothing changed")
        self.assertEqual(deleted, ['c','d'], "c and d deleted")
        self.assertEqual(added, [], "nothing added")

    def test4_added(self):
        src = Inventory()
        src.add( Resource('a',timestamp=1) )
        src.add( Resource('b',timestamp=2) )
        src.add( Resource('c',timestamp=3) )
        src.add( Resource('d',timestamp=4) )
        dst = Inventory()
        dst.add( Resource('a',timestamp=1) )
        dst.add( Resource('c',timestamp=3) )
        ( num_same, changed, deleted, added ) = dst.compare(src)
        self.assertEqual(num_same, 2, "2 things unchanged")
        self.assertEqual(changed, [], "nothing changed")
        self.assertEqual(deleted, [], "nothing deleted")
        self.assertEqual(added, ['b','d'], "b and d added")

    def test5_add(self):
        r1 = Resource(uri='a',size=1)
        r2 = Resource(uri='b',size=2)
        i = Inventory()
        i.add(r1)
        self.assertRaises( InventoryDupeError, i.add, r1)
        i.add(r2)
        self.assertRaises( InventoryDupeError, i.add, r2)
        # allow dupes
        r1d = Resource(uri='a',size=10)
        i.add(r1d,replace=True)
        self.assertEqual( len(i), 2 )
        self.assertEqual( i.resources['a'].size, 10 ) 

    def test5_add_iterable(self):
        r1 = Resource(uri='a',size=1)
        r2 = Resource(uri='b',size=2)
        i = Inventory()
        i.add( [r1,r2] )
        self.assertRaises( InventoryDupeError, i.add, r1)
        self.assertRaises( InventoryDupeError, i.add, r2)
        # allow dupes
        r1d = Resource(uri='a',size=10)
        i.add( [r1d] ,replace=True)
        self.assertEqual( len(i), 2 )
        self.assertEqual( i.resources['a'].size, 10 ) 

    def test6_has_md5(self):
        r1 = Resource(uri='a')
        r2 = Resource(uri='b')
        i = Inventory()
        self.assertFalse( i.has_md5() )
        i.add(r1)
        i.add(r2)
        self.assertFalse( i.has_md5() )
        r1.md5="aabbcc"
        self.assertTrue( i.has_md5() )

    def test7_changeset(self):
        src = Inventory()
        src.add( Resource('a',timestamp=1) )
        src.add( Resource('b',timestamp=2) )
        src.add( Resource('c',timestamp=3) )
        src.add( Resource('d',timestamp=4)) 
        src.add( Resource('e',timestamp=5) )
        self.assertEqual(len(src), 5, "5 things in src")
        changes = src.changeset( ['a','d'], changetype='X' )
        self.assertEqual(len(changes), 2, "2 things extracted")
        self.assertEqual(changes[0].uri, 'a', "changes[0].uri=a")
        self.assertEqual(changes[0].timestamp, 1, "changes[0].timestamp=1")
        self.assertEqual(changes[0].changetype, 'X', "changes[0].changetype=X")
        self.assertEqual(changes[1].timestamp, 4, "changes[1].timestamp=4")
        self.assertEqual(changes[1].changetype, 'X', "changes[1].changetype=X")
        # Make new inventory from the changes
        dst = Inventory()
        dst.add( changes )
        self.assertEqual(dst.resources['a'].timestamp, 1 )
        self.assertEqual(dst.resources['a'].changetype, 'X')
        self.assertEqual(dst.resources['d'].timestamp, 4)
        self.assertEqual(dst.resources['d'].changetype, 'X')

    def test8_iter(self):
        i = Inventory()
        i.add( Resource('a',timestamp=1) )
        i.add( Resource('b',timestamp=2) )
        i.add( Resource('c',timestamp=3) )
        i.add( Resource('d',timestamp=4) )
        resources=[]
        for r in i:
            resources.append(r)
        self.assertEqual(len(resources), 4)
        self.assertEqual( resources[0].uri, 'a')
        self.assertEqual( resources[3].uri, 'd')

if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestInventory)
#    unittest.TextTestRunner(verbosity=1).run(suite)
    unittest.TextTestRunner().run(suite)
