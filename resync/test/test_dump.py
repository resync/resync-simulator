import unittest
from resync.dump import Dump, DumpError
from resync.mapper import Mapper
from resync.inventory import Inventory
from resync.resource import Resource

class TestMapper(unittest.TestCase):

    def test00_dump_creation(self):
        i=Inventory()
        i.add( Resource('http://ex.org/a', size=1) )
        i.add( Resource('http://ex.org/b', size=2) )
        m=Mapper(['http://ex.org=./resync/test/testdata'])
        d=Dump(mapper=m)
        d.check_files(inventory=i)
        self.assertEqual(len(d.files), 2)
        self.assertEqual(d.total_size, 28)
        
    #FIXME -- need some code to actually write and read dump

if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestMapper)
    unittest.TextTestRunner(verbosity=2).run(suite)
