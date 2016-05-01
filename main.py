import fnmatch
import hashlib
import os
import sys

import sqlalchemy


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

def main():
    from db.models import Base, Document
    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///:memory:', echo=True)
    Base.metadata.create_all(engine)
    
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    
    for filename in find_files(sys.argv[1], sys.argv[2]):    
        dbsession = Session()
        try:
            hash = get_md5_hash(filename)
            doc = Document(filepath=filename, hash=hash)
            dbsession.add(doc)
            dbsession.commit()
        except Exception:
            dbsession.rollback()
        finally:
            dbsession.close()

if __name__ == '__main__':
    main()
