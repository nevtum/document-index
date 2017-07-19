import sys

from whoosh.index import open_dir
from whoosh.qparser import QueryParser

def main():
    root_dir = sys.argv[1]
    builder = PDFIndexBuilder()
    builder.run(root_dir)
 
if __name__ == '__main__':
    main()
