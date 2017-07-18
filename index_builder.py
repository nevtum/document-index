import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from whoosh.fields import *
from whoosh.index import create_in
from whoosh.qparser import QueryParser

from db.models import Base, Document
from utils import find_files, calculate_hash

class IndexBuilder(object):
    def run(self, filepath):
        if not self.index_directory:
            raise Exception("Imppoperyly configured 'index_directory'")
        
        if not self.extension_list:
            raise Exception("Improperly configured 'extension_list'")

        engine = create_engine('sqlite:///data.sqlite', echo=True)
        Base.metadata.create_all(engine)
        
        Session = sessionmaker(bind=engine)
        self._populate_database(Session, filepath)
        self._build_index(Session)
        self._create_regex()
    
    def get_contents(self, filename):
        with open(filename, 'rb') as stream:
            return stream.read()
    
    def _create_regex(self):
        regex = map(lambda s: "\.{}$".format(s), self.extension_list)
        regex = "|".join([r for r in regex])
        regex = "({})".format(regex)
        return regex
    
    def _populate_database(self, Session, filepath):
        for filename in find_files(filepath, self._create_regex()):    
            dbsession = Session()
            try:
                hash = calculate_hash(filename)
                contents = self.get_contents(filename)
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
    
    def _build_index(self, Session):
        schema = Schema(path=ID(stored=True), content=NGRAM)
        
        if not os.path.exists(self.index_directory):
            os.mkdir(self.index_directory)
        
        ix = create_in(self.index_directory, schema)
        writer = ix.writer()
        
        dbsession = Session()
        queryset = dbsession.query(Document)

        for item in queryset.all():
            writer.add_document(path=item.filepath, content=str(item.body))

        writer.commit()
        dbsession.close()
