import datetime
import time

from sqlalchemy import Column, Date, Integer, Sequence
from sqlalchemy.ext.declarative import declarative_base

from vdv.Entities.EntityBase import EntityBase

Base = declarative_base()

class EntityLike(EntityBase, Base):
    __tablename__ = 'vdv_like'

    vdvid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    userid = Column(Integer)
    created = Column(Date)

    json_serialize_items_list = ['vdvid', 'userid', 'created']

    def __init__(self, userid):
        super().__init__()

        self.userid = userid
        ts = time.time()
        self.created = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
