from collections import OrderedDict

from sqlalchemy import Column, String, Integer, Sequence
from sqlalchemy.ext.declarative import declarative_base

from vdv.db import DBConnection

Base = declarative_base()

class Prop(Base):
    __tablename__ = 'vdv_prop'

    propid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    name = Column(String)
    type = Column(String)

    def to_dict(self):
        res = OrderedDict([(key, self.__dict__[key]) for key in ['propid', 'name', 'type']])
        return res

    def __init__(self, name, type):
        self.name = name
        self.type = type

    def add(self):
        with DBConnection() as session:
            session.db.add(self)
            session.db.commit()
            return self.courtid

    @staticmethod
    def delete(id):
        with DBConnection() as session:
            res = session.db.query(Prop).filter_by(propid=id).all()

            if len(res) == 1:
                session.db.delete(res[0])
                session.db.commit()
            else:
                raise FileNotFoundError('propid was not found')

    @staticmethod
    def get():
        with DBConnection() as session:
            return session.db.query(Prop)

    @staticmethod
    def map_name_id():
        with DBConnection() as session:
            return {_.name: _.propid for _ in session.db.query(Prop).all()}

    @staticmethod
    def map_id_name():
        with DBConnection() as session:
            return {_.propid: _.name for _ in session.db.query(Prop).all()}
