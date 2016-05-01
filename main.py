import fnmatch
import hashlib
import os
import sys

from sqlalchemy import create_engine

from db.models import Base, Document
from extractors import TextExtractor


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
            
            dbsession.commit()
        except Exception:
            dbsession.rollback()
        finally:
            dbsession.close()

def query_database(Session):
    while True:
        indata = input("Enter query: ")
        
        dbsession = Session()
        queryset = dbsession.query(Document).filter(Document.filepath.contains(indata))
        
        for item in queryset.all():
            print(item)
        
        print("{} items found".format(queryset.count()))
        
        dbsession.close()

def main():
    engine = create_engine('sqlite:///data.sqlite', echo=True)
    Base.metadata.create_all(engine)
    
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    
    populate_database(Session, TextExtractor)
    query_database(Session)
 
if __name__ == '__main__':
    main()
