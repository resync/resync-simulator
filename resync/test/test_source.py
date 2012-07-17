import unittest
import random
from resync.source import Source
from resync.resource import Resource

class TestSource(unittest.TestCase):

    def setUp(self):
        config = {}
        config['name'] = "ResourceSync Simulator"
        config['number_of_resources'] = 1000
        config['change_frequency'] = 0.5
        config['event_types'] = ['create', 'update', 'delete']
        config['average_payload'] = 1000
        config['max_events'] = -1
        self.source = Source(config, "localhost", "8888")
        self.source.bootstrap()

    def test_init(self):
        self.assertTrue(self.source is not None)
        self.assertTrue(self.source.config is not None)
        self.assertEqual(self.source.port, "8888")
        self.assertEqual(self.source.hostname, "localhost")
        self.assertTrue(self.source.inventory is None)
        self.assertTrue(self.source.changememory is None)
    
    def test_base_uri(self):
        self.assertEqual(self.source.base_uri, "http://localhost:8888")
        
    def test_resource_count(self):
        self.assertEqual(self.source.resource_count, 1000)
        
    def test_resources(self):
        resources = [resource for resource in self.source.resources]
        self.assertEqual(len(resources), 1000)
    
    def test_resource(self):
        # Fetch a random basename from the source repository
        rand_basename = random.choice(self.source._repository.keys())
        self.assertTrue(rand_basename is not None)
        resource = self.source.resource(rand_basename)
        self.assertTrue(resource is not None,
            "Cannot create resource %s" % rand_basename)
        self.assertTrue( isinstance(resource, Resource) )
        self.assertEquals(resource.uri, 
            "http://localhost:8888/resources/%s" % rand_basename)
        self.assertEquals(resource.size,
            self.source._repository[rand_basename]['size'])
        self.assertEquals(resource.timestamp,
            self.source._repository[rand_basename]['timestamp'])
        # Try to fetch non-existing resource
        resource = self.source.resource(-10)
        self.assertTrue(resource is None)
    
    def test_resource_payload(self):
        # Fetch a random basename from the source repository
        rand_basename = random.choice(self.source._repository.keys())        
        size = self.source._repository[rand_basename]['size']
        payload = self.source.resource_payload(rand_basename)
        self.assertEqual(len(payload), size)
    
    def test_random_resources(self):
        self.assertEqual(len(self.source.random_resources()), 1)
        self.assertEqual(len(self.source.random_resources(1)), 1)
        self.assertEqual(len(self.source.random_resources(17)), 17)
    
    def test_create_resource(self):
        len_before = self.source.resource_count
        self.source._create_resource(basename="1177")
        self.assertEqual(self.source.resource_count, len_before+1)
        
    def test_delete_resource(self):
        len_before = self.source.resource_count
        rand_basename = self.source.random_resource.basename
        self.source._delete_resource(basename=rand_basename)
        self.assertEqual(self.source.resource_count, len_before-1)

    def test_update_resource(self):
        len_before = self.source.resource_count
        rand_basename = self.source.random_resource.basename
        self.source._update_resource(basename=rand_basename)
        self.assertEqual(self.source.resource_count, len_before)

if __name__ == '__main__':
    unittest.main()