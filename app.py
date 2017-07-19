import sys

from whoosh.index import open_dir
from whoosh.qparser import QueryParser


def query_index():
    ix = open_dir("indexdir")
    while True:
        indata = input("Enter query: ")
        with ix.searcher() as searcher:
            query = QueryParser("content", ix.schema).parse(indata)
            results = searcher.search(query)
            
            for item in results[:10]:
                # print(item.score, item['filename'])
                print(item.score, item['path'])

def main():
    query_index()
 
if __name__ == '__main__':
    main()
