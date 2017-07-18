from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey

Base = declarative_base()

class Document(Base):
    __tablename__ = 'document'

    id = Column(Integer, primary_key=True)
    filename = Column(String)
    filepath = Column(String)
    body = Column(String)
    hash = Column(String(100))
    
    def __str__(self):
        return "<Document id={}>".format(self.id, self.hash)