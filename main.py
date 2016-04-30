import fnmatch
import os
import sys


def find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename

if __name__ == '__main__':
    for filename in find_files(sys.argv[1], '*.doc'):
        print("match %s" % filename)
