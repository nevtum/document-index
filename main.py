import fnmatch
import hashlib
import os
import sys

from sqlalchemy import create_engine

from db.models import Base, Document
from extractors import TextExtractor
from whoosh.fields import *
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser


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

def calculate_hash(filename):
    return get_md5_hash(filename)
    
def populate_database(Session, Extractor):
    for filename in find_files(sys.argv[1], Extractor.extension_filter()):    
        dbsession = Session()
        try:
            hash = calculate_hash(filename)
            contents = Extractor.get_contents(filename)
            existing = dbsession.query(Document).filter_by(filepath=filename).first()
            if existing is None:
                doc = Document(filepath=filename, body=contents, hash=hash)
                dbsession.add(doc)
            
            elif existing.hash != hash:
                existing.hash = hash
                existing.body = contents
            
            dbsession.commit()
        except Exception:
            dbsession.rollback()
        finally:
            dbsession.close()

def build_index(Session):
    schema = Schema(path=ID(stored=True), content=NGRAM)
    
    if not os.path.exists("indexdir"):
        os.mkdir("indexdir")
    
    ix = create_in("indexdir", schema)
    writer = ix.writer()
    
    dbsession = Session()
    queryset = dbsession.query(Document)

    for item in queryset.all():
        writer.add_document(path=item.filepath, content=str(item.body))

    writer.commit()
    dbsession.close()

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
    engine = create_engine('sqlite:///data.sqlite', echo=True)
    Base.metadata.create_all(engine)
    
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    
    populate_database(Session, TextExtractor)
    build_index(Session)
    query_index()
 
if __name__ == '__main__':
    main()
