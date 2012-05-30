import hashlib

def md5hex_for_file(file, block_size=2**14):
    """Return hex md5 digest for a file

    Optional block_size parameter controls memory used to do md5 calculation.
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
