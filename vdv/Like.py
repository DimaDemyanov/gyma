from collections import OrderedDict

from sqlalchemy import Column, Date, Integer, Sequence
from sqlalchemy.ext.declarative import declarative_base

import datetime
import time

from vdv.db import DBConnection

Base = declarative_base()

class Like(Base):
    __tablename__ = 'vdv_like'

    likeid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    userid = Column(Integer)
    created = Column(Date)

    def __init__(self, userid):
        self.userid = userid

        ts = time.time()
        self.created = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')

    def add(self):
        with DBConnection() as session:
            session.db.add(self)
            session.db.commit()
            return self.locid

    def to_dict(self):
        tmp = self.created
        self.created = str(tmp)
        res = OrderedDict([(key, self.__dict__[key]) for key in ['likeid', 'userid', 'created']])
        self.created = tmp
        return res

    @classmethod
    def delete(cls, id):
        with DBConnection() as session:
            res = session.db.query(cls).filter_by(likeid=id).all()

            if len(res) == 1:
                session.db.delete(res[0])
                session.db.commit()
            else:
                raise FileNotFoundError('likeid was not found')

    @classmethod
    def get(cls):
        with DBConnection() as session:
            return session.db.query(cls)