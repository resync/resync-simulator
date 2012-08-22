import unittest
from resync.resource import Resource
from resync.resource_change import ResourceChange
from resync.changeset import ChangeSet
from resync.inventory import Inventory

class TestChangeSet(unittest.TestCase):

    def test1_set_with_repeats(self):
        src = ChangeSet()
        src.add( ResourceChange('a',timestamp=1) )
        src.add( ResourceChange('b',timestamp=1) )
        src.add( ResourceChange('c',timestamp=1) )
        src.add( ResourceChange('a',timestamp=2) )
        src.add( ResourceChange('b',timestamp=2) )
        self.assertEqual(len(src), 5, "5 changes in changeset")

    def test2_with_repeats_again(self):
        r1 = ResourceChange(uri='a',size=1)
        r2 = ResourceChange(uri='b',size=2)
        i = ChangeSet()
        i.add(r1)
        i.add(r2)
        self.assertEqual( len(i), 2 )
        # Can add another ResourceChange with same URI
        r1d = ResourceChange(uri='a',size=10)
        i.add(r1d)
        self.assertEqual( len(i), 3 )

    def test3_changeset(self):
        src = ChangeSet()
        src.add( ResourceChange('a',timestamp=1) )
        src.add( ResourceChange('b',timestamp=2) )
        src.add( ResourceChange('c',timestamp=3) )
        src.add( ResourceChange('d',timestamp=4)) 
        src.add( ResourceChange('e',timestamp=5) )
        self.assertEqual(len(src), 5, "5 things in src")

    def test4_iter(self):
        i = ChangeSet()
        i.add( ResourceChange('a',timestamp=1) )
        i.add( ResourceChange('b',timestamp=2) )
        i.add( ResourceChange('c',timestamp=3) )
        i.add( ResourceChange('d',timestamp=4) )
        resources=[]
        for r in i:
            resources.append(r)
        self.assertEqual(len(resources), 4)
        self.assertEqual( resources[0].uri, 'a')
        self.assertEqual( resources[3].uri, 'd')

    def test5_add_changed_resources(self):
        added = Inventory()
        added.add( Resource('a',timestamp=1) )
        added.add( Resource('d',timestamp=4))
        self.assertEqual(len(added), 2, "2 things in added inventory")
        changes = ChangeSet()
        changes.add_changed_resources( added, changetype='created' )
        self.assertEqual(len(changes), 2, "2 things added")
        i = iter(changes)
        first = i.next()
        self.assertEqual(first.uri, 'a', "changes[0].uri=a")
        self.assertEqual(first.timestamp, 1, "changes[0].timestamp=1")
        self.assertEqual(first.changetype, 'created', "changes[0].changetype=created")
        second = i.next()
        self.assertEqual(second.timestamp, 4, "changes[1].timestamp=4")
        self.assertEqual(second.changetype, 'created', "changes[1].changetype=created")
        # Now add some with updated (one same, one diff)
        updated = Inventory()
        updated.add( Resource('a',timestamp=5) )
        updated.add( Resource('b',timestamp=6))
        self.assertEqual(len(updated), 2, "2 things in updated inventory")
        changes.add_changed_resources( updated, changetype='updated' )
        self.assertEqual(len(changes), 4, "4 = 2 old + 2 things updated")
        # Make new inventory from the changes which should not have dupes
        dst = Inventory()
        dst.add( changes, replace=True )
        self.assertEqual(len(dst), 3, "3 unique resources")
        self.assertEqual(dst.resources['a'].timestamp, 5 ) # 5 was later in last the 1
        self.assertEqual(dst.resources['a'].changetype, 'updated')
        self.assertEqual(dst.resources['b'].timestamp, 6)
        self.assertEqual(dst.resources['b'].changetype, 'updated')
        self.assertEqual(dst.resources['d'].timestamp, 4)
        self.assertEqual(dst.resources['d'].changetype, 'created')

if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestChangeSet)
    unittest.TextTestRunner().run(suite)
