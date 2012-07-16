"""A set of command line client tests"""
import unittest
import os
import os.path

test_dir = '/tmp/test_resync_client'
env_var = 'RESYNC_CLIENT_TESTS'

class TestResource(unittest.TestCase):

    def setUp(self):
        print "###setUp"
        self.skip_all = False
        self.do_cleanup = False

    def check_flag(self):
        # Only do this if we force it..
        if (self.skip_all):
            self.skipTest()
        if (os.getenv(env_var) is None):
            self.skip_all = True
            self.skipTest( "Skipping resync-client tests as ENV{%s} not set" % (env_var) )
        
    def mkfile(self, dir, file, content ):
        """Make a test file"""
        filename = dir + '/' + file
        fh = open( filename, 'w' )
        fh.write( content )
        fh.close()

    def run_resync_client(self, *args):
        astr = ' '.join(args)
        print "args = %s" % (astr)
        ( cin, cout, cerr) = os.popen3( './resync-client ' + astr )
        cin.close()
        out = cout.read()
        return(out)
        
    def test01(self):
        self.check_flag()
        # Check and setup dir
        if ( os.path.exists(test_dir) ):
            self.skip_all = True
            self.fail( "Test directory %s already exists, delete it manually to run" % (test_dir) )
        # Does the code run at all?
        out = self.run_resync_client('-h')
        self.assertRegexpMatches( out, 'Usage: resync-client ' )
        # Make place to play
        os.mkdir(test_dir)
        self.do_cleanup = True
        # Now make some files
        dir1 = test_dir + '/dir1'
        os.mkdir(dir1)
        self.mkfile( dir1, 'a', 'aaaaa' )
        self.mkfile( dir1, 'b', 'bbb' )
        self.mkfile( dir1, 'c', 'c' )
        # Make a sitemap to stdout
        out = self.run_resync_client( '-w', 'http://example.org', dir1 )
        self.assertRegexpMatches( out , r'<url><loc>http://example.org/a</loc>' )
        self.assertRegexpMatches( out , r'<url><loc>http://example.org/b</loc>' )
        # Make a sitemap on disk
        sitemap = test_dir + '/sm.xml'
        out = self.run_resync_client( '-w', '--outfile', sitemap, 'http://example.org/', dir1 )
        self.assertRegexpMatches( out , r'Wrote sitemap ' )
        self.assertTrue( os.path.exists(sitemap) )
        # Audit 
        out = self.run_resync_client( '--audit', '--sitemap', sitemap, 'http://example.org/', dir1 )
        self.assertRegexpMatches( out , r'Status: +IN SYNC ' )
        self.assertRegexpMatches( out , r'same=3' )
        # Add extra resource
        self.mkfile( dir1, 'd', 'ddddddd' )
        # Make changeset
        out = self.run_resync_client( '-c', '--reference', sitemap, 'http://example.org', dir1 )
        self.assertRegexpMatches( out , r'<url><loc>http://example.org/d</loc>.*<rs:changetype>created<' )
        self.assertNotRegexpMatches( out , r'<url><loc>http://example.org/a</loc>' )
        # Audit 
        out = self.run_resync_client( '--audit', '--sitemap', sitemap, 'http://example.org/', dir1 )
        self.assertRegexpMatches( out , r'Status: +NOT IN SYNC ' )
        self.assertRegexpMatches( out , r'same=3' )
        self.assertRegexpMatches( out , r'deleted=1' ) #added on local disk == deleted on remote
        # Delete a resource, update a resource
        os.remove( dir1 + '/a' )
        self.mkfile( dir1, 'b', 'bbbupdated' )
        # Try changeset now with three changes
        out = self.run_resync_client( '-c', '--reference', sitemap, 'http://example.org', dir1 )
        self.assertRegexpMatches( out , r'<url><loc>http://example.org/d</loc>.*<rs:changetype>created<' )
        self.assertRegexpMatches( out , r'<url><loc>http://example.org/a</loc>.*<rs:changetype>deleted<' )
        self.assertRegexpMatches( out , r'<url><loc>http://example.org/b</loc>.*<rs:changetype>updated<' )
        self.assertNotRegexpMatches( out , r'<url><loc>http://example.org/c</loc>' )
        # Audit 
        out = self.run_resync_client( '--audit', '--sitemap', sitemap, 'http://example.org/', dir1 )
        self.assertRegexpMatches( out , r'Status: +NOT IN SYNC ' )
        self.assertRegexpMatches( out , r'same=1' )
        self.assertRegexpMatches( out , r'updated=1' )
        self.assertRegexpMatches( out , r'created=1' )
        self.assertRegexpMatches( out , r'deleted=1' ) #added on local disk == deleted on remote

    def tearDown(self):
        print "###tearDown"
        if (self.do_cleanup and (os.getenv('RESYNC_LEAVE_FILES') is None) ):
            os.system('rm -r /tmp/test_resync_client')
        
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestClientResource)
    unittest.TextTestRunner(verbosity=2).run(suite)
