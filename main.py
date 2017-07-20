import sys

from index_builders import PDFIndexBuilder


def main():
    root_dir = sys.argv[1]
    builder = PDFIndexBuilder()
    builder.run(root_dir)
 
if __name__ == '__main__':
    main()
