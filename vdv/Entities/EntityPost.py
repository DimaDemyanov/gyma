import datetime
import time

from sqlalchemy import Column, String, Integer, Date, Sequence
from sqlalchemy.ext.declarative import declarative_base

from vdv.Entities.EntityBase import EntityBase

Base = declarative_base()

class EntityPost(EntityBase, Base):
    __tablename__ = 'vdv_court'


    vdvid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    userid = Column(Integer)
    description = Column(String)
    created = Column(Date)
    updated = Column(Date)

    json_serialize_items_list = ['vdvid', 'userid', 'description', 'created', 'updated']

    def __init__(self, userid, description):
        super().__init__()

        self.userid = userid
        self.description = description

        ts = time.time()
        self.created = self.updated = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
