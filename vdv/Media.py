from collections import OrderedDict

from sqlalchemy import Column, String, Integer, Date, Sequence
from sqlalchemy.ext.declarative import declarative_base

import datetime
import time

from vdv.db import DBConnection

Base = declarative_base()

class Media(Base):
    __tablename__ = 'vdv_media'

    mediaid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    ownerid = Column(Integer)
    type    = Column(String)
    url     = Column(Integer)
    created = Column(Date)

    def to_dict(self):
        tmp = self.created
        self.created = str(tmp)
        res = OrderedDict([(key, self.__dict__[key]) for key in ['mediaid', 'ownerid', 'type', 'url', 'created']])
        self.created = tmp
        return res

    def __init__(self, ownerid, type, url):
        self.ownerid = ownerid
        self.type = type
        self.url = url

        ts = time.time()
        self.created = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')

    def add(self):
        with DBConnection() as session:
            session.db.add(self)
            session.db.commit()
            return self.mediaid

    @staticmethod
    def delete(id):
        with DBConnection() as session:
            res = session.db.query(Media).filter_by(mediaid=id).all()

            if len(res) == 1:
                session.db.delete(res[0])
                session.db.commit()
            else:
                raise FileNotFoundError('mediaid was not found')

    @staticmethod
    def get():
        with DBConnection() as session:
            return session.db.query(Media)