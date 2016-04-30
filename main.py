import fnmatch
import os
import sys
import hashlib


def find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename

def get_md5_hash(filename):
    BLOCKSIZE = 65536
    hasher = hashlib.md5()
    with open(filename, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()

def process(filename):
    try:
        print("match %s" % filename)
        print("hash %s" % get_md5_hash(filename))
    except Exception:
        pass

if __name__ == '__main__':
    for filename in find_files(sys.argv[1], sys.argv[2]):
        process(filename)
