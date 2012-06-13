import unittest
from resync.client import Client, ClientFatalError

class TestResource(unittest.TestCase):

    def test1_make_inventory_empty(self):
        c = Client()
        # No mapping is error
        self.assertRaises( TypeError, c.inventory )
        # Supply empty mapping
        c.set_mappings( [] )
        i = c.inventory
        self.assertEqual( len(i), 0 )

    def test2_bad_source_uri(self):
        c = Client()
        self.assertRaises( ClientFatalError, c.sync_or_audit, 'a', '/tmp/bbb' )
        self.assertRaises( ClientFatalError, c.sync_or_audit, 'http://example.org/bbb', '/tmp/bbb' )

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestClientResource)
    unittest.TextTestRunner(verbosity=2).run(suite)
