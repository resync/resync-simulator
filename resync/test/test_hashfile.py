import unittest
from resync.hashfile import md5hex_for_file

class TestHashfile(unittest.TestCase):

    def test1(self):
        self.assertEqual( md5hex_for_file('resync/test/testdata/a'),
                          '8fdd769621e003fe3c0c21e9929b491e', 'md5 for testdata/a')

if __name__ == '__main__':
    unittest.main()
