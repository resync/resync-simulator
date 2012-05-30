import unittest
from resync.mapper import Mapper

class TestMapper(unittest.TestCase):

    def test_src_to_dst(self):
        m=Mapper('http://e.org/p','/tmp/q')
        self.assertEqual( m.src_to_dst('http://e.org/p'), '/tmp/q')
        self.assertEqual( m.src_to_dst('http://e.org/p/aa'), '/tmp/q/aa')
        self.assertEqual( m.src_to_dst('http://e.org/p/aa/bb'), '/tmp/q/aa/bb')
        self.assertEqual( m.src_to_dst('http://e.org/p/aa/bb/'), '/tmp/q/aa/bb/')
        self.assertEqual( m.src_to_dst('http://e.org/pa'), '/tmp/qa') #should throw error

    def test_dst_to_src(self):
        m=Mapper('http://e.org/p','/tmp/q')
        self.assertEqual( m.dst_to_src('/tmp/q'), 'http://e.org/p')
        self.assertEqual( m.dst_to_src('/tmp/q/bb'), 'http://e.org/p/bb')
        self.assertEqual( m.dst_to_src('/tmp/q/bb/cc'), 'http://e.org/p/bb/cc')
        #self.assertEqual( m.dst_to_src('/tmp/q/'), 'http://e.org/p/')
        #self.assertEqual( m.dst_to_src('/tmp/qa'), 'http://e.org/pa') #should throw error

if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestMapper)
    unittest.TextTestRunner(verbosity=2).run(suite)
