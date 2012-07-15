import unittest
from resync.dump import Dump, DumpError
from resync.inventory import Inventory
from resync.resource_file import ResourceFile

class TestMapper(unittest.TestCase):

    def test00_dump_creation(self):
        i=Inventory()
        i.add( ResourceFile('http://ex.org/a', size=1, file='resync/test/testdata/a') )
        i.add( ResourceFile('http://ex.org/b', size=2, file='resync/test/testdata/b') )
        d=Dump()
        d.check_files(inventory=i)
        self.assertEqual(d.total_size, 28)
        
    #FIXME -- need some code to actually write and read dump

if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestMapper)
    unittest.TextTestRunner(verbosity=2).run(suite)
