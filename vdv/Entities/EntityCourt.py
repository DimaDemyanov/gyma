import datetime
import time

from sqlalchemy import Column, String, Integer, Boolean, Date, Sequence
from sqlalchemy.ext.declarative import declarative_base

from vdv.Entities.EntityBase import EntityBase

Base = declarative_base()

class EntityCourt(EntityBase, Base):
    __tablename__ = 'vdv_court'

    vdvid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    name = Column(String)
    desc = Column(String)
    location = Column(Integer)
    private = Column(Boolean)
    created = Column(Date)
    updated = Column(Date)

    json_serialize_items_list = ['vdvid', 'name', 'desc', 'location', 'private', 'created', 'updated']

    def __init__(self, name, desc, location, address, private):
        super().__init__()

        self.name = name
        self.desc = desc
        self.location = location
        self.address = address
        self.private = private

        ts = time.time()
        self.created = self.updated = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
