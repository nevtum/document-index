import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from whoosh import fields
from whoosh.index import create_in
from whoosh.qparser import QueryParser

from db.models import Base, Document
from utils import find_files, calculate_hash

class BaseIndexBuilder(object):
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
    
    def get_contents(self, filename):
        with open(filename, 'rb') as stream:
            return stream.read()
    
    def _create_regex(self):
        regex = map(lambda s: "\.{}$".format(s), self.extension_list)
        regex = "|".join([r for r in regex])
        regex = "({})".format(regex)
        return regex
    
    def _populate_database(self, Session, filepath):
        for fq_path, root, basename in find_files(filepath, self._create_regex()):    
            dbsession = Session()
            try:
                hash = calculate_hash(fq_path)
                contents = self.get_contents(fq_path)
                existing = dbsession.query(Document).filter_by(filepath=fq_path).first()
                if existing is None:
                    doc = Document(
                        filename=basename,
                        filepath=fq_path,
                        body=contents,
                        hash=hash
                    )
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
        schema = fields.Schema(
            path=fields.ID(stored=True),
            filename=fields.STORED,
            content=fields.NGRAM
        )
        
        if not os.path.exists(self.index_directory):
            os.mkdir(self.index_directory)
        
        ix = create_in(self.index_directory, schema)
        writer = ix.writer()
        
        dbsession = Session()
        queryset = dbsession.query(Document)

        for item in queryset.all():
            writer.add_document(
                path=item.filepath,
                filename=item.filename,
                content=str(item.body)
            )

        writer.commit()
        dbsession.close()

from textract import process

class DocIndexBuilder(BaseIndexBuilder):
    extension_list = ('doc', 'docx')
    index_directory = 'indexdir'

    def get_contents(self, filename):
        text = process(filename)
        return text

class PDFIndexBuilder(BaseIndexBuilder):
    extension_list = ('pdf',)
    index_directory = 'indexdir'

    def get_contents(self, filename):
        text = process(filename)
        return text
