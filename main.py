import sys

from whoosh.index import open_dir
from whoosh.qparser import QueryParser

from index_builders import PDFIndexBuilder
from utils import find_files


def query_index():
    ix = open_dir("indexdir")
    while True:
        indata = input("Enter query: ")
        with ix.searcher() as searcher:
            query = QueryParser("content", ix.schema).parse(indata)
            results = searcher.search(query)
            
            for item in results[:10]:
                print(item['filename'])
                # print(item['path'])


# def test_find_files(root_dir):
#     for fq_path, root, basename in find_files(root_dir, '\.py$'):
#         print(fq_path)

def main():
    root_dir = sys.argv[1]
    builder = PDFIndexBuilder()
    builder.run(root_dir)
    query_index()

    # test_find_files(root_dir)
 
if __name__ == '__main__':
    main()
