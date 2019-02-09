from collections import OrderedDict
import datetime
import time

from sqlalchemy import Column, String, Integer, Date, Sequence, Boolean
from sqlalchemy.ext.declarative import declarative_base

from vdv.Entities.EntityBase import EntityBase

Base = declarative_base()

class EntityTime(EntityBase, Base):
    __tablename__ = 'vdv_time'

    vdvid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    time = Column(String)

    json_serialize_items_list = ['vdvid', 'courtid', 'time']

    def __init__(self, time):
        super().__init__()
        self.time = time

