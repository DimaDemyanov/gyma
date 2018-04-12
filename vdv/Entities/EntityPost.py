import datetime
import time

from sqlalchemy import Column, String, Integer, Date, Sequence
from sqlalchemy.ext.declarative import declarative_base

from vdv.Entities.EntityBase import EntityBase

from vdv.db import DBConnection

Base = declarative_base()

class EntityPost(EntityBase, Base):
    __tablename__ = 'vdv_post'


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

    @classmethod
    def add_from_json(cls, data, userId):
        vdvid = None

        if 'description' in data:
            description = data['description']

            new_entity = EntityPost(userId, description)
            vdvid = new_entity.add()

        return vdvid
