"""Map between source URLs and destination paths"""
import os
import os.path
import re

class Mapper():
    
    def __init__(self,src_root=None,dst_root=None):
        self.src_root=src_root
        self.dst_root=dst_root

    def dst_to_src(self,dst_file):
        """Return the src URI from the dst filepath
        """
        rel_path=os.path.relpath(dst_file,start=self.dst_root)
        if (rel_path == '.'):
            rel_path=''
        else:
            rel_path= '/'+rel_path
        if (os.sep != '/'):
            # if directoty path sep isn't / then translate for URI                                            
            rel_path=rel_path.replace(os.sep,'/')
        return(self.src_root+rel_path)
        
    def src_to_dst(self,src_uri):
        """Return the dst filepath from the src URI
        
        FIXME -- look at whether urlparse can be used here?
        """
        m=re.match(self.src_root+"(.*)$",src_uri)
        if (m is None):
            raise "FIXME - Does not match"
        rel_path=m.group(1)
        if (os.sep != '/'):
            # if directoty path sep isn't / then translate for URI                                            
            rel_path=rel_path.replace('/',os.sep)
        return(self.dst_root+rel_path)
