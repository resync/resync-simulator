import unittest
from resync.resource_change import ResourceChange
from resync.changeset import ChangeSet

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

    def test3_has_md5(self):
        r1 = ResourceChange(uri='a')
        r2 = ResourceChange(uri='b')
        i = ChangeSet()
        self.assertFalse( i.has_md5() )
        i.add(r1)
        i.add(r2)
        self.assertFalse( i.has_md5() )
        r1.md5="aabbcc"
        self.assertTrue( i.has_md5() )

    def test4_changeset(self):
        src = ChangeSet()
        src.add( ResourceChange('a',timestamp=1) )
        src.add( ResourceChange('b',timestamp=2) )
        src.add( ResourceChange('c',timestamp=3) )
        src.add( ResourceChange('d',timestamp=4)) 
        src.add( ResourceChange('e',timestamp=5) )
        self.assertEqual(len(src), 5, "5 things in src")

    def test5_iter(self):
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

if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestChangeSet)
    unittest.TextTestRunner().run(suite)
