from collections import OrderedDict

from sqlalchemy import Column, String, Integer, Float, Sequence
from sqlalchemy.ext.declarative import declarative_base

from vdv.db import DBConnection

Base = declarative_base()

class Location(Base):
    __tablename__ = 'vdv_location'

    locid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)

    def __init__(self, name, latitude, longitude):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude

    def add(self):
        with DBConnection() as session:
            session.db.add(self)
            session.db.commit()
            return self.locid

    def to_dict(self):
        return OrderedDict([(key, self.__dict__[key]) for key in ['locid', 'name', 'latitude', 'longitude']])

    @staticmethod
    def delete(id):
        with DBConnection() as session:
            res = session.db.query(Location).filter_by(locid=id).all()

            if len(res) == 1:
                session.db.delete(res[0])
                session.db.commit()
            else:
                raise FileNotFoundError('location was not found')

    @staticmethod
    def get():
        with DBConnection() as session:
            return session.db.query(Location)