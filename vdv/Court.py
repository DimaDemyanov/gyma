from collections import OrderedDict

from sqlalchemy import Column, String, Integer, Boolean, Date, Sequence
from sqlalchemy.ext.declarative import declarative_base

import datetime
import time

from vdv.db import DBConnection

Base = declarative_base()

class Court(Base):
    __tablename__ = 'vdv_court'

    courtid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    name = Column(String)
    desc = Column(String)
    location = Column(Integer)
    private = Column(Boolean)
    created = Column(Date)
    updated = Column(Date)

    def to_dict(self):
        tmp_crt, tmp_upd = self.created, self.updated
        self.created, self.updated = str(self.created), str(self.update)
        res = OrderedDict([(key, self.__dict__[key]) for key in ['courtid', 'name', 'desc', 'location',
                                                                  'private', 'created', 'updated']])
        self.created, self.updated = tmp_crt, tmp_upd
        return res

    def __init__(self, name, desc, location, address, private):
        self.name = name
        self.desc = desc
        self.location = location
        self.address = address
        self.private = private
        ts = time.time()
        self.created = self.updated = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')

    def add(self):
        with DBConnection() as session:
            session.db.add(self)
            session.db.commit()
            return self.courtid

    @staticmethod
    def delete(id):
        with DBConnection() as session:
            res = session.db.query(Court).filter_by(courtid=id).all()

            if len(res) == 1:
                session.db.delete(res[0])
                session.db.commit()
            else:
                raise FileNotFoundError('courtid was not found')

    @staticmethod
    def get():
        with DBConnection() as session:
            return session.db.query(Court)