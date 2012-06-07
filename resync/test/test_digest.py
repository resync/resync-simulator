import unittest
import resync.digest

class TestDigest(unittest.TestCase):

    def test1_string(self):
        self.assertEqual( resync.digest.compute_md5_for_string('A file\n'),
                          '8fdd769621e003fe3c0c21e9929b491e', 'md5 for testdata/a')

    def test2_file(self):
        self.assertEqual( resync.digest.compute_md5_for_file('resync/test/testdata/a'),
                          '8fdd769621e003fe3c0c21e9929b491e', 'md5 for testdata/a')

if __name__ == '__main__':
    unittest.main()
