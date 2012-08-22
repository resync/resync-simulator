import unittest
import resync.digest

class TestDigest(unittest.TestCase):

    def test1_string(self):
        self.assertEqual( resync.digest.compute_md5_for_string('A file\n'),
                          'j912liHgA/48DCHpkptJHg==')

    def test2_file(self):
        # Should be same as the string above
        self.assertEqual( resync.digest.compute_md5_for_file('resync/test/testdata/a'),
                          'j912liHgA/48DCHpkptJHg==')

if __name__ == '__main__':
    unittest.main()
