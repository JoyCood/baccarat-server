from . import mongo

class Base(object):
    @classmethod
    def collection(cls):
        return getattr(cls, '_collection')

    @classmethod
    def insert_one(cls, doc, bypass_document_validation=False, session=None):
        collection = cls.collection()
        return mongo[collection].insert(doc, bypass_document_validation, session)

    @classmethod
    def find_one(cls, filter=None, *args, **kwargs):
        collection = cls.collection()
        return mongo[collection].find_one(filter, *args, **kwargs)

class Member(Base):
    _collection = 'member'

class CardLog(Base):
    _collection = 'card_log'


        
