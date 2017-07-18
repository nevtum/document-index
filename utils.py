import hashlib
import os
import re

def find_files(directory, regex):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if re.search(regex, basename):
                fq_path = os.path.join(root, basename)
                yield fq_path, root, basename

def _get_md5_hash(filename):
    BLOCKSIZE = 65536
    hasher = hashlib.md5()
    with open(filename, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()

def calculate_hash(filename):
    return _get_md5_hash(filename)