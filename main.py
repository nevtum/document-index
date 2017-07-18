import sys

from whoosh.fields import *
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from index_builder import IndexBuilder

class DocIndexBuilder(IndexBuilder):
    extension_list = "*.doc"
    index_directory = 'indexdir'

    def get_contents(self, filename):
        return super(DocIndexBuilder, self).get_contents(filename)

def query_index():
    ix = open_dir("indexdir")
    while True:
        indata = input("Enter query: ")
        with ix.searcher() as searcher:
            query = QueryParser("content", ix.schema).parse(indata)
            results = searcher.search(query)
            
            for item in results[:10]:
                print(item['path'])

def main():
    root_dir = sys.argv[1]
    builder = DocIndexBuilder()
    builder.run(root_dir)
    query_index()
 
if __name__ == '__main__':
    main()
