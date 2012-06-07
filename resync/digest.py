import hashlib

def compute_md5_for_string(string):
    """Compute MD5 digest over some string payload"""
    return hashlib.md5(string).hexdigest()

def compute_md5_for_file(file, block_size=2**14):
    """Compute MD5 digest for a file

    Optional block_size parameter controls memory used to do MD5 calculation.
    This should be a multiple of 128 bytes.
    """
    f = open(file, 'r')
    md5 = hashlib.md5()
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5.update(data)
    return md5.hexdigest()
